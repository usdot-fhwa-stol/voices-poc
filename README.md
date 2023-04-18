# VOICES Proof of Concept

Contains files to configure and run tests for the VOICES project.

## Scenario Files
The following files contain the details of the elements which will be used in a specific scenario. Elements can include vehicles, traffic signals, and weather.

<repository-root>
├── config -------------------------------------- Site configurations
│   ├── node_info.config -> <site-name>.config -- Symlink to this specific site configuration.
├── scenario_files ------------------------------ Scenario definitions.
└── scripts
    ├── build_tena_adapters --------------------- TENA adapter build configuration.
    ├── carla_python_scripts -------------------- Scripts to interface with the CARLA simulation.
    ├── collect_logs ---------------------------- Log collection script for test runs.
    └── run_scripts ----------------------------- Scripts to run specific scripts.
