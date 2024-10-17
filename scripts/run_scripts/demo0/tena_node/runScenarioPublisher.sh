#!/bin/bash

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

tenadevDir=$HOME/tenadev/INSTALL

VUG_SCENARIO_FILE=$HOME/voices-poc/scenario_files/demo0-scenario.xml

VUG_EM_ADDRESS='192.168.55.230'
VUG_EM_PORT='55100'

VUG_LOCAL_ADDRESS='192.168.55.230'

adapterVerbosity='4'

$tenadevDir/scenario-publisher/build/src/scenario-publisher -emEndpoints $VUG_EM_ADDRESS:$VUG_EM_PORT -listenEndpoints $VUG_LOCAL_ADDRESS -scenarioFile $VUG_SCENARIO_FILE -verbosity $adapterVerbosity
