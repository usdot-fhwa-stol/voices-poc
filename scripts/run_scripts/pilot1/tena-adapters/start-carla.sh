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

set_time_mode_cmd="python3 $voicesPocPath/scripts/carla_python_scripts/set_time_mode.py"


$localCarlaPath/CarlaUE4.sh &>> $CARLA_LOG &

carla_pid=$!
echo "PID: "$carla_pid
sleep 7s

python3 $voicesPocPath/scripts/carla_python_scripts/spectator_veiw_town_04.py

python3 $voicesPocPath/scripts/carla_python_scripts/set_time_mode.py

cleanup



