#!/bin/bash

. ../run_scripts/demo1/node_info.config

echo
read -p "Is this a live vehicle? [y/n] " is_live_vehicle

if [[ $is_live_vehicle =~ ^[yY]$ ]]; then
    obu_interface_name=$(ifconfig | grep -B1 "192.168.88.100" | head -n 1 | sed 's/:.*//')
    
    tcpdump_carma_platorm_out="sudo tcpdump -i $obu_interface_name dst 192.168.88.40 and port 1516 -w carma_platform_out.pcap"
    tcpdump_carma_platorm_in="sudo tcpdump -i $obu_interface_name src 192.168.88.40 and port 5398 -w carma_platform_in.pcap"
else
    tcpdump_carma_platorm_out="sudo tcpdump -i lo port 56700 -w carma_platform_out.pcap"
    tcpdump_carma_platorm_in="sudo tcpdump -i lo port 5398 -w carma_platform_in.pcap"
fi


echo
echo "What vehicle position are you? [#]" 
echo 
echo "    [1]  	lead vehicle"
echo "    [2]  	second vehicle"
echo "    [3]  	third vehicle"

echo
read -p "--> " positionIndex


if [[ $positionIndex == 1 ]]; then
    vehicle_position='lead_vehicle'
elif [[ $positionIndex == 2 ]]; then
    vehicle_position='second_vehicle'
elif [[ $positionIndex == 3 ]]; then
    vehicle_position='third_vehicle'
else
	echo "Invalid selection, try again..."
	exit
fi

timestamp=$(date -d "today" +"%Y%m%d%H%M%S")

logs_folder_name=$vehicle_position'_'$timestamp

echo
echo "Folder Name: "$logs_folder_name

mkdir -p ./log_files/$logs_folder_name
cd ./log_files/$logs_folder_name

echo
    read -p "Would you like to collect the TENA SDO data? [y/n] " save_tdcs_data

	if [[ $save_tdcs_data =~ ^[yY]$ ]]; then
        echo
        echo "Starting TDCS" 
        tdcs_command="$tdcsPath/start.sh -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -databaseName $logs_folder_name.sqlite -dbFolder ."
        echo $tdcs_command
        $tdcs_command &
    fi


trap copyCarmaLogs SIGINT

copyCarmaLogs()
{
    echo
    echo "tcpdumps stopped"
    echo
    echo "ENSURE CARMA PLATFORM, CARLA, AND ALL ADAPTERS ARE STOPPED"
    read -p "--> To continue, press [ENTER] " enter_press
    
    echo
    echo "Copying carma logs"
    latest_logs=$(readlink -f /opt/carma/logs/latest)
    cp -r $latest_logs .
    
    echo "Copying adapter logs"
    mv $localAdapterLogPath/*.log .

    echo "Copying carma simulation logs"    
    mv $localCarmaSimLogPath/*.log .
    
    echo
    read -p "Would you like to save the CARMA Platform rosbag? [y/n] " save_rosbag
	
	if [[ $save_rosbag =~ ^[yY]$ ]]; then
        echo "Copying latest bag file" 
        latest_bag=$(ls -t /opt/carma/logs/*.bag | head -1)
        cp $latest_bag .
    fi

    exit
}

echo
echo "Starting tcpdumps - when finished press [CTRL + C]"
echo
echo $tcpdump_carma_platorm_out
echo $tcpdump_carma_platorm_in
echo 
$tcpdump_carma_platorm_out & $tcpdump_carma_platorm_in && fg
