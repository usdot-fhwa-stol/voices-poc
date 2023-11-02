#! /bin/bash

source /home/carla/start_scripts/setup-carla-docker.sh

carla_graphics_api_arg=""

if [[ $VUG_CARLA_GRAPHICS_API == "vulkan" ]]; then
   echo "SETTING CARLA GRAPHICS API TO VULKAN"
   carla_graphics_api_arg="-vulkan"

elif [[ $VUG_CARLA_GRAPHICS_API == "opengl" ]]; then
   echo "SETTING CARLA GRAPHICS API TO OPENGL"
   carla_graphics_api_arg="-opengl"
fi

carla_graphics_quality_arg=""

if [[ $VUG_CARLA_QUALITY_LEVEL == "Epic" ]]; then
   echo "CARLA GRAPHICS QUALITY SET TO EPIC"
   carla_graphics_quality_arg="-quality-level=Epic"

elif [[ $VUG_CARLA_QUALITY_LEVEL == "Low" ]]; then
   echo "CARLA GRAPHICS QUALITY SET TO LOW"
   carla_graphics_quality_arg="-quality-level=Low"
fi

echo "STARTING CARLA"
/bin/bash /home/carla/CarlaUE4.sh $carla_graphics_api_arg $carla_graphics_quality_arg -nosound &

sleep 5s

echo "VUG CARLA STARTUP COMLPETE"

tail -f /dev/null