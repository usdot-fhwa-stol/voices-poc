#!/bin/bash
trap cleanup SIGINT

function cleanup {
	echo
	echo "Stopping CARMA Simulation"
	pkill -9 CarlaUE4
	exit
}

function print_help {
	echo
	echo "usage: start-carla.sh [--no_tick] [--low_quality] [--help]"
	echo
	echo "Start CARLA Simulator for VOICES"
	echo
	echo "optional arguments:"
	echo "    --no-tick          do not set time mode and tick simulation"
	echo "    --low_quality      start CARLA in low quality mode"
	echo "    --help             show help"
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

no_tick_enabled=false
low_quality_flag=""


for arg in "$@"
do
	if [[ $arg == "--no_tick" ]]; then
		
		no_tick_enabled=true

	elif [[ $arg == "--low_quality" ]]; then
		
		low_quality_flag="-quality-level=Low"

	elif [[ $arg == "--help" ]]; then
		
		print_help

	elif [[ $arg != "" ]]; then
		
		echo
		echo "Invalid argument: $arg"
		print_help
		exit

	fi
done

if [ "$no_tick_enabled" = true ]; then

	$localCarlaPath/CarlaUE4.sh $low_quality_flag > $CARLA_LOG 2>&1 &

	carla_pid=$!
	echo "CARLA PID: "$carla_pid
	sleep 7s

	python3 $voicesPocPath/scripts/carla_python_scripts/blank_traffic_signals.py

	python3 $voicesPocPath/scripts/carla_python_scripts/spectator_veiw_town_04.py

	read -s -n 1 -p "Press any key to quit . . ."

else
	
	$localCarlaPath/CarlaUE4.sh $low_quality_flag > $CARLA_LOG 2>&1 &

	carla_pid=$!
	echo "CARLA PID: "$carla_pid
	sleep 7s

	python3 $voicesPocPath/scripts/carla_python_scripts/blank_traffic_signals.py

	python3 $voicesPocPath/scripts/carla_python_scripts/spectator_veiw_town_04.py

	python3 $voicesPocPath/scripts/carla_python_scripts/set_time_mode.py

fi

cleanup



