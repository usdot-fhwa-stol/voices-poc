#!/bin/bash
trap cleanup SIGINT

function cleanup {
	echo "Stopping CARMA Simulation"
	pkill -9 CarlaUE4
	exit
}

. ../../../../config/node_info.config

if [[ -f $localCarlaPath/CarlaUE4.sh ]]; then
	echo "Found CARLA Simulator"
else
	echo
	echo "CARLA Simulator not found at $localCarlaPath/CarlaUE4.sh"
	exit
fi

mkdir -p $localCarmaSimLogPath

CARLA_LOG=$localCarmaSimLogPath/voices_carla_simulator.log

# set time mode producing faster that real time clock, disabled for Pilot 1 tests 1-3

$localCarlaPath/CarlaUE4.sh > $CARLA_LOG 2>&1 &

carla_pid=$!
echo "CARLA PID: "$carla_pid
sleep 7s

python3 $voicesPocPath/scripts/carla_python_scripts/blank_traffic_signals.py

python3 $voicesPocPath/scripts/carla_python_scripts/spectator_veiw_town_04.py

python3 $voicesPocPath/scripts/carla_python_scripts/set_time_mode.py

cleanup



