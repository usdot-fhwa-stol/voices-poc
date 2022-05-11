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

username=$(whoami)

#-------------------| LOCAL VARIABLES |-------------------#
localTenaDir=/home/$username/TENA 				#root directory of TENA installation
localTenaPackageDownloadDir=/home/$username/Downloads/TENA	#location of the TENA dependency packages
localInstallDir=/home/$username/tenadev/INSTALL		#location to install/build TENA adapters
#---------------------------------------------------------#

#-------------------| TENA VARIABLES |-------------------#
tenaVersion=6.0.7
tenaBuildVersion=u1804-gcc75-64
tenaSourceScript=$localTenaDir/$tenaVersion/scripts/tenaenv-$tenaBuildVersion-v$tenaVersion.sh
#--------------------------------------------------------#
/*                                                                              
 * Copyright (C) 2019-2021 LEIDOS.                                              
 *                                                                              
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not  
 * use this file except in compliance with the License. You may obtain a copy o\
f                                                                               
 * the License at                                                               
 *                                                                              
 * http://www.apache.org/licenses/LICENSE-2.0                                   
 *                                                                              
 * Unless required by applicable law or agreed to in writing, software          
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT    
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the     
 * License for the specific language governing permissions and limitations unde\
r                                                                               
 * the License.                                                                 
 */

#-------------------| REMOTE VARIABLES |-------------------#
#-------------------|  DO NOT CHANGE   |-------------------#
remoteDownloadsDir=/home/Downloads 		#DO NOT CHANGE: internal docker directory mapped to localTenaPackageDownloadDir
remoteTenaDir=/home/TENA			#DO NOT CHANGE: internal docker directory mapped to localTenaDir
#--------------------------------------------------------#

v2xhubGitUrl="https://github.com/usdot-fhwa-OPS/V2X-Hub.git"

skipMake=false
skipCmake=false
skipDocker=false


if [[ -f $tenaSourceScript ]]; then
	source $tenaSourceScript
else
	echo
	echo "TENA Source script not found..."
	exit
fi


echo
echo "What application would you like to install? [#]" 
echo 
echo "[1] carlaadapter"
echo "[2] tenav2xhubgateway"
echo "[3] tenaspatplugin"
echo
read -p "--> " tenaAppIndex

if [[ $tenaAppIndex == 1 ]]; then
	tenaApp=carlaadapter
	toInstall=("MiddlewareSDK-v6.0.7" "boost-v1.70.0.2" "VUG-Scenario-Distribution-v0.3.0" "VUG-Vehicle-Distribution-v0.4.0" "VUG-TrafficLight-Distribution-v0.2.0" "TENA-Geospatial-Waypoint-Distribution-v1.0.0")
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/carlaadapter.git"
	dockerContainer=tena:carla
	remoteAppDir=/home/$tenaApp 			#DO NOT CHANGE: internal docker directory mapped to localAppDir
elif [[ $tenaAppIndex == 2 ]]; then
	tenaApp=tenav2xhubgateway
	toInstall=("MiddlewareSDK-v6.0.7" "boost-v1.70.0.2" "VUG-Scenario-Distribution-v0.3.0" "VUG-Vehicle-Distribution-v0.4.0" )
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/tenav2xhubgateway.git"
	dockerContainer=tena:v2xhub
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	
elif [[ $tenaAppIndex == 3 ]]; then
	tenaApp=tenaspatplugin
	toInstall=("MiddlewareSDK-v6.0.7" "boost-v1.70.0.2" "VUG-Scenario-Distribution-v0.3.0" "VUG-Vehicle-Distribution-v0.4.0" )
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/tenaspatplugin.git"
	dockerContainer=tena:v2xhub
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
else
	echo "Invalid selection, try again..."
	exit
fi

localAppDir=$localInstallDir/$tenaApp	#location of git directory of application to be built
			

echo
if [[ ! -d $localAppDir ]]; then
	read -p "Application directory not found. Would you like to download from BitBucket? [y/n] " downloadApp
	
	if [[ $downloadApp =~ ^[yY]$ ]]; then
		git clone $gitCloneUrl $localAppDir
	else
		echo "Please clone the latest application directory from BitBucket..."
	fi
else
	echo "$tenaApp directory found"
fi

echo
if ([[ $tenaApp == "tenav2xhubgateway" ]] || [[ $tenaApp == "tenaspatplugin" ]] ) && [[ ! -d $localInstallDir/V2X-Hub ]]; then
	read -p "V2X-Hub directory not found. Would you like to download from GitHub? [y/n] " downloadApp
	
	if [[ $downloadApp =~ ^[yY]$ ]]; then
		git clone $v2xhubGitUrl
	else
		echo "Please clone the latest V2X-Hub directory from Github..."
	fi
else
	echo "V2X-Hub directory found"
fi



availableInstallers=($localTenaPackageDownloadDir/*.bin)

echo
echo "The looking for packages to be installed:"
echo


allPackagesFound=true

for f in "${toInstall[@]}"; do
	packageFound=false
	for i in "${availableInstallers[@]}"; do
		if grep -q "$f" <<<"$i"; then
			echo "Package $f found..."
			packageFound=true
		fi
	done
	if [[ $packageFound == false ]]; then
		allPackagesFound=false
		echo "[!!!] Package $f not found..."
	fi
done

if  [[ $allPackagesFound == false ]]; then
	echo
	echo "Not all packages found, exiting..." 
	exit
fi

for arg in "$@"; do
	case $arg in
		"-d")
			skipDocker=true;;
		"-c")
			skipCmake=true;;
		"-m")
			skipMake=true;;
	esac
done

currentDockerImages=$(sudo docker image list -q $dockerContainer)
rebuildContainer=true

if [[ $skipDocker == false ]] && [[ -n $currentDockerImages ]]; then
	echo
	read -p "Container $dockerContainer already exists, would you like to rebuild? [y/n] " rebuildContainerYn
	if [[ $rebuildContainerYn =~ ^[yY]$ ]]; then
		skipDocker=false
	else
		skipDocker=true
	fi
fi

if [[ "$skipDocker" == true ]]
	then
		echo
		echo "#### Skipping Docker Container Build ####"
	else
		echo
		echo "#### Docker Container Build ####"
		
		sudo docker rm -v $dockerContainer 
		sudo docker image rm $dockerContainer
				
		sudo docker build --force-rm --rm -f $localAppDir/docker/Dockerfile -t $dockerContainer .
		
		
		currentDockerImages=$(sudo docker image list -q $dockerContainer)

		if [[ -z $currentDockerImages ]]; then
			echo
			echo "[!!!] Container $dockerContainer not built, check logs for details..."
			exit
		fi
		
		echo
		echo "#### TENA Components Install ####"
		for f in "${availableInstallers[@]}"; do
			for i in "${toInstall[@]}"; do
				if grep -q "$i" <<<"$f"; then
					sudo docker run --rm -v $localTenaPackageDownloadDir:$remoteDownloadsDir -v $localTenaDir:$remoteTenaDir $dockerContainer $remoteDownloadsDir/$(basename $f) -i /home --auto
				fi
			done
		done
fi


#-- Cmake example
#sudo docker run --rm -v /home/ejslattery/dev/carlaadapter:/home/CarlaAdapter -v /home/ejslattery/dev/tenadev/u1804-gcc75-64/TENA:/home/TENA tena:carla bash -c "cd /home/CarlaAdapter/build; export TENA_PLATFORM=u1804-gcc75-64; export TENA_HOME=/home/TENA; export TENA_VERSION=6.0.7; export CARLA_HOME=/home/carla; cmake -D CMAKE_EXPORT_COMPILE_COMMANDS=ON -D CMAKE_INSTALL_PREFIX=/home/CarlaAdapter/INSTALL -D CMAKE_PREFIX_PATH=/home/TENA/lib/cmake -D BOOST_INCLUDEDIR=/home/TENA/TENA_boost_1.70.0.2_Library/u1804-gcc75-64/include -D VUG_INSTALL_DIR=/home/CarlaAdapter/INSTALL ../"
#-- Cmake

if [[ ! -d $localAppDir/build ]]; then
	mkdir $localAppDir/build
else
	echo
	read -p "Existing build folder found, would you like to regenerate makefiles? [y/n] " regenerateMakefiles
	if [[ $regenerateMakefiles =~ ^[yY]$ ]]; then
		skipCmake=false
		sudo rm -rf $localAppDir/build
		mkdir $localAppDir/build
		
	else
		skipCmake=true
	fi
	
fi

if [[ "$skipCmake" == true ]]
	then
		echo
		echo "#### Skipping CMAKE ####"
	else
		echo
		echo "#### Running CMAKE ####"
		
		
		#check for mw library
		ls $localTenaDir/lib/cmake
		if [[ ! -d $localTenaDir/lib/cmake/mw ]]; then
			echo
			echo mw library not installed in local TENA install $localTenaDir/lib/cmake/mw
			echo Please add the mw library and try again...; exit
		fi
		
		
		echo "CMAKE COMMAND: "
		echo docker run --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir $dockerContainer bash -c "cd $remoteAppDir/build; export TENA_PLATFORM=u1804-gcc75-64; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.7; export CARLA_HOME=/home/carla; cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_INSTALL_PREFIX=$remoteAppDir/INSTALL -DCMAKE_PREFIX_PATH=$remoteTenaDir/lib/cmake -D BOOST_INCLUDEDIR=$remoteTenaDir/TENA_boost_1.70.0.2_Library/u1804-gcc75-64/include -D VUG_INSTALL_DIR=$remoteAppDir/INSTALL ../"
		echo
		
		sudo docker run --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir $dockerContainer bash -c "cd $remoteAppDir/build; export TENA_PLATFORM=u1804-gcc75-64; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.7; export CARLA_HOME=/home/carla; cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_INSTALL_PREFIX=$remoteAppDir/INSTALL -DCMAKE_PREFIX_PATH=$remoteTenaDir/lib/cmake -D BOOST_INCLUDEDIR=$remoteTenaDir/TENA_boost_1.70.0.2_Library/u1804-gcc75-64/include -D VUG_INSTALL_DIR=$remoteAppDir/INSTALL ../"
fi

#--Make example
#sudo docker run --rm -v /home/ejslattery/dev/carlaadapter:/home/CarlaAdapter -v /home/ejslattery/dev/tenadev/u1804-gcc75-64/TENA:/home/TENA tena:carla bash -c "cd /home/CarlaAdapter/build; export TENA_PLATFORM=u1804-gcc75-64; export TENA_HOME=/home/TENA; export TENA_VERSION=6.0.7; export CARLA_HOME=/home/carla; make VERBOSE=1"

#-- make
if [[ "$skipMake" == true ]]
	then
		echo
		echo "#### Skipping Make ####"
	else
		echo
		echo "#### Running Make ####"
		
		echo
		echo "MAKE COMMAND: "
		echo docker run --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir $dockerContainer bash -c "cd $remoteAppDir/build; export TENA_PLATFORM=u1804-gcc75-64; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.7; export CARLA_HOME=/home/carla; make VERBOSE=1"
		echo
		sudo docker run --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir $dockerContainer bash -c "cd $remoteAppDir/build; export TENA_PLATFORM=u1804-gcc75-64; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.7; export CARLA_HOME=/home/carla; make VERBOSE=1"
fi
