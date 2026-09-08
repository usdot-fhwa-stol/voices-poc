#!/usr/bin/env python3
"""
Unified V2X Analysis Runner.
Executes PCAP decoding/analysis and CSV analysis using shared arguments.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import analysis_csv
import analysis_pcap


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Unified V2X Latency Analysis runner for PCAP and CSV files."
    )

    # --- Shared Arguments ---
    parser.add_argument(
        "-r",
        "--run-dir",
        type=Path,
        required=True,
        help="Directory for analysis output results.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing input files (defaults to --run-dir).",
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
        help="Customize result directory names (e.g., --name dut_1_to_proxy_1=side_1).",
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

    results: list[int] = []

    if run_pcap:
        logging.info("================ Running PCAP Analysis ================")
        pcap_status = analysis_pcap.run_pcap_analysis(args)
        results.append(pcap_status)

    if run_csv:
        logging.info("================ Running CSV Analysis ================")
        csv_status = analysis_csv.run_csv_analysis(args)
        results.append(csv_status)

    return max(results) if results else 0


if __name__ == "__main__":
    sys.exit(main())