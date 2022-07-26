#!/bin/bash

. ../run_scripts/demo1/node_info.config

echo
read -p "Is this a live vehicle? [y/n] " is_live_vehicle

if [[ ! $is_live_vehicle =~ ^[yY]$ ]]; then
    echo
    read -p "Is this a V2X Hub? [y/n] " is_v2xhub
fi

if [[ $is_v2xhub =~ ^[yY]$ ]]; then
    
    vehicle_position='v2xhub'
    
else
    
    echo
    echo "What vehicle position are you? [#]" 
    echo 
    echo "    [1]  	lead vehicle"
    echo "    [2]  	second vehicle"
    echo "    [3]  	third vehicle"
    echo "    [4]  	virtual vehicle"

    echo
    read -p "--> " positionIndex


    if [[ $positionIndex == 1 ]]; then
        vehicle_position='lead_vehicle'
    elif [[ $positionIndex == 2 ]]; then
        vehicle_position='second_vehicle'
    elif [[ $positionIndex == 3 ]]; then
        vehicle_position='third_vehicle'
    elif [[ $positionIndex == 4 ]]; then
        vehicle_position='virtual_vehicle'
    else
        echo "Invalid selection, try again..."
        exit
    fi

fi

if [[ $is_live_vehicle =~ ^[yY]$ ]]; then
    obu_interface_name=$(ifconfig | grep -B1 "192.168.88.100" | head -n 1 | sed 's/:.*//')
    
    tcpdump_out="sudo tcpdump -i $obu_interface_name dst 192.168.88.40 and port 1516 -w carma_platform_out.pcap"
    tcpdump_in="sudo tcpdump -i $obu_interface_name src 192.168.88.40 and port 5398 -w carma_platform_in.pcap"
elif [[ $vehicle_position == 'virtual_vehicle' ]]; then

    tcpdump_out=""
    tcpdump_in=""

elif [[ $is_v2xhub =~ ^[yY]$ ]]; then
    
    echo
    ifconfig | grep -B 1 "inet "

    echo
    read -p "What is the name of the network interface used to connect to the RSU? " v2xhub_interface

    echo
    read -p "What is the IP of the RSU? " v2xhub_rsu_ip

    echo
    read -p "What is the inbound Message Receiver Plugin port? (typically 26789) " v2xhub_mr_in_port

    echo
    read -p "What is the outbound DSRC Message Manager port? (typically 1516) " v2xhub_dmm_out_port
    
    tcpdump_out="sudo tcpdump -i $v2xhub_interface dst $v2xhub_rsu_ip and port $v2xhub_dmm_out_port -w v2xhub_out.pcap"
    tcpdump_in="sudo tcpdump -i $v2xhub_interface src $v2xhub_rsu_ip and port $v2xhub_mr_in_port -w v2xhub_in.pcap"
else
    tcpdump_out="sudo tcpdump -i lo port 56700 -w carma_platform_out.pcap"
    tcpdump_in="sudo tcpdump -i lo port 5398 -w carma_platform_in.pcap"
fi

timestamp=$(date -d "today" +"%Y%m%d%H%M%S")

logs_folder_name=$vehicle_position'_'$timestamp

echo
echo "Folder Name: "$logs_folder_name

mkdir -p ./log_files/$logs_folder_name
cd ./log_files/$logs_folder_name

#if we are not a live vehicle then prompt to collect logs 
#(live vehicle is not connected to VOICES network)

if [[ ! $is_live_vehicle =~ ^[yY]$ ]]; then

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

trap copyCarmaLogs SIGINT

copyCarmaLogs()
{
    echo
    echo "tcpdumps stopped"
    echo
    echo "ENSURE CARMA PLATFORM, CARLA, TDCS, AND ALL ADAPTERS ARE STOPPED (All V2X Hub plugins may remain enabled)"
    read -p "--> To continue, press [ENTER] " enter_press
    
    #if carma vehicle - at this time v2xhub is only non vehicle
    if [[ ! $is_v2xhub =~ ^[yY]$ ]]; then
        echo
        echo "Copying carma logs"
        latest_logs=$(readlink -f /opt/carma/logs/latest)
        cp -r $latest_logs .

        #if not a live vehicle (meaning must be constructive) then get adapter logs
        if [[ ! $is_live_vehicle =~ ^[yY]$ ]]; then
    
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
    fi

    exit
}

#not collecting tcpdumps for virtual vehicle
if [[ ! $vehicle_position == "virtual_vehicle" ]]; then
    echo
    echo "Starting tcpdumps - when finished press [CTRL + C]"
    echo
    echo $tcpdump_out
    echo $tcpdump_in
    echo 
    $tcpdump_out & $tcpdump_in && fg
fi
