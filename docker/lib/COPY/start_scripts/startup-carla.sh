#! /bin/bash

source /home/carla/start_scripts/setup-carla-docker.sh




echo "STARTING CARLA"
/bin/bash /home/carla/CarlaUE4.sh -vulkan -nosound &

sleep 5s

echo "VUG CARLA STARTUP COMLPETE"

tail -f /dev/null