#!/bin/bash
trap cleanup SIGINT

function cleanup {
	echo "Stopping CARMA Simulation"
	pkill -9 CarlaUE4
	exit
}

. ../../../../config/node_info.config


mkdir -p $localCarmaSimLogPath

CARLA_LOG=$localCarmaSimLogPath/voices_carla_simulator.log

set_time_mode_cmd="python3 $voicesPocPath/scripts/carla_python_scripts/set_time_mode.py"


$localCarlaPath/CarlaUE4.sh &>> $CARLA_LOG &

carla_pid=$!
echo "PID: "$carla_pid
sleep 7s

python3 $voicesPocPath/scripts/carla_python_scripts/set_time_mode.py

cleanup



