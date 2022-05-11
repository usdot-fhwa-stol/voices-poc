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

echo
echo "Checking for SpatPlugin_West.zip"

eastLs=$(sudo docker exec -it v2xhub ls -1 /home/V2X-Hub/src/v2i-hub | grep SpatPlugin_West.zip)
#echo $eastLs

echo
if [[ -z $eastLs ]]; then
	echo "SpatPlugin_West.zip does not exist, copying to v2xhub and installing..."
	sudo docker cp SpatPlugin_West.zip v2xhub:/home/V2X-Hub/src/v2i-hub
	sudo docker exec -it -w '/home/V2X-Hub/src/v2i-hub/' v2xhub tmxctl --plugin-install SpatPlugin_West.zip
else
	echo "SpatPlugin_West.zip exists..."
fi

echo
echo "Checking for SpatPlugin_East.zip"

eastLs=$(sudo docker exec -it v2xhub ls -1 /home/V2X-Hub/src/v2i-hub | grep SpatPlugin_East.zip)
#echo $eastLs

echo
if [[ -z $eastLs ]]; then
        echo "SpatPlugin_East.zip does not exist, copying to v2xhub and installing..."
        sudo docker cp SpatPlugin_East.zip v2xhub:/home/V2X-Hub/src/v2i-hub
        sudo docker exec -it -w '/home/V2X-Hub/src/v2i-hub/' v2xhub tmxctl --plugin-install SpatPlugin_East.zip
else
        echo "SpatPlugin_East.zip exists..."
fi
