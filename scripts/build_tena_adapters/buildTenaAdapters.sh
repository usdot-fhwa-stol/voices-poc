#!/bin/bash

##############################
#	TODO
# add download and build of VUG Threads
#
# ask if you want to do a git pull? 
#	will have to check its on the correct branch 



username=$(whoami)

#-------------------| LOCAL VARIABLES |-------------------#
localTenaDir=/home/$username/TENA 				#root directory of TENA installation
localTenaPackageDownloadDir=/home/$username/Downloads/TENA	#location of the TENA dependency packages
localTenadevDir=/home/$username/tenadev			#location of local tenadev
localInstallDir=$localTenadevDir/INSTALL		#location to install/build TENA adapters
#---------------------------------------------------------#

#-------------------| TENA VARIABLES |-------------------#
tenaVersion=6.0.8
tenaBuildVersion=u2004-gcc9-64
tenaSourceScript=$localTenaDir/$tenaVersion/scripts/tenaenv-$tenaBuildVersion-v$tenaVersion.sh
#--------------------------------------------------------#


#-------------------| REMOTE VARIABLES |-------------------#
#-------------------|  DO NOT CHANGE   |-------------------#
remoteDownloadsDir=/home/Downloads 		#DO NOT CHANGE: internal docker directory mapped to localTenaPackageDownloadDir
remoteTenaDir=/home/TENA			#DO NOT CHANGE: internal docker directory mapped to localTenaDir
remoteInstallDir=/home/INSTALL		#DO NOT CHANGE: internal docker directory mapped to localInstallDir	
remoteCarlaDir=/home/carla
#--------------------------------------------------------#

middlewareVersion="MiddlewareSDK-v6.0.8"
boostVersion="TENA_boost_1.77.0.1_Library"
vugCombinedVersion="VUG-VOICES-Combined-v0.12.0"
vugThreadsVersion="vug-threads-2.2.0"


v2xhubGitUrl="https://github.com/usdot-fhwa-OPS/V2X-Hub.git"

skipDocker=false
skipCmake=false
skipMake=false



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
echo "[1] carla-tena-adapter"
echo "[2] v2xhub-tena-bsm-plugin"
echo "[3] v2xhub-tena-spat-plugin"
echo "[4] v2xhub-tena-mobility-plugin"
echo "[5] v2xhub-tena-traffic-control-plugin"
echo
read -p "--> " tenaAppIndex

if [[ $tenaAppIndex == 1 ]]; then
	tenaApp=carla-tena-adapter
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/carla-tena-adapter.git"
	dockerContainer=tena:carla
	remoteAppDir=/home/$tenaApp 			#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=false
	
elif [[ $tenaAppIndex == 2 ]]; then
	tenaApp=v2xhub-tena-bsm-plugin
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/v2xhub-tena-bsm-plugin.git"
	dockerContainer=tena:v2xhub
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=true
	
elif [[ $tenaAppIndex == 3 ]]; then
	tenaApp=v2xhub-tena-spat-plugin
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/v2xhub-tena-spat-plugin.git"
	dockerContainer=tena:v2xhub
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=true
	
elif [[ $tenaAppIndex == 4 ]]; then
	tenaApp=v2xhub-tena-mobility-plugin
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/v2xhub-tena-mobility-plugin.git"
	dockerContainer=tena:v2xhub
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=true
	
elif [[ $tenaAppIndex == 5 ]]; then
	tenaApp=v2xhub-tena-traffic-control-plugin
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/v2xhub-tena-traffic-control-plugin.git"
	dockerContainer=tena:v2xhub
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=true

else
	echo "Invalid selection, try again..."
	exit
fi

localAppDir=$localTenadevDir/$tenaApp	#location of git directory of application to be built
			

echo
if [[ ! -d $localAppDir ]]; then
	read -p "Application directory not found. Would you like to download from BitBucket? [y/n] " downloadApp
	
	read -p "What branch would you like to use? [leave blank for develop] " branchToDownload
	
	if [[ $downloadApp =~ ^[yY]$ ]]; then
	
		if [[ $branchToDownload == "" ]]; then
			git clone $gitCloneUrl -b develop $localAppDir
		else
			git clone $gitCloneUrl -b $branchToDownload $localAppDir
		fi
	else
		echo "Please clone the latest application directory from BitBucket..."
	fi
else
	echo "$tenaApp directory found"
fi


##### Look for required packages to be isntalled

echo
echo "The looking for packages to be installed:"
echo


# look for middleware
if [ -d $localTenaDir/$tenaVersion ]; then
	echo "TENA Middleware $tenaVersion found..."
else
	echo "The proper TENA Middleware version was not found. Please install version $tenaVersion"
	exit
fi

#look for boost
if [ -d $localTenaDir/$boostVersion* ]; then
	echo "$boostVersion found..."
else
	echo "The proper Boost version was not found. Please install version $boostVersion"
	exit
fi

#look for VUG Combined
if [ -d $localTenaDir/$tenaVersion/src/$vugCombinedVersion* ]; then
	echo "$vugCombinedVersion found..."
else
	echo "The proper VUG-Combined was not found. Please install version $vugCombinedVersion"
	exit
fi

#look for VUG Threads
if [ -d $localInstallDir/$vugThreadsVersion ]; then
	echo "$vugThreadsVersion found..."
else
	echo "The proper VUG-Threads was not found. Please install version $vugThreadsVersion"
	exit
fi

for arg in "$@"; do
	case $arg in
		"-d")
			skipDocker=true;;
		"-c")
			skipMake=true;;
	esac
done



if [[ $skipDocker == false ]] ; then
	
	currentDockerImages=$(sudo docker image list -q $dockerContainer)
	
	if [[ -n $currentDockerImages ]] ; then
	
		echo
		read -p "Container $dockerContainer already exists, would you like to rebuild? [y/n] " rebuildContainerYn
		if [[ $rebuildContainerYn =~ ^[yY]$ ]]; then
			skipDocker=false
		else
			skipDocker=true
		fi
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
		
		#if v2xhub plugin need to build image inside the V2X-Hub dir
		if [ isV2xhubPlugin ]; then
			
			#if the v2xhub directory doesnt exist, download it
			if [[ ! -d ./V2X-Hub ]]; then
				
				echo
				read -p "V2X-Hub directory not found. Would you like to download from GitHub? [y/n] " downloadApp
				read -p "What branch would you like to use? [leave blank for develop] " branchToDownload

				if [[ $downloadApp =~ ^[yY]$ ]]; then
					if [[ $branchToDownload == "" ]]; then
						git clone $v2xhubGitUrl -b develop 
					else
						git clone $v2xhubGitUrl -b $branchToDownload 
					fi
				else
					echo "Please clone the latest V2X-Hub directory from Github..."
					exit
				fi
			else
				echo "V2X-Hub directory found"
			fi
			
			cd ./V2X-Hub
		fi
				
		echo
		echo "#### Starting Docker Build ####"
		sudo -E docker build --force-rm --rm -f $localAppDir/docker/Dockerfile -t $dockerContainer .
		
		
		
		currentDockerImages=$(sudo docker image list -q $dockerContainer)

		if [[ -z $currentDockerImages ]]; then
			echo
			echo "[!!!] Container $dockerContainer not built, check logs for details..."
			exit
		fi
		
		#if v2xhub plugin go out of the v2xhub directory and remove it
		if [ isV2xhubPlugin ]; then
			cd ../
			sudo rm -rf ./V2X-Hub
		fi
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
		#ls $localTenaDir/lib/cmake
		if [[ ! -d $localTenaDir/lib/cmake/mw ]]; then
			echo
			echo mw library not installed in local TENA install $localTenaDir/lib/cmake/mw
			echo Please add the mw library and try again...; exit
		fi

		echo
		
		( set -x ; sudo docker run --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir -v $localInstallDir:$remoteInstallDir $dockerContainer bash -c "cd $remoteAppDir/build; export TENA_PLATFORM=$tenaBuildVersion; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.8; export CARLA_HOME=$remoteCarlaDir; cmake -D CMAKE_EXPORT_COMPILE_COMMANDS=ON -D CMAKE_INSTALL_PREFIX=$remoteAppDir/$tenaApp -D CMAKE_PREFIX_PATH='$remoteTenaDir/lib/cmake;$remoteInstallDir' -D BOOST_INCLUDEDIR=$remoteTenaDir/$boostVersion/$tenaBuildVersion/include -D VUG_INSTALL_DIR=$remoteInstallDir/$tenaApp ../" )
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
		echo
		( set -x ; sudo docker run --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir -v $localInstallDir:$remoteInstallDir $dockerContainer bash -c "cd $remoteAppDir/build; export TENA_PLATFORM=$tenaBuildVersion; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.8; export CARLA_HOME=/home/carla; make VERBOSE=1" )
		
		if [ isV2xhubPlugin ]; then
		
			echo
			echo "#### Running Make Install ####"
			
			echo
			echo "MAKE INSTALL COMMAND: "
			( set -x ; sudo docker run --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir -v $localInstallDir:$remoteInstallDir $dockerContainer bash -c "cd $remoteAppDir/build; export TENA_PLATFORM=$tenaBuildVersion; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.8; export CARLA_HOME=/home/carla; make install VERBOSE=1" )
		fi
fi
