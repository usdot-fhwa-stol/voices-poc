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
	echo "    --map <map name>   start carla with given map name"
	echo "                           Currently supported maps:"
	echo "                             - Town04"
	echo "                             - smart_intersection"
	echo "    --help             show help"
	echo
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

no_tick_enabled=false
low_quality_flag=""
next_flag_is_map=false
carla_map=""


for arg in "$@"
do
	if [ "$next_flag_is_map" = true ]; then

		carla_map=$arg
		next_flag_is_map=false
	
	elif [[ $arg == "--no_tick" ]]; then
		
		no_tick_enabled=true

	elif [[ $arg == "--low_quality" ]]; then
		
		low_quality_flag="-quality-level=Low"

	elif [[ $arg == "--map" ]]; then
		
		next_flag_is_map=true

	elif [[ $arg == "--help" ]]; then
		
		print_help
		exit

	elif [[ $arg != "" ]]; then
		
		echo
		echo "Invalid argument: $arg"
		print_help
		exit

	fi
done

$localCarlaPath/CarlaUE4.sh $low_quality_flag > $CARLA_LOG 2>&1 &

carla_pid=$!
echo "CARLA PID: "$carla_pid
sleep 7s


if [[ $carla_map == "Town04" ]]; then

	echo "Changing map to: $carla_map"
	python3 $voicesPocPath/scripts/carla_python_scripts/config.py -m $carla_map
	sleep 5s

	python3 $voicesPocPath/scripts/carla_python_scripts/spectator_view_town_04.py


elif [[ $carla_map == "smart_intersection" ]]; then

	echo "Changing map to: $carla_map"
	python3 $voicesPocPath/scripts/carla_python_scripts/config.py -m $carla_map
	sleep 5s

	python3 $voicesPocPath/scripts/carla_python_scripts/spectator_view_smart_intersection.py

elif [[ $carla_map == "" ]]; then

	echo "Loading default CARLA map"

else
	echo
	echo "Map not supported: $carla_map"
	echo
	cleanup
	
fi

python3 $voicesPocPath/scripts/carla_python_scripts/blank_traffic_signals.py


if [ "$no_tick_enabled" = true ]; then

	read -s -n 1 -p "Press any key to quit . . ."

else

	python3 $voicesPocPath/scripts/carla_python_scripts/set_time_mode.py

fi

cleanup



