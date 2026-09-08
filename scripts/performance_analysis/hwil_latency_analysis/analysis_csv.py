"""Run-level Latency Analysis for Radio & SecureV2XMessage CSVs."""

from __future__ import annotations

import argparse
import logging
import os
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
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._") or "analysis"


def normalize_timestamp_ms(value: Any) -> float:
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
    endpoint = clean_value(value)
    if not endpoint:
        return ""

    endpoint = re.sub(r"^[A-Za-z][A-Za-z0-9+.-]*://", "", endpoint)
    if endpoint.startswith("["):
        closing_bracket = endpoint.find("]")
        if closing_bracket != -1:
            return endpoint[1:closing_bracket]

    if endpoint.count(":") == 1:
        return endpoint.rsplit(":", maxsplit=1)[0]

    return endpoint


def find_csv_file(directory: Path, patterns: Iterable[str]) -> Path | None:
    if not directory.is_dir():
        return None

    for pattern in patterns:
        matches = list(directory.rglob(pattern))
        if matches:
            return sorted(matches)[0]

    return None


def read_records(csv_file: Path, msg_type: str) -> list[LogRecord]:
    cfg = DATA_TYPES[msg_type]

    try:
        df = pd.read_csv(csv_file, dtype=str, low_memory=False)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        logging.error("Failed to read %s: %s", csv_file, error)
        return []

    tx_col = next(
        (c for c in ("Metadata,TimeOfTransmission", "Metadata,TimeOfCommit", "const^Metadata,TimeOfCreation") if c in df.columns),
        None,
    )
    rx_col = next(
        (c for c in ("Metadata,TimeOfReceipt", "packetTimestamp") if c in df.columns),
        None,
    )

    if tx_col is None or rx_col is None:
        logging.warning("Missing timing columns in %s", csv_file)
        return []

    event_col = "Metadata,Enum,Middleware::EventType"
    skip_events = cfg["skip_events"]
    if event_col in df.columns and skip_events:
        df = df.loc[~df[event_col].isin(skip_events)]

    ip_col = next(
        (c for c in ("const^Metadata,SDOid.hostIPaddress", "Metadata,Endpoint", "const^Metadata,Endpoint") if c in df.columns),
        None,
    )

    available_id_cols = [c for c in cfg["id_cols"] if c in df.columns]

    records: list[LogRecord] = []
    for row_index, row in df.iterrows():
        try:
            tx_ms = normalize_timestamp_ms(row[tx_col])
            rx_ms = normalize_timestamp_ms(row[rx_col])
        except (TypeError, ValueError, OverflowError):
            continue

        key_parts = [clean_value(row.get(c)) for c in available_id_cols if clean_value(row.get(c))]
        row_id = clean_value(row.get("rowID")) or str(row_index)

        match_key = f"{msg_type}::{'::'.join(key_parts)}" if key_parts else f"{msg_type}::row::{row_id}"
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

    return sorted(records, key=lambda r: (r.tx_time_ms, r.rx_time_ms))


def process_csv(records: list[LogRecord]) -> pd.DataFrame:
    rows = [
        {
            "Tx Timestamp (ms)": record.tx_time_ms,
            "Rx Timestamp (ms)": record.rx_time_ms,
            "Latency (ms)": record.latency_ms,
            "Match Key": record.match_key,
            "Row ID": record.row_id,
            "IP Address": record.ip_address,
            "Datetime": pd.to_datetime(record.tx_time_ms, unit="ms", utc=True, errors="coerce"),
        }
        for record in records
        if np.isfinite(record.latency_ms) and record.latency_ms >= 0
    ]
    return pd.DataFrame(rows)


def save_analysis(
    df: pd.DataFrame,
    *,
    message_type: str,
    run_name: str,
    results_dir: Path,
    max_latency_ms: float,
    rolling_window: int,
) -> tuple[dict[str, Any], Path]:
    output_dir = results_dir / safe_filename(message_type)
    os.makedirs(output_dir, exist_ok=True)

    df.to_csv(output_dir / "latency_results.csv", index=False)

    plot_latency_histogram(df, output_dir, int(max_latency_ms))
    plot_latency_cdf(df, output_dir, int(max_latency_ms))
    plot_latency_timeseries(df, output_dir, rolling_window)

    summary = calculate_statistics(df, message_type=message_type, run_name=run_name)
    pd.DataFrame([summary]).to_csv(output_dir / "results_summary.csv", index=False)

    return summary, output_dir.resolve()


def run_csv_analysis(args: argparse.Namespace) -> int:
    """Core execution function called directly or via the runner."""
    run_dir = args.run_dir.expanduser().resolve()
    input_dir = run_dir if args.input_dir is None else args.input_dir.expanduser().resolve()
    results_dir = run_dir / "results"

    if not run_dir.is_dir() or not input_dir.is_dir():
        logging.error("Directory not found. Run: %s, Input: %s", run_dir, input_dir)
        return 1

    results_dir.mkdir(parents=True, exist_ok=True)
    summary_records: list[dict[str, Any]] = []

    for msg_type, cfg in DATA_TYPES.items():
        csv_file = find_csv_file(input_dir, cfg["patterns"])

        if not csv_file:
            logging.info("[-] No CSV file found for %s in %s", msg_type, input_dir)
            continue

        logging.info("[+] Processing %s: %s", msg_type, csv_file.name)
        records = read_records(csv_file, msg_type)

        if not records:
            logging.warning("  [-] No valid records in %s", csv_file.name)
            continue

        df = process_csv(records)
        if df.empty:
            logging.warning("  [-] No valid non-negative latency calculated.")
            continue

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
            f"Mean: {summary['mean_ms']:.2f} ms | P95: {summary['p95_ms']:.2f} ms"
        )

    if not summary_records:
        logging.info("[-] No matching CSV data was processed.")
        return 0

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run-level Latency Analysis for CSVs.")
    parser.add_argument("-r", "--run-dir", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, default=None)
    parser.add_argument("--max-latency-ms", type=float, default=200.0)
    parser.add_argument("--rolling-window", type=int, default=20)
    parser.add_argument("--debug", action="store_true")

    cli_args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if cli_args.debug else logging.INFO)
    sys.exit(run_csv_analysis(cli_args))