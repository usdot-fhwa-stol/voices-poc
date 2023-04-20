#!/bin/bash

SIM_LOG=/home/carma/voices-poc/scripts/collect_logs/log_files/carma_sim_logs/voices_carla_carma_integration.log


docker run \
	   -it -d --rm \
       --name carla_carma_integration \
       --net=host \
       usdotfhwastol/carma-carla-integration:K900-test

echo "--------------exec----------------------"
docker exec \
       -it \
       carla_carma_integration \
       bash -c \
       "export PYTHONPATH=$PYTHONPATH:/home/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg && \
    	source /home/carma_carla_ws/devel/setup.bash && \
       roslaunch carma_carla_agent carma_carla_agent.launch spawn_point:="44.369656, 86.320465, 1, 0, 0, 263" town:="Town04" selected_route:="Voices_Pilot1_Test4_TFHRC-CAR-2" selected_plugins:="['RouteFollowingPlugin','InLaneCruisingPlugin','StopAndWaitPlugin','Pure Pursuit','CooperativeLaneChangePlugin']" synchronous_mode:=false speed_Kp:=0.4 speed_Ki:=0.03 speed_Kd:=0" &>> $SIM_LOG
