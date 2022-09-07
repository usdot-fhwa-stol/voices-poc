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

. ../node_info.config

if [[ $? -ne 0 ]] ; then
    echo
    echo "[!!!] .config file not found, please run the start script from its containing folder"
    echo
    exit 1
fi

localCarlaAdapterPath=$localInstallPath/$carlaAdapterVersion

carlaHost=$localAddress

adapterVerbosity='4'
 
mkdir -p $localAdapterLogPath

adapterLogFile=$localAdapterLogPath/carla_adapter_terminal_out.log

echo "<< ***** Adapter Started **** >>" > $adapterLogFile
date >> $adapterLogFile

# open a new file descriptor for logging
exec 4>> $adapterLogFile

# redirect trace logs to fd 4
BASH_XTRACEFD=4

set -x

$localCarlaAdapterPath/bin/CARLAtenaAdapter -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -carlaHost $carlaHost -simId $simId -verbosity $adapterVerbosity 2>&1 | tee -a $adapterLogFile
