"""Decode PCAPs and run V2X messaging-performance analysis."""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path

import pandas as pd
import pcapDecode
from radio_latency_plotting import (
    calculate_latency,
    calculate_statistics,
    plot_latency_cdf,
    plot_latency_histogram,
    plot_latency_timeseries,
    read_log_entries,
    results_to_dataframe,
)

PCAP_SUFFIXES = {".pcap"}

ENDPOINTS = (
    "dut_1",
    "proxy_1",
    "proxy_2",
    "dut_2",
    "v2xhub",
)

CAPTURE_DIRECTIONS = ("tx", "rx")

PCAP_ROLES = tuple(
    f"{endpoint}_{direction}"
    for endpoint in ENDPOINTS
    for direction in CAPTURE_DIRECTIONS
)

SUPPORTED_LINKS = (
    ("dut_1", "proxy_1"),
    ("dut_2", "proxy_2"),
    ("proxy_1", "v2xhub"),
    ("proxy_2", "v2xhub"),
    ("dut_1", "dut_2"),
)

ENDPOINT_PATTERNS = {
    "dut_1": r"dut[_-]?1",
    "proxy_1": r"proxy[_-]?1",
    "proxy_2": r"proxy[_-]?2",
    "dut_2": r"dut[_-]?2",
    "v2xhub": r"v2xhub[_-]|v2xhub",
}

DIRECTION_PATTERNS = {
    "tx": r"tx|transmit",
    "rx": r"rx|receive",
}


def validate_pcap(role: str, path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"PCAP assigned to {role} does not exist: {path}")

    if path.suffix.lower() not in PCAP_SUFFIXES:
        suffixes = ", ".join(sorted(PCAP_SUFFIXES))
        raise ValueError(
            f"Unsupported PCAP type for {role}: {path}. Expected one of: {suffixes}"
        )


def role_parts(role: str) -> tuple[str, str]:
    endpoint, direction = role.rsplit("_", maxsplit=1)
    return endpoint, direction


def cli_option_name(role: str) -> str:
    return f"--{role.replace('_', '-')}"


def decoded_log_name(pcap_path: Path) -> str:
    return f"decoded_{pcap_path.stem}.log"


def find_pcap_candidates(input_dir: Path, role: str) -> list[Path]:
    endpoint, direction = role_parts(role)
    endpoint_re = re.compile(
        rf"(?:^|[^a-z0-9]){ENDPOINT_PATTERNS[endpoint]}(?:[^a-z0-9]|$)",
        re.IGNORECASE,
    )
    direction_re = re.compile(
        rf"(?:^|[^a-z0-9]){DIRECTION_PATTERNS[direction]}(?:[^a-z0-9]|$)",
        re.IGNORECASE,
    )

    candidates: list[Path] = []

    for path in input_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in PCAP_SUFFIXES:
            continue

        rel_path = path.relative_to(input_dir)
        folder_parts = rel_path.parts[:-1]

        endpoint_in_folder = any(endpoint_re.search(part) for part in folder_parts)
        direction_in_folder = any(direction_re.search(part) for part in folder_parts)
        endpoint_in_file = endpoint_re.search(path.stem) is not None
        direction_in_file = direction_re.search(path.stem) is not None

        if (endpoint_in_folder or endpoint_in_file) and (direction_in_folder or direction_in_file):
            candidates.append(path.resolve())

    return sorted(candidates, key=lambda path: path.name.lower())


def discover_role_pcap(input_dir: Path, role: str) -> Path | None:
    candidates = find_pcap_candidates(input_dir, role)

    if not candidates:
        logging.info("No PCAP automatically discovered for %s", role)
        return None

    if len(candidates) > 1:
        candidate_list = "\n".join(f"  - {path}" for path in candidates)
        raise ValueError(
            f"Multiple PCAP files matched {role}:\n"
            f"{candidate_list}\n"
            f"Choose one explicitly with {cli_option_name(role)}."
        )

    logging.info("Automatically discovered %s: %s", role, candidates[0].name)
    return candidates[0]


def resolve_explicit_path(value: Path, input_dir: Path) -> Path:
    value = value.expanduser()
    if value.is_absolute():
        return value.resolve()

    input_relative = input_dir / value
    if input_relative.is_file():
        return input_relative.resolve()

    return value.resolve()


def collect_pcap_inputs(args: argparse.Namespace, input_dir: Path) -> dict[str, Path]:
    inputs: dict[str, Path] = {}
    assigned_paths: dict[Path, str] = {}

    for role in PCAP_ROLES:
        explicit_value = getattr(args, role, None)

        if explicit_value is not None:
            path = resolve_explicit_path(explicit_value, input_dir)
            logging.info("Using explicit %s PCAP: %s", role, path)
        else:
            path = discover_role_pcap(input_dir, role)

        if path is None:
            continue

        validate_pcap(role, path)

        if path in assigned_paths:
            other_role = assigned_paths[path]
            raise ValueError(
                f"The same PCAP is assigned to both {other_role} and {role}: {path}"
            )

        assigned_paths[path] = role
        inputs[role] = path

    return inputs


def locate_decoder_output(decoded_dir: Path, pcap_path: Path, expected_output: Path) -> Path:
    if expected_output.is_file() and expected_output.stat().st_size > 0:
        return expected_output.resolve()

    alternative_names = (
        f"decoded_{pcap_path.stem}.log",
        f"{pcap_path.stem}.log",
    )

    for filename in alternative_names:
        candidate = decoded_dir / filename
        if candidate.is_file() and candidate.stat().st_size > 0:
            logging.warning(
                "Decoder output filename differed from expectation; using %s", candidate
            )
            return candidate.resolve()

    raise RuntimeError(
        "The decoder completed without creating an identifiable nonempty log for "
        f"{pcap_path}. Expected: {expected_output}"
    )


def decode_pcap(role: str, pcap_path: Path, decoded_dir: Path, force_decode: bool) -> Path:
    decoded_dir.mkdir(parents=True, exist_ok=True)
    expected_output = decoded_dir / decoded_log_name(pcap_path)

    if not force_decode and expected_output.is_file() and expected_output.stat().st_size > 0:
        logging.info("Reusing decoded %s log: %s", role, expected_output)
        return expected_output.resolve()

    if expected_output.is_file():
        expected_output.unlink()

    logging.info("Decoding %s: %s", role, pcap_path.name)
    pcapDecode.decode_pcap(pcap_path, decoded_dir)

    decoded_log = locate_decoder_output(
        decoded_dir=decoded_dir,
        pcap_path=pcap_path,
        expected_output=expected_output,
    )

    logging.info("Decoded %s log: %s", role, decoded_log)
    return decoded_log


def supported_direction_names() -> set[str]:
    directions: set[str] = set()
    for endpoint_a, endpoint_b in SUPPORTED_LINKS:
        directions.add(f"{endpoint_a}_to_{endpoint_b}")
        directions.add(f"{endpoint_b}_to_{endpoint_a}")
    return directions


def parse_custom_result_names(values: list[str]) -> dict[str, str]:
    valid_directions = supported_direction_names()
    custom_names: dict[str, str] = {}

    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --name value {value!r}. Expected DIRECTION=FOLDER_NAME.")

        direction, folder_name = value.split("=", maxsplit=1)
        direction = direction.strip()
        folder_name = folder_name.strip()

        if direction not in valid_directions:
            valid_direction_text = ", ".join(sorted(valid_directions))
            raise ValueError(
                f"Unknown direction {direction!r} in --name. Valid directions: {valid_direction_text}"
            )

        if not folder_name:
            raise ValueError(f"Result folder name cannot be empty for {direction!r}.")

        if Path(folder_name).name != folder_name:
            raise ValueError(f"Result folder name must not contain path separators: {folder_name!r}")

        if folder_name in custom_names.values():
            raise ValueError(f"Custom result folder name is duplicated: {folder_name!r}")

        custom_names[direction] = folder_name

    return custom_names


def evaluate_direction(
    tx_endpoint: str,
    rx_endpoint: str,
    decoded_logs: dict[str, Path],
    results_dir: Path,
    custom_result_names: dict[str, str],
    max_latency_ms: int,
    rolling_window: int,
) -> Path | None:
    tx_role = f"{tx_endpoint}_tx"
    rx_role = f"{rx_endpoint}_rx"

    if tx_role not in decoded_logs or rx_role not in decoded_logs:
        logging.info(
            "Skipping %s -> %s because %s or %s is missing",
            tx_endpoint, rx_endpoint, tx_role, rx_role,
        )
        return None

    direction_name = f"{tx_endpoint}_to_{rx_endpoint}"
    folder_name = custom_result_names.get(direction_name, direction_name)
    output_dir = results_dir / folder_name
    os.makedirs(output_dir, exist_ok=True)

    logging.info("Analyzing and plotting %s -> %s", tx_endpoint, rx_endpoint)

    tx_entries = read_log_entries(decoded_logs[tx_role])
    rx_entries = read_log_entries(decoded_logs[rx_role])

    logging.info("Loaded %d TX messages and %d RX messages.", len(tx_entries), len(rx_entries))

    latency_results = calculate_latency(tx_entries, rx_entries)
    df = results_to_dataframe(latency_results)

    if df.empty:
        logging.warning("No matching TX/RX messages found for %s -> %s.", tx_endpoint, rx_endpoint)
        return None

    df.to_csv(output_dir / "latency_results.csv", index=False)

    plot_latency_histogram(df, output_dir, max_latency_ms)
    plot_latency_cdf(df, output_dir, max_latency_ms)
    plot_latency_timeseries(df, output_dir, rolling_window)

    summary = calculate_statistics(
        df,
        message_type=f"{tx_endpoint}->{rx_endpoint}",
        run_name=results_dir.parent.name,
    )
    pd.DataFrame([summary]).to_csv(output_dir / "results_summary.csv", index=False)

    logging.info("Results and plots written to: %s", output_dir)
    return output_dir.resolve()


def evaluate_bidirectional(
    endpoint_a: str,
    endpoint_b: str,
    decoded_logs: dict[str, Path],
    results_dir: Path,
    custom_result_names: dict[str, str],
    max_latency_ms: int,
    rolling_window: int,
) -> list[Path]:
    has_forward = f"{endpoint_a}_tx" in decoded_logs and f"{endpoint_b}_rx" in decoded_logs
    has_reverse = f"{endpoint_b}_tx" in decoded_logs and f"{endpoint_a}_rx" in decoded_logs

    if not has_forward and not has_reverse:
        logging.info("Skipping %s <-> %s because no complete direction is available", endpoint_a, endpoint_b)
        return []

    logging.info("=== Evaluating %s <-> %s ===", endpoint_a, endpoint_b)
    result_dirs: list[Path] = []

    forward_output = evaluate_direction(
        endpoint_a, endpoint_b, decoded_logs, results_dir, custom_result_names, max_latency_ms, rolling_window
    )
    if forward_output:
        result_dirs.append(forward_output)

    reverse_output = evaluate_direction(
        endpoint_b, endpoint_a, decoded_logs, results_dir, custom_result_names, max_latency_ms, rolling_window
    )
    if reverse_output:
        result_dirs.append(reverse_output)

    return result_dirs


def run_pcap_analysis(args: argparse.Namespace) -> int:
    """Core execution function called directly or via the runner."""
    try:
        run_dir = args.run_dir.expanduser().resolve()
        input_dir = run_dir if args.input_dir is None else args.input_dir.expanduser().resolve()

        if not run_dir.is_dir():
            raise FileNotFoundError(f"Run directory does not exist: {run_dir}")
        if not input_dir.is_dir():
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

        custom_result_names = parse_custom_result_names(getattr(args, "name", []))
        pcap_inputs = collect_pcap_inputs(args, input_dir)

        if not pcap_inputs:
            logging.warning("No PCAPs discovered in %s for PCAP analysis.", input_dir)
            return 0

        decoded_dir = run_dir / "decoded"
        results_dir = run_dir / "results"
        decoded_dir.mkdir(parents=True, exist_ok=True)
        results_dir.mkdir(parents=True, exist_ok=True)

        decoded_logs: dict[str, Path] = {}
        for role, pcap_path in sorted(pcap_inputs.items()):
            decoded_logs[role] = decode_pcap(
                role=role,
                pcap_path=pcap_path,
                decoded_dir=decoded_dir,
                force_decode=getattr(args, "force_decode", False),
            )

        result_dirs: list[Path] = []
        for endpoint_a, endpoint_b in SUPPORTED_LINKS:
            result_dirs.extend(
                evaluate_bidirectional(
                    endpoint_a, endpoint_b, decoded_logs, results_dir,
                    custom_result_names, int(args.max_latency_ms), args.rolling_window
                )
            )

        if not result_dirs:
            logging.warning("No valid bidirectional PCAP directions evaluated.")
            return 0

        print(f"[✓] PCAP Analysis complete. Results saved to: {results_dir}")
        return 0

    except Exception as error:
        logging.error("PCAP Analysis failed: %s", error)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode PCAPs and run V2X analysis.")
    parser.add_argument("-r", "--run-dir", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, default=None)
    parser.add_argument("--max-latency-ms", type=float, default=200.0)
    parser.add_argument("--rolling-window", type=int, default=20)
    parser.add_argument("--force-decode", action="store_true")
    parser.add_argument("--name", action="append", default=[])
    parser.add_argument("--debug", action="store_true")

    for role in PCAP_ROLES:
        parser.add_argument(cli_option_name(role), dest=role, type=Path, default=None)

    cli_args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if cli_args.debug else logging.INFO)
    sys.exit(run_pcap_analysis(cli_args))