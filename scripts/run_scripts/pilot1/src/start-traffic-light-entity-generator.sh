#/bin/bash

#  *
#  * Copyright (C) 2022 LEIDOS.
#  *
#  * Licensed under the Apache License, Version 2.0 (the "License"); you may not
#  * use this file except in compliance with the License. You may obtain a copy o\
# f
#  * the License at
#  *
#  * http://www.apache.org/licenses/LICENSE-2.0
#  *
#  * Unless required by applicable law or agreed to in writing, software
#  * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  * License for the specific language governing permissions and limitations under
#  * the License.
#  *


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

if [[ $? -ne 0 ]] ; then
    echo
    echo "[!!!] .config file not found, please run the start script from its containing folder"
    echo
    exit 1
fi

localadapterPath=$VUG_LOCAL_INSTALL_PATH/$VUG_TRAFFIC_LIGHT_ENTITY_GENERATOR_VERSION

adapterVerbosity='1'

mkdir -p $VUG_ADAPTER_LOG_PATH

adapterLogFile=$VUG_ADAPTER_LOG_PATH/traffic_light_entity_generator_terminal_out.log

echo "<< ***** Adapter Started **** >>" > $adapterLogFile
date >> $adapterLogFile

# open a new file descriptor for logging
exec 4>> $adapterLogFile

# redirect trace logs to fd 4
BASH_XTRACEFD=4

set -x

$localadapterPath/bin/tena-traffic-light-entity-generator -emEndpoints $VUG_EM_ADDRESS:$VUG_EM_PORT -listenEndpoints $VUG_LOCAL_ADDRESS -intersectionID $VUG_INTERSECTION_ID -verbosity $adapterVerbosity | tee -a $adapterLogFile

