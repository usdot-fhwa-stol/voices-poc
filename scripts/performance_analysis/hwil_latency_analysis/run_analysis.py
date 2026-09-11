"""
Run CSV and PCAP latency analysis for every run under a parent folder.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import analysis_csv
import analysis_pcap
import pandas as pd

TOTAL_SUMMARY_FILENAME = "total_data_summary.csv"
FAILURE_RESULTS = {"FAIL", "ERROR"}


def parse_arguments() -> argparse.Namespace:
    """Read the command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Run V2X PCAP and CSV latency analysis for every run under an "
            "input directory."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help=(
            "Parent directory containing the run directories. Results are "
            "written to a results directory beside this parent directory."
        ),
    )
    return parser.parse_args()


def discover_runs(input_dir: Path) -> tuple[list[Path], Path]:
    """Find all run directories directly inside the input directory."""
    input_dir = input_dir.expanduser().resolve()

    if not input_dir.is_dir():
        raise FileNotFoundError(
            f"Input directory does not exist: {input_dir}"
        )

    ignored_names = {
        "decoded",
        "__pycache__",
    }

    run_directories = sorted(
        (
            path.resolve()
            for path in input_dir.iterdir()
            if path.is_dir()
            and path.name not in ignored_names
            and not path.name.startswith(".")
        ),
        key=lambda path: path.name.lower(),
    )

    if not run_directories:
        raise FileNotFoundError(
            f"No run directories found inside {input_dir}"
        )

    results_root = (input_dir.parent / "results").resolve()
    return run_directories, results_root


def normalize_threshold_result(value: Any) -> str:
    """Convert a threshold result to a consistent uppercase value."""
    if value is None or pd.isna(value):
        return "NOT_CONFIGURED"

    normalized = str(value).strip().upper()
    return normalized or "NOT_CONFIGURED"


def read_run_summary_files(results_dir: Path) -> pd.DataFrame:
    """Read all generated result summaries for a run."""
    if not results_dir.is_dir():
        return pd.DataFrame()

    summary_files = sorted(
        (
            path
            for path in results_dir.rglob("results_summary.csv")
            if path.is_file()
        ),
        key=lambda path: str(path).lower(),
    )

    summary_frames: list[pd.DataFrame] = []

    for summary_file in summary_files:
        try:
            summary = pd.read_csv(summary_file)
        except (
            OSError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            UnicodeDecodeError,
        ) as error:
            logging.error(
                "Failed to read summary %s: %s",
                summary_file,
                error,
            )
            continue

        if summary.empty:
            logging.warning("Summary file is empty: %s", summary_file)
            continue

        relative_file = summary_file.relative_to(results_dir)
        relative_parent = summary_file.parent.relative_to(results_dir)

        # This keeps enough context to show where each result came from.
        summary["run_name"] = results_dir.name
        summary["test_name"] = str(relative_parent)
        summary["summary_file"] = str(relative_file)

        metadata_columns = [
            "run_name",
            "test_name",
            "summary_file",
        ]
        remaining_columns = [
            column
            for column in summary.columns
            if column not in metadata_columns
        ]

        summary_frames.append(
            summary[metadata_columns + remaining_columns]
        )

    if not summary_frames:
        return pd.DataFrame()

    return pd.concat(
        summary_frames,
        ignore_index=True,
        sort=False,
    )


def add_run_result(
    summary: pd.DataFrame,
    analysis_status: int,
) -> pd.DataFrame:
    """Add the overall run result to every summary row."""
    result = summary.copy()

    if "threshold_result" in result.columns:
        normalized_results = result["threshold_result"].map(
            normalize_threshold_result
        )
        result["threshold_result"] = normalized_results
        threshold_failed = normalized_results.isin(
            FAILURE_RESULTS
        ).any()
    else:
        threshold_failed = False

    if analysis_status != 0:
        run_result = "FAIL"
        failure_reason = "ANALYSIS_ERROR"
    elif threshold_failed:
        run_result = "FAIL"
        failure_reason = "THRESHOLD_FAILURE"
    elif result.empty:
        run_result = "NO_RESULTS"
        failure_reason = "NO_RESULTS"
    else:
        run_result = "PASS"
        failure_reason = ""

    result["run_result"] = run_result
    result["run_failed"] = run_result == "FAIL"
    result["failure_reason"] = failure_reason
    result["analysis_status"] = analysis_status

    return result


def write_run_summary(
    run_dir: Path,
    results_dir: Path,
    analysis_status: int,
) -> pd.DataFrame:
    """Write the combined summary for one run."""
    summary = read_run_summary_files(results_dir)
    summary = add_run_result(summary, analysis_status)

    if summary.empty:
        run_result = "FAIL" if analysis_status != 0 else "NO_RESULTS"
        failure_reason = (
            "ANALYSIS_ERROR"
            if analysis_status != 0
            else "NO_RESULTS"
        )

        summary = pd.DataFrame(
            [
                {
                    "run_name": run_dir.name,
                    "test_name": "",
                    "summary_file": "",
                    "threshold_result": "",
                    "run_result": run_result,
                    "run_failed": run_result == "FAIL",
                    "failure_reason": failure_reason,
                    "analysis_status": analysis_status,
                }
            ]
        )

    results_dir.mkdir(parents=True, exist_ok=True)
    output_file = results_dir / TOTAL_SUMMARY_FILENAME
    summary.to_csv(output_file, index=False)

    logging.info("Run summary written to %s", output_file)
    return summary


def write_total_summary(
    results_root: Path,
    run_summaries: list[pd.DataFrame],
) -> Path:
    """Combine all run summaries into one final summary."""
    if run_summaries:
        total_summary = pd.concat(
            run_summaries,
            ignore_index=True,
            sort=False,
        )
    else:
        total_summary = pd.DataFrame(
            columns=[
                "run_name",
                "test_name",
                "summary_file",
                "threshold_result",
                "run_result",
                "run_failed",
                "failure_reason",
                "analysis_status",
            ]
        )

    results_root.mkdir(parents=True, exist_ok=True)
    output_file = results_root / TOTAL_SUMMARY_FILENAME
    total_summary.to_csv(output_file, index=False)

    logging.info("Total summary written to %s", output_file)
    return output_file.resolve()


def analyze_run(
    input_dir: Path,
    results_dir: Path,
) -> int:
    """Run the PCAP and CSV analysis for one run."""
    logging.info("============================================================")
    logging.info("Processing run: %s", input_dir.name)
    logging.info("Input: %s", input_dir)
    logging.info("Output: %s", results_dir)

    results_dir.mkdir(parents=True, exist_ok=True)
    statuses: list[int] = []

    try:
        status = analysis_pcap.run_pcap_analysis(
            input_dir=input_dir,
            results_dir=results_dir,
        )
        statuses.append(status)
    except Exception:
        logging.exception(
            "Unhandled PCAP analysis error for %s",
            input_dir.name,
        )
        statuses.append(1)

    try:
        status = analysis_csv.run_csv_analysis(
            input_dir=input_dir,
            results_dir=results_dir,
        )
        statuses.append(status)
    except Exception:
        logging.exception(
            "Unhandled CSV analysis error for %s",
            input_dir.name,
        )
        statuses.append(1)

    return max(statuses, default=0)


def main() -> int:
    """Analyze every run found under the input directory."""
    args = parse_arguments()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    try:
        run_directories, results_root = discover_runs(args.input_dir)
    except (FileNotFoundError, OSError) as error:
        logging.error("Unable to find input runs: %s", error)
        return 1

    statuses: list[int] = []
    run_summaries: list[pd.DataFrame] = []

    for run_dir in run_directories:
        run_results_dir = results_root / run_dir.name

        run_status = analyze_run(
            input_dir=run_dir,
            results_dir=run_results_dir,
        )
        statuses.append(run_status)

        try:
            run_summary = write_run_summary(
                run_dir=run_dir,
                results_dir=run_results_dir,
                analysis_status=run_status,
            )
            run_summaries.append(run_summary)
        except Exception:
            logging.exception(
                "Failed to write summary for %s",
                run_dir.name,
            )
            statuses.append(1)

    try:
        summary_file = write_total_summary(
            results_root=results_root,
            run_summaries=run_summaries,
        )
        print(
            "[✓] Analysis complete. "
            f"Summary saved to: {summary_file}"
        )
    except Exception:
        logging.exception("Failed to write the total summary")
        statuses.append(1)

    failed_runs = sum(
        1
        for summary in run_summaries
        if "run_failed" in summary.columns
        and summary["run_failed"].fillna(False).astype(bool).any()
    )

    if failed_runs:
        logging.warning(
            "%d of %d run(s) failed.",
            failed_runs,
            len(run_directories),
        )

    return max(statuses, default=0)


if __name__ == "__main__":
    sys.exit(main())