# VOICES Proof of Concept

Contains files to configure and run tests for the VOICES project.

## Directory Structure

<repository-root>
├── config -------------------------------------- Site configurations
│   ├── node_info.config -> <site-name>.config -- Symlink to this specific site configuration.
├── scenario_files ------------------------------ Scenario definitions.
└── scripts
    ├── build_tena_adapters --------------------- TENA adapter build configuration.
    ├── carla_python_scripts -------------------- Scripts to interface with the CARLA simulation.
    ├── collect_logs ---------------------------- Log collection script for test runs.
    └── run_scripts ----------------------------- Scripts to run specific scripts.
