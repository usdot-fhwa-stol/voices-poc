#!/bin/bash


python3 batch_calculate_e2e_perf_pilot2.py -m ~/voices-poc/logs/P2E2-RFR2/R1/metadata.json -n P2E2-RFR2-R1-BSM --plot_only
python3 batch_calculate_e2e_perf_pilot2.py -m ~/voices-poc/logs/P2E2-RFR2/R2/metadata.json -n P2E2-RFR2-R2-BSM --plot_only
python3 batch_calculate_e2e_perf_pilot2.py -m ~/voices-poc/logs/P2E2-RFR2/R3/metadata.json -n P2E2-RFR2-R3-BSM --plot_only
python3 batch_calculate_e2e_perf_pilot2.py -m ~/voices-poc/logs/P2E2-RFR2/R4/metadata.json -n P2E2-RFR2-R4-BSM --plot_only
python3 batch_calculate_e2e_perf_pilot2.py -m ~/voices-poc/logs/P2E2-RFR2/R5/metadata.json -n P2E2-RFR2-R5-BSM --plot_only