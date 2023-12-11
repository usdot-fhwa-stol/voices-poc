#!/bin/bash

# Start Execution Manager

voices_config=~/.voices_config

if [ -L ${voices_config} ] ; then
   if [ -e ${voices_config} ] ; then
      config_link_dest=$(readlink -f $voices_config)
      link_base_name=$(basename ${config_link_dest})

      . $voices_config


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

$VUG_EM_PATH/bin/executionManager \
    -listenendpoints $VUG_EM_ADDRESS:$VUG_EM_PORT \
    -logDir $VUG_EM_PATH/log \
    -recoveryDir $VUG_EM_PATH/save \
    -connectionTimeoutInMilliseconds 10000 -twowayTimeoutInMilliseconds 20000 \
    -transientCommunicationAttempts 3 -disconnectTimeoutInMilliseconds 5000 \
    -quiet -nonInteractive &
