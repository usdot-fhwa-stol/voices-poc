#! /bin/bash

env_set_site_config_path=/home/carla/voices-poc/config/site_config/$VUG_SITE_CONFIG_FILE

# the .voices_config setup is as follows in order to make existing scripts work within docker container: 
# 
# $HOME/.voices_config_link = actual site config link
# 
# 
# .voices_config_docker = source $HOME/.voices_config_link + overwrite vars pertaining to locations within docker container
# 
# therefore:
# 
# $HOME/.voices_config --> $HOME/.voices_config_docker = source $HOME/.voices_config_link + overwrites
# 
# $HOME/.voices_config_docker exists because $HOME/.voices_config must be a sym link for run_scripts
# 

if [ ! -f $env_set_site_config_path ]; then
        echo "    [!!!] Site Config file not found: $VUG_SITE_CONFIG_FILE"
        exit 1
else
        ln -sf $env_set_site_config_path $HOME/.voices_config_link
        ln -sf $HOME/.voices_config_docker $HOME/.voices_config
fi

voices_config=$HOME/.voices_config_link
voices_config_base=$HOME/.voices_config

if [ -L ${voices_config} ] ; then
   if [ -e ${voices_config} ] ; then
      config_link_dest=$(readlink -f $voices_config)
      link_base_name=$(basename ${config_link_dest})

      source $voices_config_base


      echo "Site Config: "$link_base_name
      echo "Scenario Config: "$VUG_SCENARIO_CONFIG_FILE
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

