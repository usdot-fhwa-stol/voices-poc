#! /bin/bash

export HOME=/home

env_set_site_config_path=$HOME/voices-poc/config/site_config/$VOICES_SITE_CONFIG

if [ ! -f $env_set_site_config_path ]; then
        echo "    [!!!] Site Config file not found: $VOICES_SITE_CONFIG"
else
        ln -sf $env_set_site_config_path $HOME/.voices_config
fi

voices_config=$HOME/.voices_config

if [ -L ${voices_config} ] ; then
   if [ -e ${voices_config} ] ; then
      config_link_dest=$(readlink -f $voices_config)
      link_base_name=$(basename ${config_link_dest})

      source $voices_config


      echo "Site Config: "$link_base_name
      echo "Scenario Config: "$scenario_config_file
   else
      echo "[!!!] .voices_config link is broken"
      exit 1
   fi
elif [ -e ${voices_config} ] ; then
   echo "[!!!] .voices_config file is not a symbolic link"
   exit 1
else
   echo "[!!!] .voices_config link is is missing"
   exit 1
fi

# overwrite VOI_CARLA_EGG_DIR as this is within the container

export VOI_CARLA_EGG_DIR=$HOME/CARLA_0.9.10/PythonAPI/carla/dist/

