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

localCarlaAdapterPath=$HOME/tenadev/INSTALL/carlaadapter
VUG_LOCAL_TENA_PATH=$HOME/TENA

VUG_EM_ADDRESS='192.168.55.230'
VUG_EM_PORT='55100'

dockerInternalAddress='172.17.0.2'
VUG_LOCAL_ADDRESS='192.168.55.231'

carlaMap='Ubuntu_1222'

adapterVerbosity='1'

tenaPlatform='u1804-gcc75-64'
tenaVersion='6.0.7'

carlaDockerName='tena:carla'

sudo docker run -it --rm -p 56100:56100 -v $localCarlaAdapterPath:/home/CarlaAdapter -v $VUG_LOCAL_TENA_PATH:/home/TENA  $carlaDockerName bash -c "cd /home/CarlaAdapter/build/src; export TENA_PLATFORM=$tenaPlatform; export TENA_HOME=/home/TENA; export TENA_VERSION=$tenaVersion; export LD_LIBRARY_PATH=/home/TENA/lib; ./CarlaAdapter -emEndpoints $VUG_EM_ADDRESS:$VUG_EM_PORT -listenEndpoints $dockerInternalAddress:56100/hostname_in_ior=$VUG_LOCAL_ADDRESS -carlaHost $VUG_LOCAL_ADDRESS -verbosity $adapterVerbosity -mapPath '$carlaMap' -timeout 60000"


