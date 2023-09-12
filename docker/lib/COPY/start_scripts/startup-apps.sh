#! /bin/bash

source /home/start_scripts/setup-docker.sh


sleep 5s

if [[ $VOICES_START_EM == true ]]; then
   echo "STARTING TENA EXECUTION MANAGER"
   $HOME/voices-poc/scripts/run_scripts/pilot1/src/start-em-bg.sh

   sleep 5s
fi

if [[ $VOICES_START_CONSOLE == true ]]; then
   echo "STARTING TENA CONSOLE"
   /opt/TENA/Console-v2.0.1/start.sh -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -autoConnect &

   sleep 5s
fi

# change carla map if carla_
if ping -c 1 $VOICES_CARLA_CONTAINER &> /dev/null
then
    echo "CHANGING CARLA MAP TO: $carlaMapName"
	python3 $HOME/voices-poc/scripts/carla_python_scripts/config.py -m $carlaMapName --weather ClearNoon --host $VOICES_CARLA_CONTAINER

   sleep 5s
else
  echo "NO CARLA CONTAINER FOUND"
fi

if [[ $VOICES_START_CANARY == true ]]; then
   echo "STARTING TENA CANARY"
   /home/TENA/tenaCanary-v1.0.12/start.sh -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -auto &

   sleep 5s
fi

if [[ $VOICES_START_TDCS == true ]]; then
   echo "STARTING TENA DATA COLLECTION SYSTEM"
   mkdir $voicesPocPath/logs
   $tdcsPath/start.sh -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -dbFolder $voicesPocPath/logs &

   sleep 5s
fi


if [[ $VOICES_START_DATAVIEW == true ]]; then
   echo "STARTING TENA DATAVIEW"
   /opt/TENA/DataView-v1.5.4/start.sh &

   sleep 5s
fi

if [[ $VOICES_START_SCENARIO_PUBLISHER == true ]]; then
   echo "STARTING SCENARIO PUBLISHER"
   $HOME/voices-poc/scripts/run_scripts/pilot1/src/start-scenario-publisher.sh &

   sleep 5s
fi

if [[ $VOICES_START_TENA_CARLA_ADAPTER == true ]]; then
   echo "STARTING TENA CARLA ADAPTER"
   $HOME/voices-poc/scripts/run_scripts/pilot1/src/start-carla-tena-adapter.sh &

   sleep 5s
fi

if [[ $VOICES_START_MANUAL_CARLA_VEHICLE == true ]]; then
   echo "STARTING MANUAL CARLA VEHICLE"

   # if we are starting the carla adapter and a manual vehicle, we almost certainly are trying to use a vehicle from the scenario which should already be spawined
   if [[ $VOICES_START_TENA_CARLA_ADAPTER == true ]]; then
      echo "   CONNECTING TO SCENARIO MANUAL VEHICLE"
      python3 $HOME/voices-poc/scripts/carla_python_scripts/manual_control_keyboard_virtual.py --follow_vehicle $vehicleID --host $localAddress &

   else
      echo "   SPAWNING NEW MANUAL VEHICLE"
      python3 $HOME/voices-poc/scripts/carla_python_scripts/manual_control_keyboard.py --rolename $vehicleID --host $localAddress &

   fi

   sleep 5s
fi

tail -f /dev/null