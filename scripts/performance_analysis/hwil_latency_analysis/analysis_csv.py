"""Run-level Latency Analysis for Radio & SecureV2XMessage CSVs."""

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from radio_latency_plotting import (
    calculate_statistics,
    plot_latency_cdf,
    plot_latency_histogram,
    plot_latency_timeseries,
)

LATENCY_THRESHOLD_MS = 10.0


# "patterns" = what the filename looks like.
# "id_cols" = columns that help us match up rows.
# "skip_events" = rows we want to throw away and not use.
DATA_TYPES: dict[str, dict[str, Any]] = {
    "Radio": {
        "patterns": ["*Entities-Radio*.csv", "*Radio*.csv"],
        "id_cols": ["const^identifier,String", "Metadata,StateVersion"],
        "skip_events": {"Discovery", "Destruction"},
    },
    "SecureV2XMessage": {
        "patterns": [
            "*TV2XMsg-SecureV2XMsg*.csv",
            "*SecureV2XMsg*.csv",
            "*SecureV2X*.csv",
        ],
        "id_cols": [
            "Metadata,MessageCount",
            "senderIdentifier,String",
            "uuid,String",
        ],
        "skip_events": set(),
    },
}


@dataclass(frozen=True, slots=True)
class LogRecord:
    tx_time_ms: float
    rx_time_ms: float
    latency_ms: float
    match_key: str
    row_id: str
    ip_address: str


def clean_value(value: Any) -> str:
    """Turn an empty/missing value into "", and everything else into plain text."""
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def normalize_timestamp_ms(value: Any) -> float:
    """
    Makes sure timestamp values are in milliseconds.
    """
    numeric = float(value)
    if not np.isfinite(numeric):
        raise ValueError("Timestamp is not finite")

    magnitude = abs(numeric)
    if magnitude >= 1e17:
        return numeric / 1e6
    if magnitude >= 1e14:
        return numeric / 1e3
    if 1e8 <= magnitude < 1e11:
        return numeric * 1e3

    return numeric


def extract_host(value: Any) -> str:
    """Pull just the address part out of something like 'http://1.2.3.4:8080' -> '1.2.3.4'."""
    endpoint = clean_value(value)
    if not endpoint:
        return ""

    # Remove any "http://" or similar bit at the front.
    endpoint = re.sub(
        r"^[A-Za-z][A-Za-z0-9+.-]*://",
        "",
        endpoint,
    )

    # Remove brackets
    if endpoint.startswith("["):
        closing_bracket = endpoint.find("]")
        if closing_bracket != -1:
            return endpoint[1:closing_bracket]

    # Remove port
    if endpoint.count(":") == 1:
        return endpoint.rsplit(":", maxsplit=1)[0]

    return endpoint


def find_csv_file(
    directory: Path,
    patterns: Iterable[str],
) -> Path | None:
    """Look inside a folder (and its subfolders) for a file matching one of the given name patterns."""
    if not directory.is_dir():
        return None

    for pattern in patterns:
        matches = list(directory.rglob(pattern))
        if matches:
            return sorted(matches)[0]

    return None


def read_records(
    csv_file: Path,
    msg_type: str,
) -> list[LogRecord]:
    """Open a CSV file and turn each usable row into a LogRecord."""
    cfg = DATA_TYPES[msg_type]

    # Try to open the file. If it's broken or unreadable, give up and return nothing.
    try:
        df = pd.read_csv(csv_file, dtype=str, low_memory=False)
    except (
        OSError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ) as error:
        logging.error("Failed to read %s: %s", csv_file, error)
        return []

    # Figure out which column tells us "when it was sent".
    tx_col = next(
        (
            column
            for column in (
                "Metadata,TimeOfTransmission",
                "Metadata,TimeOfCommit",
                "const^Metadata,TimeOfCreation",
            )
            if column in df.columns
        ),
        None,
    )
    # Figure out which column tells us "when it arrived".
    rx_col = next(
        (
            column
            for column in (
                "Metadata,TimeOfReceipt",
                "packetTimestamp",
            )
            if column in df.columns
        ),
        None,
    )

    # If we can't find both times, skip this file.
    if tx_col is None or rx_col is None:
        logging.warning("Missing timing columns in %s", csv_file)
        return []

    # Throw away rows that are the "skip" kind of event (like Discovery/Destruction), if any.
    event_col = "Metadata,Enum,Middleware::EventType"
    skip_events = cfg["skip_events"]
    if event_col in df.columns and skip_events:
        df = df.loc[~df[event_col].isin(skip_events)]

    # Figure out which column (if any) holds the sender's IP address.
    ip_col = next(
        (
            column
            for column in (
                "const^Metadata,SDOid.hostIPaddress",
                "Metadata,Endpoint",
                "const^Metadata,Endpoint",
            )
            if column in df.columns
        ),
        None,
    )

    # Only keep the ID columns that actually exist in this file.
    available_id_cols = [column for column in cfg["id_cols"] if column in df.columns]

    records: list[LogRecord] = []
    for row_index, row in df.iterrows():
        # Try to read and fix up the two timestamps for this row.
        try:
            tx_ms = normalize_timestamp_ms(row[tx_col])
            rx_ms = normalize_timestamp_ms(row[rx_col])
        except (TypeError, ValueError, OverflowError):
            continue

        # Build a "key" out of the ID columns so we can match rows to each other later.
        key_parts = []
        for column in available_id_cols:
            value = clean_value(row.get(column))
            if value:
                key_parts.append(value)

        row_id = clean_value(row.get("rowID")) or str(row_index)

        match_key = (
            f"{msg_type}::{'::'.join(key_parts)}"
            if key_parts
            else f"{msg_type}::row::{row_id}"
        )
        ip_address = extract_host(row.get(ip_col)) if ip_col else ""

        records.append(
            LogRecord(
                tx_time_ms=tx_ms,
                rx_time_ms=rx_ms,
                latency_ms=rx_ms - tx_ms,
                match_key=match_key,
                row_id=row_id,
                ip_address=ip_address,
            )
        )

    # Put the records in time order, earliest first.
    return sorted(
        records,
        key=lambda record: (
            record.tx_time_ms,
            record.rx_time_ms,
        ),
    )


def process_csv(records: list[LogRecord]) -> pd.DataFrame:
    """
    Turn our list of LogRecords into a dataframe.
    """
    rows = [
        {
            "Tx Timestamp (ms)": record.tx_time_ms,
            "Rx Timestamp (ms)": record.rx_time_ms,
            "Latency (ms)": record.latency_ms,
            "Match Key": record.match_key,
            "Row ID": record.row_id,
            "IP Address": record.ip_address,
            "Datetime": pd.to_datetime(
                record.tx_time_ms,
                unit="ms",
                utc=True,
                errors="coerce",
            ),
        }
        for record in records
        if (np.isfinite(record.latency_ms) and record.latency_ms >= 0)
    ]
    return pd.DataFrame(rows)


def add_threshold_summary(
    summary: dict[str, Any],
    df: pd.DataFrame,
) -> dict[str, Any]:
    """Add latency threshold counts, percentage, and result to a summary."""
    latencies = pd.to_numeric(
        df["Latency (ms)"],
        errors="coerce",
    ).dropna()

    total_samples = len(latencies)
    passed_samples = int((latencies < LATENCY_THRESHOLD_MS).sum())
    failed_samples = total_samples - passed_samples
    pass_percent = passed_samples / total_samples * 100.0 if total_samples else 0.0

    summary.update(
        {
            "latency_threshold_ms": LATENCY_THRESHOLD_MS,
            "threshold_total_samples": total_samples,
            "threshold_passed_samples": passed_samples,
            "threshold_failed_samples": failed_samples,
            "threshold_pass_percent": round(pass_percent, 2),
            "threshold_result": (
                "PASS" if total_samples > 0 and failed_samples == 0 else "FAIL"
            ),
        }
    )

    return summary


def save_analysis(
    df: pd.DataFrame,
    *,
    message_type: str,
    run_name: str,
    results_dir: Path,
    max_latency_ms: float,
    rolling_window: int,
) -> tuple[dict[str, Any], Path]:
    """Save the table to a CSV file, create plots and data summary."""
    output_dir = results_dir / message_type
    output_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        output_dir / "latency_results.csv",
        index=False,
    )

    plot_latency_histogram(
        df,
        output_dir,
        max_latency_ms,
    )
    plot_latency_cdf(
        df,
        output_dir,
        max_latency_ms,
    )
    plot_latency_timeseries(
        df,
        output_dir,
        rolling_window,
    )

    summary = calculate_statistics(
        df,
        message_type=message_type,
        run_name=run_name,
    )
    summary = add_threshold_summary(summary, df)

    pd.DataFrame([summary]).to_csv(
        output_dir / "results_summary.csv",
        index=False,
    )

    logging.info(
        "Threshold result for %s: %s (%d/%d samples below %.2f ms, %.2f%%)",
        message_type,
        summary["threshold_result"],
        summary["threshold_passed_samples"],
        summary["threshold_total_samples"],
        LATENCY_THRESHOLD_MS,
        summary["threshold_pass_percent"],
    )

    return summary, output_dir.resolve()


def run_csv_analysis(args: argparse.Namespace) -> int:
    """
    For each type of data we know about
    (Radio, SecureV2XMessage), find its CSV file, read, clean,
    and save the results and plots.
    """
    run_dir = args.run_dir.expanduser().resolve()
    input_dir = (
        run_dir if args.input_dir is None else args.input_dir.expanduser().resolve()
    )
    results_dir = run_dir / "results"

    # Stop early if the folders we need don't actually exist.
    if not run_dir.is_dir() or not input_dir.is_dir():
        logging.error(
            "Directory not found. Run: %s, Input: %s",
            run_dir,
            input_dir,
        )
        return 1

    results_dir.mkdir(parents=True, exist_ok=True)
    summary_records: list[dict[str, Any]] = []

    # Go through each data type one at a time (Radio, then SecureV2XMessage).
    for msg_type, cfg in DATA_TYPES.items():
        csv_file = find_csv_file(
            input_dir,
            cfg["patterns"],
        )

        if not csv_file:
            logging.info(
                "[-] No CSV file found for %s in %s",
                msg_type,
                input_dir,
            )
            continue

        logging.info(
            "[+] Processing %s: %s",
            msg_type,
            csv_file.name,
        )
        records = read_records(csv_file, msg_type)

        if not records:
            logging.warning(
                "  [-] No valid records in %s",
                csv_file.name,
            )
            continue

        df = process_csv(records)
        if df.empty:
            logging.warning("  [-] No valid non-negative latency calculated.")
            continue

        # Save the results, charts, and summary for this data type.
        summary, out_path = save_analysis(
            df,
            message_type=msg_type,
            run_name=run_dir.name,
            results_dir=results_dir,
            max_latency_ms=args.max_latency_ms,
            rolling_window=args.rolling_window,
        )
        summary_records.append(summary)
        print(
            f"  [✓] Processed {len(df):,} records | "
            f"Mean: {summary['mean_ms']:.2f} ms | "
            f"P95: {summary['p95_ms']:.2f} ms | "
            f"Threshold: {summary['threshold_result']} "
            f"({summary['threshold_pass_percent']:.2f}% below "
            f"{LATENCY_THRESHOLD_MS:g} ms)"
        )

    if not summary_records:
        logging.info("[-] No matching CSV data was processed.")
        return 0

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run-level Latency Analysis for CSVs.")
    parser.add_argument(
        "-r",
        "--run-dir",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--max-latency-ms",
        type=float,
        default=200.0,
    )
    parser.add_argument(
        "--rolling-window",
        type=int,
        default=20,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )

    cli_args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if cli_args.debug else logging.INFO)
    sys.exit(run_csv_analysis(cli_args))
