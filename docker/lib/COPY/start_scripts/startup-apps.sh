#! /bin/bash

source /home/start_scripts/setup-docker.sh


sleep 5s

if [[ $VUG_START_EM == true ]]; then
   echo "STARTING TENA EXECUTION MANAGER"
   $HOME/voices-poc/scripts/run_scripts/pilot1/src/start-em-bg.sh

   sleep 5s
fi

if [[ $VUG_START_CONSOLE == true ]]; then
   echo "STARTING TENA CONSOLE"
   /opt/TENA/Console-v2.0.1/start.sh -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -autoConnect &

   sleep 5s
fi

# try to change carla map 
{
   echo "CHANGING CARLA MAP TO: $carlaMapName"
	python3 $HOME/voices-poc/scripts/carla_python_scripts/config.py -m $carlaMapName --weather ClearNoon --host $carlaAddress &

   sleep 5s

   # blank signals
   python3 $HOME/voices-poc/scripts/carla_python_scripts/blank_traffic_signals.py & 

   # set spectator view
   python3 $HOME/voices-poc/scripts/carla_python_scripts/spectator_view_mcity.py &

   sleep 5s


} || {
   echo "NO CARLA CONTAINER FOUND"

}

if [[ $VUG_START_SUMO == true ]]; then
   echo "STARTING SUMO"
   cd $HOME/voices-poc/scripts/carla_python_scripts/Sumo/
   python3 $HOME/voices-poc/scripts/carla_python_scripts/Sumo/run_synchronization.py $HOME/voices-poc/scripts/carla_python_scripts/Sumo/$VUG_SUMO_CONFIG --sumo-gui --tls-manager carla &
   cd $HOME
   sleep 5s
fi

if [[ $VUG_START_CANARY == true ]]; then
   echo "STARTING TENA CANARY"
   /home/TENA/tenaCanary-v1.0.12/start.sh -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -auto &

   sleep 5s
fi

if [[ $VUG_START_TDCS == true ]]; then
   echo "STARTING TENA DATA COLLECTION SYSTEM"
   $HOME/voices-poc/scripts/run_scripts/pilot1/src/start-tdcs.sh &
   
   sleep 5s
fi


if [[ $VUG_START_DATAVIEW == true ]]; then
   echo "STARTING TENA DATAVIEW"
   /opt/TENA/DataView-v1.5.4/start.sh &

   sleep 5s
fi

if [[ $VUG_START_SCENARIO_PUBLISHER == true ]]; then
   echo "STARTING SCENARIO PUBLISHER"
   $HOME/voices-poc/scripts/run_scripts/pilot1/src/start-scenario-publisher.sh &

   sleep 5s
fi

if [[ $VUG_START_TENA_CARLA_ADAPTER == true ]]; then
   echo "STARTING TENA CARLA ADAPTER"
   $HOME/voices-poc/scripts/run_scripts/pilot1/src/start-carla-tena-adapter.sh &

   sleep 5s
fi

if [[ $VUG_START_TJ2735_ADAPTER == true ]]; then
   echo "STARTING TENA J2735 ADAPTER"
   $HOME/voices-poc/scripts/run_scripts/pilot1/src/start-tj2735-message-adapter.sh &

   sleep 5s
fi

if [[ $VUG_START_TRAFFIC_LIGHT_EG == true ]]; then
   echo "STARTING TENA TRAFFIC LIGHT ENTITY GENERATOR"
   $HOME/voices-poc/scripts/run_scripts/pilot1/src/start-traffic-light-entity-generator.sh &

   sleep 5s
fi

if [[ $VUG_START_MANUAL_CARLA_VEHICLE == true ]]; then
   echo "STARTING MANUAL CARLA VEHICLE"

   # if we are starting the carla adapter and a manual vehicle, we almost certainly are trying to use a vehicle from the scenario which should already be spawined
   if [[ $VUG_MANUAL_CARLA_VEHICLE_IS_NEW == true ]]; then
      echo "   SPAWNING NEW MANUAL VEHICLE"
      python3 $HOME/voices-poc/scripts/carla_python_scripts/manual_control_keyboard.py --rolename $vehicleID --host $localAddress &

   else
      echo "   CONNECTING TO SCENARIO MANUAL VEHICLE"
      python3 $HOME/voices-poc/scripts/carla_python_scripts/manual_control_keyboard_virtual.py --follow_vehicle $vehicleID --host $localAddress &

   fi

   sleep 5s
fi

echo
echo "VUG STARTUP COMLPETE"

tail -f /dev/null