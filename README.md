# VOICES Proof of Concept


TODO update


# voices-poc
## All Components
CARLA
J2735 Message Adapter
Traffic Light Entity Generator
CARMA
CARLA TENA Adapter
Scenario Publisher
CARMA Platform TENA Adapter
Simple Vehicle Model
## EM Pilot 1
Execution Manager
Sceneraio publisher
Data collections - tdcs tena data collection system (optinoal)
## UCLA - Constructive simulation
CARLA
CARLA TENA Adapter
Vechile Model
TJ2735 Adapter
## Nissan
CARLA
CARLA TENA Adapter
Simple Vehicle Model
## Econolite
//CARLA Adapter ?
CARLA
Traffic Light Entity Generator
J2735 Message Adapter
Virtual Traffic Controller
## MCity
CARLA
CARLA TENA Adapter








# Run Instructions

# Start Execution Manager
/opt/TENA/Console-v2.0.1/start.sh

# Start DataCollection
$HOME/TENA/VOICES-Combined-v0.12.0-DataCollection-v1.1.10/start.sh

# Start CARLA
$HOME/CARLA_0.9.10/CarlaUE4.sh

# Change map
python3 config.py -m Town04

# Start CARLA-TENA Adapter
$HOME/voices-poc/scripts/run_scripts/pilot1/runCarlaAdapter.sh

# Start Scenario-Publisher

# Start manually-driven car
python3 manual_control_keyboard_virtual.py

# Follow a car in a running simulation
python3 manual_control_keyboard_virtual.py --follow_vehicle CARMA-MANUAL-2








## Scenario Files
The following files contain the details of the elements which will be used in a specific scenario. Elements can include vehicles, traffic signals, and weather.



<repository-root>
├── config -------------------------------------- Site configurations
│   ├── node_info.config -> <site-name>.config -- Symlink to this specific site configuration.
├── scenario_files ------------------------------ Scenario definitions.
└── scripts
    ├── build_tena_adapters
    │   ├── buildTenaAdapters.sh
    │   └── readme.md
    ├── carla_python_scripts - Handy customized CARLA scripts. Also refer to the CARLA-provided scripts in $CARLA_HOME/...../
    │   ├── config.py
    │   ├── destroy_signals.py
    │   ├── destroy_vehicles.py
    │   ├── first_person_live_vehicle.py
    │   ├── follow_vehicle_3rd_person_behind.py
    │   ├── follow_vehicle_3rd_person_behind_switching.py
    │   ├── follow_vehicle_birds_eye.py
    │   ├── follow_vehicle_dash_cam.py
    │   ├── follow_vehicle_top_down.py
    │   ├── get_signals.py
    │   ├── get_trafficSignal_actorID.py
    │   ├── get_vehicles.py
    │   ├── list_maps.py
    │   ├── live_vehicle_birds_eye.py
    │   ├── log_vehicles_signals.py
    │   ├── manual_control_keyboard.py
    │   ├── manual_control_keyboard_virtual.py
    │   ├── manual_control_steeringwheel_ff_lap.py
    │   ├── manual_control_steeringwheel_ff_no_hud.py
    │   ├── manual_control_steeringwheel_ff.py
    │   ├── manual_control_steeringwheel_ff_virtual.py
    │   ├── readme.md
    │   ├── set_time_mode.py
    │   ├── spawn_npc.py
    │   ├── ubuntu_desktop_shortcuts -- Installable desktop shortcuts.
    │   └── wheel_config.ini
    ├── collect_logs
    │   ├── collect_voices_logs.sh
    │   └── log_files
    │       ├── carma_sim_logs
    │       │   ├── voices_carla_carma_integration.log
    │       │   └── voices_carla_simulator.log
    │       ├── local_adapter_logs
    │       │   ├── carla_adapter_terminal_out.log
    │       │   └── carma_platform_adapter_terminal_out.log
    │       ├── second_vehicle_20220908133328_ntp_test
    │       │   ├── carma_platform_in.pcap
    │       │   ├── carma_platform_out.pcap
    │       │   ├── e0c6c87c-2f9a-11ed-b6b3-a8a1599846b2
    │       │   │   ├── carma_record-carma_record-67-stdout.log
    │       │   │   ├── carma_record-carma_record_load_regex-66-stdout.log
    │       │   │   ├── environment-carma_wm_broadcaster-18-stdout.log
    │       │   │   ├── environment-lanelet2_map_loader-16-stdout.log
    │       │   │   ├── environment-lanelet2_map_visualization-17-stdout.log
    │       │   │   ├── environment-motion_computation-19-stdout.log
    │       │   │   ├── environment-motion_prediction_visualizer-21-stdout.log
    │       │   │   ├── environment-naive_motion_predict-32-stdout.log
    │       │   │   ├── environment-ray_ground_filter-34-stdout.log
    │       │   │   ├── environment-roadway_objects-20-stdout.log
    │       │   │   ├── environment-traffic_incident_parser-35-stdout.log
    │       │   │   ├── guidance-arbitrator-38-stdout.log
    │       │   │   ├── guidance-cooperative_lanechange-52-stdout.log
    │       │   │   ├── guidance-guidance_node-37-stdout.log
    │       │   │   ├── guidance-guidance_plugin_validator-63.log
    │       │   │   ├── guidance-guidance_plugin_validator-63-stdout.log
    │       │   │   ├── guidance-health_monitor-36-stdout.log
    │       │   │   ├── guidance-inlanecruising_plugin-48-stdout.log
    │       │   │   ├── guidance-intersection_transit_maneuvering-60-stdout.log
    │       │   │   ├── guidance-mobilitypath_publisher-54-stdout.log
    │       │   │   ├── guidance-mobilitypath_visualizer-55-stdout.log
    │       │   │   ├── guidance-plan_delegator-39-stdout.log
    │       │   │   ├── guidance-platoon_control-45-stdout.log
    │       │   │   ├── guidance-platooning_tactical_plugin-49-stdout.log
    │       │   │   ├── guidance-platoon_strategic-59-stdout.log
    │       │   │   ├── guidance-port_drayage_plugin-58-stdout.log
    │       │   │   ├── guidance-pure_pursuit-41-stdout.log
    │       │   │   ├── guidance-pure_pursuit_wrapper_node-42-stdout.log
    │       │   │   ├── guidance-route-53-stdout.log
    │       │   │   ├── guidance-route_following_plugin-43-stdout.log
    │       │   │   ├── guidance-sci_strategic_plugin-61-stdout.log
    │       │   │   ├── guidance-stop_and_wait_plugin-50-stdout.log
    │       │   │   ├── guidance-stop_controlled_intersection_tactical_plugin-62-stdout.log
    │       │   │   ├── guidance-trajectory_executor_node-40-stdout.log
    │       │   │   ├── guidance-trajectory_visualizer-56-stdout.log
    │       │   │   ├── guidance-twist_filter-46-stdout.log
    │       │   │   ├── guidance-twist_gate-47-stdout.log
    │       │   │   ├── guidance-unobstructed_lanechange-51-stdout.log
    │       │   │   ├── guidance-wz_strategic_plugin-44-stdout.log
    │       │   │   ├── guidance-yield_plugin-57-stdout.log
    │       │   │   ├── hardware_interface-driver_shutdown_voices_1_1_6810500306609373757-1-stdout.log
    │       │   │   ├── hardware_interface-lightbar_manager-2-stdout.log
    │       │   │   ├── localization-config_random_filter-9.log
    │       │   │   ├── localization-config_random_filter-9-stdout.log
    │       │   │   ├── localization-config_voxel_grid_filter-11.log
    │       │   │   ├── localization-config_voxel_grid_filter-11-stdout.log
    │       │   │   ├── localization-gnss_to_map_convertor-6-stdout.log
    │       │   │   ├── localization-localization_manager-7-stdout.log
    │       │   │   ├── localization-map_param_loader-3-stdout.log
    │       │   │   ├── localization-ndt_matching-5-stdout.log
    │       │   │   ├── localization-points_map_loader-4-stdout.log
    │       │   │   ├── localization-random_filter-10-stdout.log
    │       │   │   ├── localization-voxel_grid_filter-12-stdout.log
    │       │   │   ├── master.log
    │       │   │   ├── message-bsm_generator-14-stdout.log
    │       │   │   ├── message-cpp_message_node-15-stdout.log
    │       │   │   ├── message-j2735_convertor-13-stdout.log
    │       │   │   ├── param_dump-68-stdout.log
    │       │   │   ├── robot_state_publisher-1-stdout.log
    │       │   │   ├── roslaunch-voices-1-1.log
    │       │   │   ├── rosout-1-stdout.log
    │       │   │   ├── rosout.log
    │       │   │   ├── rosparams.yaml
    │       │   │   ├── ui-rosapi-65.log
    │       │   │   └── ui-rosbridge_websocket-64.log
    │       │   └── TDCS-20220908173345.sqlite
    │       ├── second_vehicle_20220908133328_ntp_test.zip
    │       ├── second_vehicle_2022092111xxxx_boost-crash.tar
    │       ├── second_vehicle_20220921151312_demo1b_run_4.tar
    │       ├── second_vehicle_20220921152144_demo1b_run_5.tar
    │       ├── second_vehicle_20220921153516_demo1b_run_6.tar
    │       └── second_vehicle_20220921154420_demo1b_run_7.tar
    ├── DecodeSinglePCAP
    │   ├── decodeJ2735.py
    │   ├── J2735_201603_combined.py
    │   ├── J2735_201603_combined_voices_mr_fix.py
    │   └── pcapDecoder.py
    ├── encodeJ2735
    │   ├── encodeJ2735.py
    │   ├── J2735.py
    │   └── README.txt
    ├── install_spat_plugins
    │   ├── installSpatPlugins.sh
    │   ├── manifest_east.json
    │   ├── manifest_west.json
    │   ├── readme.md
    │   ├── SpatPlugin_East.zip
    │   └── SpatPlugin_West.zip
    ├── J2735_pcap_decoder
    │   └── src
    │       ├── J2735_201603_combined.py
    │       ├── J2735_201603_combined_voices_mr_fix.py
    │       ├── J2735decoder.py
    │       ├── J2735_pcap_decoder.sh
    │       ├── tshark_ascii_parser.py
    │       ├── tshark_json_parser.py
    │       └── tshark_OutputParser.py
    ├── performance_analysis
    │   ├── batch_calculate_e2e_perf.py
    │   ├── calculate_e2e_perf.py
    │   ├── get_latency_from_tena_network_logs.py
    │   └── throughput_analysis
    │       └── calculate_throughput_averages.py
    ├── readme.md
    ├── run_scripts
    │   ├── demo0
    │   │   ├── carla_node
    │   │   │   ├── runCarlaAdapter.sh
    │   │   │   └── runEntityGenerator.sh
    │   │   ├── tena_node
    │   │   │   └── runScenarioPublisher.sh
    │   │   └── v2x_node
    │   │       ├── runTenaspatplugin_east.sh
    │   │       ├── runTenaspatplugin_west.sh
    │   │       └── runTenaV2XHubGatewayplugin
    │   ├── demo1
    │   │   ├── augusta_prod.config
    │   │   ├── augusta_test.config
    │   │   ├── constructive_node
    │   │   │   ├── runCarlaAdapter.sh
    │   │   │   ├── runCarmaPlatformAdapter.sh
    │   │   │   └── runCarmaSim.sh
    │   │   ├── live_node
    │   │   │   ├── runCarlaAdapter.sh
    │   │   │   └── runEntityGenerator.sh
    │   │   ├── mitre_prod.config
    │   │   ├── mitre_test.config
    │   │   ├── node_info.config -> placeholder.config
    │   │   ├── other_apps
    │   │   │   └── runScenarioPublisher.sh
    │   │   ├── springfield_prod.config
    │   │   ├── springfield_test.config
    │   │   ├── tfhrc_prod.config
    │   │   ├── tfhrc_test.config
    │   │   ├── tfhrc_test_replay.config
    │   │   ├── v2xhub_prod.config
    │   │   ├── v2xhub_test.config
    │   │   └── virtual_node
    │   │       └── runCarlaAdapter.sh
    │   ├── pilot1
    │   │   └── runCarlaAdapter.sh
    │   └── readme.md
    └── v2xhub_database_scripts
        ├── constants.py
        ├── README.md
        ├── v2xhub_sql_import.py
        └── v2xhub_sql_update.py
