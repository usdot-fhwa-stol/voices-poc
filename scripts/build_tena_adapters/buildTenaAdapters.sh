#!/bin/bash

##############################
#	TODO
# 	- make a general build container for most apps instead of using CARLA build container
# 
# 
# 


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
vugUdbProtocolioVersion="vug-udp-protocolio-2.2.1"


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
echo "    [1]  	carla-tena-adapter"
echo "    [2]  	v2xhub-tena-bsm-plugin"
echo "    [3]  	v2xhub-tena-spat-plugin"
echo "    [4]  	v2xhub-tena-mobility-plugin"
echo "    [5]  	v2xhub-tena-traffic-control-plugin"
echo "    [6]  	scenario-publisher"
echo "    [7]  	tena-entity-generator"
echo "    [8] 	carma-platform-tena-adapter"
echo "    [9] 	vug-threads"
echo "    [10] 	vug-udp-protocolio"
echo
read -p "--> " tenaAppIndex

carlaTenaAdapterGitUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/carla-tena-adapter.git"

if [[ $tenaAppIndex == 1 ]]; then
	tenaApp=carla-tena-adapter
	gitCloneUrl=$carlaTenaAdapterGitUrl
	dockerContainer=tena:carla
	remoteAppDir=/home/$tenaApp 			#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=false
	requiresProtocolio=false
	useMasterDefaultBranch=false
	
elif [[ $tenaAppIndex == 2 ]]; then
	tenaApp=v2xhub-tena-bsm-plugin
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/v2xhub-tena-bsm-plugin.git"
	dockerContainer=usdotfhwaops/v2xhubamd:7.3.1
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=true
	requiresProtocolio=false
	useMasterDefaultBranch=false

elif [[ $tenaAppIndex == 3 ]]; then
	tenaApp=v2xhub-tena-spat-plugin
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/v2xhub-tena-spat-plugin.git"
	dockerContainer=usdotfhwaops/v2xhubamd:7.3.1
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=true
	requiresProtocolio=false
	useMasterDefaultBranch=false
	
elif [[ $tenaAppIndex == 4 ]]; then
	tenaApp=v2xhub-tena-mobility-plugin
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/v2xhub-tena-mobility-plugin.git"
	dockerContainer=usdotfhwaops/v2xhubamd:7.3.1
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=true
	requiresProtocolio=false
	useMasterDefaultBranch=false
	
elif [[ $tenaAppIndex == 5 ]]; then
	tenaApp=v2xhub-tena-traffic-control-plugin
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/v2xhub-tena-traffic-control-plugin.git"
	dockerContainer=usdotfhwaops/v2xhubamd:7.3.1
	remoteAppDir=/home/V2X-Hub/src/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=true
	requiresProtocolio=false
	useMasterDefaultBranch=false

elif [[ $tenaAppIndex == 6 ]]; then
	tenaApp=scenario-publisher
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/scenario-publisher.git"
	dockerContainer=tena:carla
	remoteAppDir=/home/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=false
	requiresProtocolio=false
	useMasterDefaultBranch=false

elif [[ $tenaAppIndex == 7 ]]; then
	tenaApp=tena-entity-generator
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/tena-entity-generator.git"
	dockerContainer=tena:carla
	remoteAppDir=/home/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=false
	requiresProtocolio=false
	useMasterDefaultBranch=false
	
elif [[ $tenaAppIndex == 8 ]]; then
	tenaApp=carma-platform-tena-adapter
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/carma-platform-tena-adapter.git"
	dockerContainer=tena:carla
	remoteAppDir=/home/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=false
	requiresProtocolio=true
	useMasterDefaultBranch=false

elif [[ $tenaAppIndex == 9 ]]; then
	tenaApp=vug-threads
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/vug-threads.git"
	dockerContainer=tena:carla
	remoteAppDir=/home/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=false
	requiresProtocolio=false
	useMasterDefaultBranch=true
	
elif [[ $tenaAppIndex == 10 ]]; then
	tenaApp=vug-udp-protocolio
	gitCloneUrl="https://www.trmc.osd.mil/bitbucket/scm/vug/vug-udp-protocolio.git"
	dockerContainer=tena:carla
	remoteAppDir=/home/$tenaApp	#DO NOT CHANGE: internal docker directory mapped to localAppDir
	isV2xhubPlugin=false
	requiresProtocolio=false
	useMasterDefaultBranch=true

else
	echo "Invalid selection, try again..."
	exit
fi

localAppDir=$localTenadevDir/$tenaApp	#location of git directory of application to be built
			
downloadedSource=false

echo
if [[ ! -d $localAppDir ]]; then
	read -p "Application directory not found. Would you like to download from BitBucket? [y/n] " downloadApp
	
	if $useMasterDefaultBranch; then
		defaultBranch=master
	else
		defaultBranch=develop
	fi

	read -p "What branch would you like to use? [leave blank for $defaultBranch] " branchToDownload
	
	if [[ $downloadApp =~ ^[yY]$ ]]; then
	
		if [[ $branchToDownload == "" ]]; then
			git clone $gitCloneUrl -b $defaultBranch $localAppDir || exit
		else
			git clone $gitCloneUrl -b $branchToDownload $localAppDir || exit
		fi
	else
		echo "Please clone the latest application directory from BitBucket..."
	fi

	downloadedSource=true
else
	echo "$tenaApp directory found"
fi

cd $localAppDir

if ! $downloadedSource; then
	gitCommitId=$(git rev-parse HEAD)
	gitBranch=$(git rev-parse --abbrev-ref HEAD)
	gitInfo=$(git show $gitCommitId  | sed 's/^/    /' )
	gitInfo="$(echo $gitInfo | sed 's/diff .*//' )"

	echo
	echo Current Branch: $gitBranch
	echo
	read -p "Would you like to switch branches? [y/n] " switchBranch

	if [[ $switchBranch =~ ^[yY]$ ]]; then
		read -p "    Enter the desired branch name --> " newBranch

		git checkout $newBranch || exit
	fi

	echo
	echo "Current Commit Info:"
	echo
	echo "$gitInfo"

	echo
	read -p "Would you like to pull the latest code? [y/n] " pullLatest

	if [[ $pullLatest =~ ^[yY]$ ]]; then
		echo
		git pull || exit
	fi
fi

echo
echo "Would you like to build release or debug? [#]" 
echo 
echo "    [1]  	release"
echo "    [2]  	debug"
echo
read -p "--> " releaseOrDebug

if [[ $releaseOrDebug == 1 ]]; then
	buildVersion=release
	buildVersionCaps=RELEASE
	
elif [[ $releaseOrDebug == 2 ]]; then
	buildVersion=debug
	buildVersionCaps=DEBUG

else
	echo "Invalid selection, try again..."
	exit
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
if [ $tenaApp == "vug-threads" ] || [ -d $localInstallDir/$vugThreadsVersion ]; then
	echo "vug-threads found..."
else
	echo "vug-threads was not found. Please install vug-threads"
	exit
fi

#look for VUG ProtocolIO
if $requiresProtocolio; then
	if [ -d $localInstallDir/$vugUdbProtocolioVersion ]; then
		echo "ProtocolIO found..."
	else
		echo "vug-udp-protocolio was not found. Please install vug-udp-protocolio"
		exit
	fi
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
		echo "Build container $dockerContainer already exists, would you like to rebuild? [y/n] "
		echo 
		echo "[!!!] WARNING: THIS WILL DESTROY THE EXISTING BUILD CONTAINER AND REBUILD FROM SCRATCH"
		echo "                               THIS PROCESS CAN TAKE OVER 1 HOUR"
		echo
		read -p "    [y/n] --> " rebuildContainerYn

		if [[ $rebuildContainerYn =~ ^[yY]$ ]]; then
			echo
			read -p "    Are you sure you want to rebuild the docker container? [y/n] " rebuildContainerYnConfirm
			if [[ $rebuildContainerYnConfirm =~ ^[yY]$ ]]; then
				skipDocker=false
			else
				skipDocker=true
			fi
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
		sudo docker image rm -f $dockerContainer
		
		#if v2xhub plugin need to build image inside the V2X-Hub dir
		if $isV2xhubPlugin; then

			docker pull $dockerContainer
		fi

		#if we are vug-threads or protocolio
		if [ $dockerContainer == "tena:carla" ]; then
			if [ ! -d $localTenadevDir/carla-tena-adapter ]; then
				echo "This application uses the tena:carla build container from the carla-tena-adapter. Cloning carla-tena-adapter repository to use dockerfile"
			
				git clone $carlaTenaAdapterGitUrl -b develop $localTenadevDir/carla-tena-adapter || exit

			fi

			dockerfileToUse=$localTenadevDir/carla-tena-adapter/docker/Dockerfile
			echo
			echo "#### Starting Docker Build ####"
			sudo -E docker build --force-rm --rm -f $dockerfileToUse -t $dockerContainer .
		
		# removed to test using dockerhub image
		# else
			
		# 	dockerfileToUse=$localAppDir/docker/Dockerfile
		fi
				
		currentDockerImages=$(sudo docker image list -q $dockerContainer)

		if [[ -z $currentDockerImages ]]; then
			echo
			echo "[!!!] Container $dockerContainer not built, check logs for details..."
			exit
		fi

		echo "#### Docker Build Complete ####"
		
		# removed to test using dockerhub image
		# #if v2xhub plugin go out of the v2xhub directory and remove it
		# if $isV2xhubPlugin; then
		# 	cd ../
		# 	#changed to not remove v2xhub so we know what branch we used
		# 	#sudo rm -rf ./V2X-Hub
		# fi
fi


#-- Cmake example
#sudo docker run --rm -v /home/ejslattery/dev/carlaadapter:/home/CarlaAdapter -v /home/ejslattery/dev/tenadev/u1804-gcc75-64/TENA:/home/TENA tena:carla bash -c "cd /home/CarlaAdapter/build; export TENA_PLATFORM=u1804-gcc75-64; export TENA_HOME=/home/TENA; export TENA_VERSION=6.0.7; export CARLA_HOME=/home/carla; cmake -D CMAKE_EXPORT_COMPILE_COMMANDS=ON -D CMAKE_PREFIX_PATH=/home/TENA/lib/cmake -D BOOST_INCLUDEDIR=/home/TENA/TENA_boost_1.70.0.2_Library/u1804-gcc75-64/include -D VUG_INSTALL_DIR=/home/CarlaAdapter/INSTALL ../"
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
			echo Pulling mw library
			sudo git clone https://www.trmc.osd.mil/bitbucket/scm/vug/tena-cmake-package.git -b main cmake_temp || exit
			sudo mv cmake_temp/cmake/ $localTenaDir/lib/ || exit
			sudo rm -rf cmake_temp || exit
		fi

		echo
		
		if ! ( set -x ; sudo docker run --entrypoint /bin/bash --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir -v $localInstallDir:$remoteInstallDir $dockerContainer -c "cd $remoteAppDir/build; export TENA_PLATFORM=$tenaBuildVersion; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.8; export CARLA_HOME=$remoteCarlaDir; cmake -D CMAKE_EXPORT_COMPILE_COMMANDS=ON -B $buildVersion -D CMAKE_BUILD_TYPE=$buildVersionCaps -D CMAKE_PREFIX_PATH='$remoteTenaDir/lib/cmake;$remoteInstallDir' -D BOOST_INCLUDEDIR=$remoteTenaDir/$boostVersion/$tenaBuildVersion/include -D VUG_INSTALL_DIR=$remoteInstallDir ../" ); then
			echo
			echo "[!!!] CMAKE FAILED"
			exit
		fi

		echo
		echo "#### CMAKE Complete ####"

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
		if ! ( set -x ; sudo docker run --entrypoint /bin/bash --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir -v $localInstallDir:$remoteInstallDir $dockerContainer -c "cd $remoteAppDir/build/$buildVersion; export TENA_PLATFORM=$tenaBuildVersion; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.8; export CARLA_HOME=/home/carla; make VERBOSE=1" ); then
			echo
			echo "[!!!] MAKE FAILED"
			exit
		fi

		echo
		echo "#### Make Complete ####"

		if $isV2xhubPlugin
			then
		
				echo
				echo "#### Running Make Package ####"
				
				echo
				echo "MAKE PACKAGE COMMAND: "
				if ! ( set -x ; sudo docker run --entrypoint /bin/bash --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir -v $localInstallDir:$remoteInstallDir $dockerContainer -c "cd $remoteAppDir/build/$buildVersion; export TENA_PLATFORM=$tenaBuildVersion; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.8; export CARLA_HOME=/home/carla; make package VERBOSE=1" ); then
					echo
					echo "[!!!] MAKE PACKAGE FAILED"
					exit
				fi

				
				echo
				echo "#### Make Package Complete ####"
			else
			
				echo
				echo "#### Running Make Install ####"
				
				echo
				echo "MAKE INSTALL COMMAND: "
				if ! ( set -x ; sudo docker run --entrypoint /bin/bash --rm -v $localAppDir:$remoteAppDir -v $localTenaDir:$remoteTenaDir -v $localInstallDir:$remoteInstallDir $dockerContainer -c "cd $remoteAppDir/build/$buildVersion; export TENA_PLATFORM=$tenaBuildVersion; export TENA_HOME=$remoteTenaDir; export TENA_VERSION=6.0.8; export CARLA_HOME=/home/carla; make install VERBOSE=1" ); then
					echo
					echo "[!!!] MAKE INSTALL FAILED"
					exit
				fi

				echo
				echo "#### Make Install Complete ####"
		fi
fi

echo
echo
echo "#### Build Script Complete ####"
echo

