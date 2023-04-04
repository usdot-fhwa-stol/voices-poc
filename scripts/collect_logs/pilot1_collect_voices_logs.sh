#!/bin/bash

. ../../config/node_info.config

echo
echo "What vehicle position are you? [#]" 
echo 
echo "    [1]  	UCLA Vehicle"
echo "    [2]  	Nissan Vehicle"
echo "    [3]  	Econolite Traffic Light"
echo "    [4]  	MCity Observer"
echo "    [5]  	TFHRC Manual Vehicle"
echo "    [6]  	TFHRC Local CARMA Platform Vehicle"

echo
read -p "--> " positionIndex

vehicle_type='virtual_vehicle'
if [[ $positionIndex == 1 ]]; then
    vehicle_name='ucla'
elif [[ $positionIndex == 2 ]]; then
    vehicle_name='nissan'
elif [[ $positionIndex == 3 ]]; then
    vehicle_name='econolite'
elif [[ $positionIndex == 4 ]]; then
    vehicle_name='mcity'
elif [[ $positionIndex == 5 ]]; then
    vehicle_name='tfhrc_manual'
elif [[ $positionIndex == 6 ]]; then
    vehicle_name='tfhrc_carma'
    vehicle_type='local_carma_platform_vehicle'
else
    echo "Invalid selection, try again..."
    exit
fi

if [[ $vehicle_type == 'live_vehicle' ]]; then

    # Live vehicle
    obu_interface_name=$(ifconfig | grep -B1 "192.168.88.100" | head -n 1 | sed 's/:.*//')
    tcpdump_out="sudo tcpdump -i $obu_interface_name dst 192.168.88.40 and port 1516 -w carma_platform_out.pcap"
    tcpdump_in="sudo tcpdump -i $obu_interface_name src 192.168.88.40 and port 5398 -w carma_platform_in.pcap"

elif [[ $vehicle_type == 'virtual_vehicle' ]]; then

    # Virtual vehicle
    tcpdump_out=""
    tcpdump_in=""

elif [[ $vehicle_type == 'local_carma_platform_vehicle' ]]; then

    # Local CARMA Platform Vehicle
    tcpdump_out="sudo tcpdump -i lo port 56700 -w carma_platform_out.pcap"
    tcpdump_in="sudo tcpdump -i lo port 5398 -w carma_platform_in.pcap"

fi

timestamp=$(date -d "today" +"%Y%m%d%H%M%S")

logs_folder_name=$vehicle_name'_'$timestamp

echo
echo "Folder Name: "$logs_folder_name

mkdir -p ./log_files/$logs_folder_name
cd ./log_files/$logs_folder_name

#if we are not a live vehicle then prompt to collect logs 
#(live vehicle is not connected to VOICES network)

if [[ ! $vehicle_type == 'live_vehicle' ]]; then

    echo
    read -p "Would you like to collect the TENA SDO data? [y/n] " save_tdcs_data

    if [[ $save_tdcs_data =~ ^[yY]$ ]]; then
        echo
        echo "Starting TDCS" 
        tdcs_command="$tdcsPath/start.sh -emEndpoints $emAddress:$emPort -listenEndpoints $localAddress -databaseName $logs_folder_name.sqlite -dbFolder ."
        echo $tdcs_command
        $tdcs_command &
    fi
fi

if [[ $vehicle_type == 'local_carma_platform_vehicle' ]]; then
    trap copyCarmaLogs SIGINT
fi

copyCarmaLogs()
{
    echo
    echo "tcpdumps stopped"
    echo
    echo "ENSURE CARMA PLATFORM, CARLA, TDCS, AND ALL ADAPTERS ARE STOPPED (All V2X Hub plugins may remain enabled)"
    read -p "--> To continue, press [ENTER] " enter_press
    
    #if carma vehicle
    echo
    echo "Copying carma logs"
    latest_logs=$(readlink -f /opt/carma/logs/latest)
    cp -r $latest_logs .

    #if not a live vehicle (meaning must be constructive) then get adapter logs
    if [[ ! $vehicle_type == 'live_vehicle' ]]; then

        echo "Copying adapter logs"
        mv $localAdapterLogPath/*.log .

        echo "Copying carma simulation logs"    
        mv $localCarmaSimLogPath/*.log .
    
    fi

    echo
    read -p "Would you like to save the CARMA Platform rosbag? [y/n] " save_rosbag
    
    if [[ $save_rosbag =~ ^[yY]$ ]]; then
        echo "Copying latest bag file" 
        latest_bag=$(ls -t /opt/carma/logs/*.bag | head -1)
        cp $latest_bag .
    fi

    exit
}

#not collecting tcpdumps for virtual vehicle
if [[ ! $vehicle_type == "virtual_vehicle" ]]; then
    echo
    echo "Starting tcpdumps - when finished press [CTRL + C]"
    echo
    echo $tcpdump_out
    echo $tcpdump_in
    echo 
    $tcpdump_out & $tcpdump_in && fg
fi
