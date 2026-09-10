"""
Runs PCAP decoding/analysis and CSV analysis, can do batches of test runs.
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
    parser = argparse.ArgumentParser(
        description="Unified V2X Latency Analysis runner for PCAP and CSV files."
    )

    # --- Shared Arguments ---
    run_selection = parser.add_mutually_exclusive_group(required=True)
    run_selection.add_argument(
        "-r",
        "--run-dir",
        type=Path,
        help="Directory for one analysis run.",
    )
    run_selection.add_argument(
        "-b",
        "--batch-dir",
        type=Path,
        help="Directory containing multiple run directories.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help=(
            "Directory containing input files. For a single run, it defaults "
            "to --run-dir. For a batch, each run uses the same-named "
            "subdirectory inside --input-dir."
        ),
    )
    parser.add_argument(
        "--max-latency-ms",
        type=float,
        default=200.0,
        help="Maximum displayed latency value (ms) in histogram/CDF plots.",
    )
    parser.add_argument(
        "--rolling-window",
        type=int,
        default=20,
        help="Number of samples in rolling latency mean plot.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging.",
    )

    # --- Toggles ---
    toggles = parser.add_argument_group("Analysis Toggles")
    toggles.add_argument(
        "--no-pcap",
        action="store_true",
        help="Skip running PCAP analysis.",
    )
    toggles.add_argument(
        "--no-csv",
        action="store_true",
        help="Skip running CSV analysis.",
    )

    # --- PCAP-Specific Options ---
    pcap_group = parser.add_argument_group("PCAP Options")
    pcap_group.add_argument(
        "--force-decode",
        action="store_true",
        help="Force re-decoding of PCAP files.",
    )
    pcap_group.add_argument(
        "--name",
        action="append",
        default=[],
        metavar="DIRECTION=FOLDER_NAME",
        help=(
            "Customize result directory names (e.g., --name dut_1_to_proxy_1=side_1)."
        ),
    )

    for role in analysis_pcap.PCAP_ROLES:
        pcap_group.add_argument(
            analysis_pcap.cli_option_name(role),
            dest=role,
            type=Path,
            default=None,
            help=f"Explicit path for {role}.",
        )

    return parser.parse_args()


def discover_batch_runs(batch_dir: Path) -> list[Path]:
    """Find sub-directories for individual runs."""
    if not batch_dir.is_dir():
        raise FileNotFoundError(f"Batch directory does not exist: {batch_dir}")

    ignored_names = {
        "decoded",
        "results",
        "__pycache__",
    }
    run_dirs = sorted(
        (
            path.resolve()
            for path in batch_dir.iterdir()
            if path.is_dir()
            and path.name not in ignored_names
            and not path.name.startswith(".")
        ),
        key=lambda path: path.name.lower(),
    )

    if not run_dirs:
        raise FileNotFoundError(
            f"No run directories found inside batch directory: {batch_dir}"
        )

    return run_dirs


def get_run_directories(args: argparse.Namespace) -> list[Path]:
    """Return either the selected run or all runs found in a batch."""
    if args.run_dir is not None:
        run_dir = args.run_dir.expanduser().resolve()
        if not run_dir.is_dir():
            raise FileNotFoundError(f"Run directory does not exist: {run_dir}")
        return [run_dir]

    batch_dir = args.batch_dir.expanduser().resolve()
    return discover_batch_runs(batch_dir)


def get_run_input_dir(
    args: argparse.Namespace,
    run_dir: Path,
) -> Path:
    """Select the input directory for one run."""
    if args.input_dir is None:
        return run_dir

    input_root = args.input_dir.expanduser().resolve()

    if args.batch_dir is None:
        return input_root

    run_input_dir = input_root / run_dir.name
    if not run_input_dir.is_dir():
        raise FileNotFoundError(
            f"Input directory for run {run_dir.name!r} does not exist: {run_input_dir}"
        )

    return run_input_dir.resolve()


def make_run_arguments(
    args: argparse.Namespace,
    run_dir: Path,
) -> argparse.Namespace:
    """Make arguments for one analysis run."""
    run_values = vars(args).copy()
    run_values["run_dir"] = run_dir
    run_values["input_dir"] = get_run_input_dir(args, run_dir)
    run_values["batch_dir"] = None
    return argparse.Namespace(**run_values)


def normalize_threshold_result(value: Any) -> str:
    """Normalize a threshold result read from a generated summary CSV."""
    if value is None or pd.isna(value):
        return "NOT_CONFIGURED"

    result = str(value).strip().upper()
    return result or "NOT_CONFIGURED"


def read_run_summary_files(run_dir: Path) -> pd.DataFrame:
    """Read all generated test summary CSV files for one run."""
    results_dir = run_dir / "results"
    if not results_dir.is_dir():
        logging.warning(
            "No results directory found for run %s",
            run_dir.name,
        )
        return pd.DataFrame()

    summary_files = sorted(
        (path for path in results_dir.rglob("results_summary.csv") if path.is_file()),
        key=lambda path: str(path).lower(),
    )

    if not summary_files:
        logging.warning(
            "No results_summary.csv files found for run %s",
            run_dir.name,
        )
        return pd.DataFrame()

    summary_frames: list[pd.DataFrame] = []

    for summary_file in summary_files:
        try:
            summary_df = pd.read_csv(summary_file)
        except (
            OSError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            UnicodeDecodeError,
        ) as error:
            logging.error(
                "Failed to read summary file %s: %s",
                summary_file,
                error,
            )
            continue

        if summary_df.empty:
            logging.warning(
                "Summary file is empty: %s",
                summary_file,
            )
            continue

        relative_file = summary_file.relative_to(run_dir)
        test_name = summary_file.parent.name

        # Assign instead of inserting because these columns may already exist.
        summary_df["run_name"] = run_dir.name
        summary_df["test_name"] = test_name
        summary_df["summary_file"] = str(relative_file)

        # Move the metadata columns to the beginning of the DataFrame.
        metadata_columns = [
            "run_name",
            "test_name",
            "summary_file",
        ]
        remaining_columns = [
            column for column in summary_df.columns if column not in metadata_columns
        ]
        summary_df = summary_df[metadata_columns + remaining_columns]

        summary_frames.append(summary_df)

    if not summary_frames:
        return pd.DataFrame()

    return pd.concat(
        summary_frames,
        ignore_index=True,
        sort=False,
    )


def add_run_result(
    summary_df: pd.DataFrame,
    analysis_status: int,
) -> pd.DataFrame:
    """
    Add a run result that fails when an analysis errored or any individual
    threshold test failed.
    """
    result_df = summary_df.copy()

    if "threshold_result" in result_df.columns:
        threshold_results = result_df["threshold_result"].map(
            normalize_threshold_result
        )
        result_df["threshold_result"] = threshold_results
        threshold_failed = threshold_results.isin(FAILURE_RESULTS).any()
    else:
        threshold_failed = False

    if analysis_status != 0:
        run_result = "FAIL"
        failure_reason = "ANALYSIS_ERROR"
    elif threshold_failed:
        run_result = "FAIL"
        failure_reason = "THRESHOLD_FAILURE"
    elif result_df.empty:
        run_result = "NO_RESULTS"
        failure_reason = "NO_RESULTS"
    else:
        run_result = "PASS"
        failure_reason = ""

    result_df["run_result"] = run_result
    result_df["run_failed"] = run_result == "FAIL"
    result_df["failure_reason"] = failure_reason
    result_df["analysis_status"] = analysis_status

    return result_df


def write_run_total_summary(
    run_dir: Path,
    analysis_status: int,
) -> pd.DataFrame:
    """Create the total data summary CSV for one run."""
    summary_df = read_run_summary_files(run_dir)
    summary_df = add_run_result(
        summary_df,
        analysis_status,
    )

    results_dir = run_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_file = results_dir / TOTAL_SUMMARY_FILENAME

    if summary_df.empty:
        run_result = "FAIL" if analysis_status != 0 else "NO_RESULTS"
        failure_reason = "ANALYSIS_ERROR" if analysis_status != 0 else "NO_RESULTS"
        summary_df = pd.DataFrame(
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

    summary_df.to_csv(output_file, index=False)
    logging.info(
        "Run total summary written to: %s",
        output_file,
    )

    return summary_df


def write_batch_total_summary(
    batch_dir: Path,
    run_summaries: list[pd.DataFrame],
) -> Path:
    """Combine all run summaries into one batch-level summary CSV."""
    output_file = batch_dir / TOTAL_SUMMARY_FILENAME

    if run_summaries:
        batch_summary = pd.concat(
            run_summaries,
            ignore_index=True,
            sort=False,
        )
    else:
        batch_summary = pd.DataFrame(
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

    batch_summary.to_csv(output_file, index=False)
    logging.info(
        "Batch total summary written to: %s",
        output_file,
    )

    return output_file.resolve()


def analyze_single_run(
    args: argparse.Namespace,
    run_dir: Path,
) -> int:
    """Run the analysis for one run directory."""
    try:
        run_args = make_run_arguments(args, run_dir)
    except Exception as error:
        logging.error(
            "Unable to prepare run %s: %s",
            run_dir.name,
            error,
        )
        return 1

    logging.info(
        "================ Processing Run: %s ================",
        run_dir.name,
    )
    logging.info("Run directory: %s", run_dir)
    logging.info("Input directory: %s", run_args.input_dir)

    results: list[int] = []

    if not args.no_pcap:
        logging.info("================ Running PCAP Analysis ================")
        try:
            pcap_status = analysis_pcap.run_pcap_analysis(run_args)
        except Exception:
            logging.exception(
                "Unhandled PCAP analysis error for run %s",
                run_dir.name,
            )
            pcap_status = 1

        results.append(pcap_status)

    if not args.no_csv:
        logging.info("================ Running CSV Analysis ================")
        try:
            csv_status = analysis_csv.run_csv_analysis(run_args)
        except Exception:
            logging.exception(
                "Unhandled CSV analysis error for run %s",
                run_dir.name,
            )
            csv_status = 1

        results.append(csv_status)

    return max(results) if results else 0


def main() -> int:
    args = parse_arguments()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    run_pcap = not args.no_pcap
    run_csv = not args.no_csv

    if not run_pcap and not run_csv:
        logging.warning("Both PCAP and CSV analysis were disabled. Exiting.")
        return 0

    try:
        run_dirs = get_run_directories(args)
    except Exception as error:
        logging.error("Unable to select analysis runs: %s", error)
        return 1

    statuses: list[int] = []
    run_summaries: list[pd.DataFrame] = []

    for run_dir in run_dirs:
        run_status = analyze_single_run(
            args,
            run_dir,
        )
        statuses.append(run_status)

        try:
            run_summary = write_run_total_summary(
                run_dir,
                run_status,
            )
            run_summaries.append(run_summary)
        except Exception:
            logging.exception(
                "Failed to create total summary for run %s",
                run_dir.name,
            )
            statuses.append(1)

    if args.batch_dir is not None:
        batch_dir = args.batch_dir.expanduser().resolve()
        try:
            batch_summary_file = write_batch_total_summary(
                batch_dir,
                run_summaries,
            )
            print(
                "[✓] Batch analysis complete. "
                f"Total summary saved to: {batch_summary_file}"
            )
        except Exception:
            logging.exception("Failed to create the batch total summary")
            statuses.append(1)
    elif run_dirs:
        summary_file = run_dirs[0] / "results" / TOTAL_SUMMARY_FILENAME
        print(f"[✓] Analysis complete. Total summary saved to: {summary_file}")

    failed_runs = 0
    for run_summary in run_summaries:
        if (
            "run_failed" in run_summary.columns
            and run_summary["run_failed"].fillna(False).any()
        ):
            failed_runs += 1

    if failed_runs:
        logging.warning(
            "%d of %d run(s) failed at least one threshold.",
            failed_runs,
            len(run_dirs),
        )

    return max(statuses) if statuses else 0


if __name__ == "__main__":
    sys.exit(main())
