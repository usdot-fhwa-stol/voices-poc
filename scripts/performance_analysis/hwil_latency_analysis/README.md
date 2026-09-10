# Radio HWIL Latency Analysis

This tool runs the PCAP and CSV latency analyses for either:

- One selected run
- A batch containing multiple run directories

It also collects the generated `results_summary.csv` files into a consolidated
`total_data_summary.csv`.

A run is marked as failed if at least one test has a threshold result of
`FAIL`, or `ERROR`.

## Input Folder Setup

### Single run

For the simplest setup, place all PCAP and CSV inputs under one run directory:

```text
runs/
└── run_001/
    ├── dut_1_tx.pcap
    ├── dut_1_rx.pcap
    ├── dut_2_tx.pcap
    ├── dut_2_rx.pcap
    ├── proxy_1_tx.pcap
    ├── proxy_1_rx.pcap
    ├── proxy_2_tx.pcap
    ├── proxy_2_rx.pcap
    ├── v2xhub_tx.pcap
    ├── v2xhub_rx.pcap
    ├── Entities-Radio.csv
    └── TV2XMsg-SecureV2XMsg.csv
```

The files may also be placed in subdirectories. For example:

```text
runs/
└── run_001/
    ├── pcap/
    │   ├── dut_1/
    │   │   ├── tx.pcap
    │   │   └── rx.pcap
    │   ├── proxy_1/
    │   │   ├── tx.pcap
    │   │   └── rx.pcap
    │   └── v2xhub/
    │       ├── tx.pcap
    │       └── rx.pcap
    └── csv/
        ├── Entities-Radio.csv
        └── TV2XMsg-SecureV2XMsg.csv
```

The analysis searches recursively under the selected input directory.

### PCAP filename discovery

PCAP files are assigned to roles by looking for an endpoint and direction in
the filename or folder path.

Supported endpoints are:

```text
dut_1
dut_2
proxy_1
proxy_2
v2xhub
```

Supported directions are:

```text
tx
rx
```

Endpoint names may use forms such as:

```text
dut_1
dut-1
dut1
proxy_1
proxy-1
proxy1
```

Directions may use:

```text
tx
rx
transmit
receive
```

Examples of discoverable PCAP names include:

```text
dut_1_tx.pcap
dut-1-receive.pcap
proxy1_transmit.pcap
v2xhub_rx.pcap
```

The endpoint and direction can also be represented by folder names:

```text
run_001/
└── dut_1/
    ├── tx/
    │   └── capture.pcap
    └── rx/
        └── capture.pcap
```

If multiple PCAP files match the same role, automatic discovery stops with an
error. Use an explicit PCAP option to select the correct file.

### CSV filename discovery

The CSV analysis looks for these filename patterns recursively.

#### Radio

```text
*Entities-Radio*.csv
*Radio*.csv
```

#### SecureV2XMessage

```text
*TV2XMsg-SecureV2XMsg*.csv
*SecureV2XMsg*.csv
*SecureV2X*.csv
```

If multiple files match, the first sorted match is used.

## Running a Single Run

Run both PCAP and CSV analysis:

```bash
python run_analysis.py --run-dir /path/to/runs/run_001
```

Short form:

```bash
python run_analysis.py -r /path/to/runs/run_001
```

When `--input-dir` is not provided, the run directory is also used as the input
directory.

### Separate single-run input and output directories

Use `--run-dir` for generated output and `--input-dir` for source data:

```bash
python run_analysis.py \
  --run-dir /path/to/output/run_001 \
  --input-dir /path/to/input/run_001
```

The `--run-dir` directory must already exist. Generated `decoded` and `results`
subdirectories are created automatically.

## Running a Batch

A batch directory must contain one immediate child directory for each run:

```text
runs/
├── run_001/
│   ├── dut_1_tx.pcap
│   ├── proxy_1_rx.pcap
│   └── Entities-Radio.csv
├── run_002/
│   ├── dut_1_tx.pcap
│   ├── proxy_1_rx.pcap
│   └── Entities-Radio.csv
└── run_003/
    ├── dut_1_tx.pcap
    ├── proxy_1_rx.pcap
    └── Entities-Radio.csv
```

Run every immediate child directory:

```bash
python run_analysis.py --batch-dir /path/to/runs
```

The runner ignores these directories when discovering runs:

```text
decoded
results
__pycache__
```

It also ignores hidden directories whose names start with `.`.

### Separate batch input and output directories

Input and output runs must have matching directory names:

```text
input-runs/
├── run_001/
├── run_002/
└── run_003/

output-runs/
├── run_001/
├── run_002/
└── run_003/
```

Run the batch with:

```bash
python run_analysis.py \
  --batch-dir /path/to/output-runs \
  --input-dir /path/to/input-runs
```

For each output run, the runner selects the same-named input directory:

```text
output-runs/run_001 -> input-runs/run_001
output-runs/run_002 -> input-runs/run_002
output-runs/run_003 -> input-runs/run_003
```

The run directories under `--batch-dir` must already exist.

## Analysis Options

### Skip PCAP analysis

```bash
python run_analysis.py \
  --run-dir /path/to/run_001 \
  --no-pcap
```

### Skip CSV analysis

```bash
python run_analysis.py \
  --run-dir /path/to/run_001 \
  --no-csv
```

### Force PCAP decoding

Existing decoded logs are normally reused. To decode every selected PCAP
again:

```bash
python run_analysis.py \
  --run-dir /path/to/run_001 \
  --force-decode
```

### Enable debug logging

```bash
python run_analysis.py \
  --run-dir /path/to/run_001 \
  --debug
```

### Set the plot latency range

`--max-latency-ms` controls the maximum displayed latency in histogram and CDF
plots. It does not change the pass/fail thresholds.

```bash
python run_analysis.py \
  --run-dir /path/to/run_001 \
  --max-latency-ms 250
```

The default is `200` milliseconds.

### Set the rolling window

```bash
python run_analysis.py \
  --run-dir /path/to/run_001 \
  --rolling-window 50
```

The default rolling window is `20` samples.

## Explicit PCAP Selection

If automatic discovery cannot identify a PCAP unambiguously, provide its path
explicitly.

Available options include:

```text
--dut-1-tx
--dut-1-rx
--dut-2-tx
--dut-2-rx
--proxy-1-tx
--proxy-1-rx
--proxy-2-tx
--proxy-2-rx
--v2xhub-tx
--v2xhub-rx
```

Example:

```bash
python run_analysis.py \
  --run-dir /path/to/run_001 \
  --dut-1-tx /path/to/run_001/captures/sender.pcap \
  --proxy-1-rx /path/to/run_001/captures/receiver.pcap
```

Paths may be absolute or relative to the selected input directory.

Explicit PCAP options are most suitable for single-run analysis. Batch runs
should use consistent, discoverable endpoint and direction names in each run
directory.

## Custom PCAP Result Names

By default, PCAP result directories use direction names such as:

```text
dut_1_to_proxy_1
proxy_1_to_dut_1
proxy_1_to_v2xhub
dut_1_to_dut_2
```

Use `--name` to customize one:

```bash
python run_analysis.py \
  --run-dir /path/to/run_001 \
  --name dut_1_to_proxy_1=side_1
```

Use `--name` more than once to customize multiple directions:

```bash
python run_analysis.py \
  --run-dir /path/to/run_001 \
  --name dut_1_to_proxy_1=side_1 \
  --name dut_2_to_proxy_2=side_2
```

Custom names must:

- Use the `DIRECTION=FOLDER_NAME` format
- Refer to a supported direction
- Not contain path separators
- Not duplicate another custom folder name

## Latency Thresholds

### PCAP thresholds

| Direction | Threshold |
|---|---:|
| DUT to DUT | `< 120 ms` |
| DUT to proxy | `< 39.77 ms` |
| Proxy to V2X Hub | `< 10 ms` |
| Proxy to DUT | `< 32 ms` |

### CSV threshold

Both CSV message types use:

```text
< 10 ms
```

An individual test receives a `PASS` result only when every valid latency
sample is below its configured threshold.

## Generated Output

### Single-run output

After analysis, a run generally has this structure:

```text
run_001/
├── decoded/
│   ├── decoded_dut_1_tx.log
│   ├── decoded_proxy_1_rx.log
│   └── ...
└── results/
    ├── dut_1_to_proxy_1/
    │   ├── latency_results.csv
    │   ├── results_summary.csv
    │   └── plot files
    ├── proxy_1_to_dut_1/
    │   ├── latency_results.csv
    │   ├── results_summary.csv
    │   └── plot files
    ├── Radio/
    │   ├── latency_results.csv
    │   ├── results_summary.csv
    │   └── plot files
    ├── SecureV2XMessage/
    │   ├── latency_results.csv
    │   ├── results_summary.csv
    │   └── plot files
    └── total_data_summary.csv
```

### Batch output

Each run receives its own summary:

```text
runs/
├── run_001/
│   └── results/
│       └── total_data_summary.csv
├── run_002/
│   └── results/
│       └── total_data_summary.csv
└── total_data_summary.csv
```

The batch-level file combines the test summaries from every processed run:

```text
<batch-dir>/total_data_summary.csv
```

## Summary Columns

Each individual `results_summary.csv` includes threshold information such as:

```text
latency_threshold_ms
passed_samples
failed_samples
pass_percent
threshold_result
```

The consolidated `total_data_summary.csv` adds identification and run-level
status columns:

```text
run_name
test_name
summary_file
run_result
run_failed
failure_reason
analysis_status
```

### Run failure behavior

A run is marked with:

```text
run_result = FAIL
run_failed = True
failure_reason = THRESHOLD_FAILURE
```

if even one generated test summary contains:

```text
threshold_result = FAIL
```

It is also marked as failed if an analysis process returns an error:

```text
run_result = FAIL
run_failed = True
failure_reason = ANALYSIS_ERROR
```

If no test summaries are found:

```text
run_result = NO_RESULTS
run_failed = False
failure_reason = NO_RESULTS
```

## Common Commands

Run all analyses for one run:

```bash
python run_analysis.py -r /data/runs/run_001
```

Run all analyses for a batch:

```bash
python run_analysis.py --batch-dir /data/runs
```

Run only PCAP analysis:

```bash
python run_analysis.py \
  --batch-dir /data/runs \
  --no-csv
```

Run only CSV analysis:

```bash
python run_analysis.py \
  --batch-dir /data/runs \
  --no-pcap
```

Force PCAP decoding with debug logs:

```bash
python run_analysis.py \
  --run-dir /data/runs/run_001 \
  --force-decode \
  --debug
```

Use separate batch input and output locations:

```bash
python run_analysis.py \
  --batch-dir /data/analysis-output \
  --input-dir /data/captured-runs
```
