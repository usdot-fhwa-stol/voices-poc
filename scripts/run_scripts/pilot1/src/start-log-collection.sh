#!/bin/bash

voices_config=~/.voices_config

if [ -L ${voices_config} ] ; then
   if [ -e ${voices_config} ] ; then
      config_link_dest=$(readlink -f $voices_config)
      link_base_name=$(basename ${config_link_dest})

      . $voices_config


      echo "Site Config: "$link_base_name
      echo "Scenario Config: "$VUG_SCENARIO_CONFIG_FILE
   else
      echo "[!!!] .voices_config link is broken"
      exit 1
   fi
elif [ -e ${voices_config} ] ; then
   echo "[!!!] .voices_config file is not a symbolic link"
   exit 1
else
   echo "[!!!] .voices_config link is is missing"
   exit 1
fi

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
vehicle_name=$VUG_CARMA_VEHICLE_ID
if [[ $positionIndex == 6 ]]; then
    vehicle_type='local_carma_platform_vehicle'
elif [[ $positionIndex -gt 6 ]]; then
    echo "Invalid selection, try again..."
    exit
fi

if [[ $vehicle_type == 'live_vehicle' ]]; then

    # Live vehicle
    obu_interface_name=$(ifconfig | grep -B1 "192.168.88.100" | head -n 1 | sed 's/:.*//')
    tcpdump_out="sudo tcpdump -i $obu_interface_name dst 192.168.88.40 and port 1516 -w carma_platform_out.pcap"
    tcpdump_in="sudo tcpdump -i $obu_interface_name src 192.168.88.40 and port 5398 -w carma_platform_in.pcap"

else

    tcpdump_out="sudo tcpdump -i lo port $VUG_J2735_ADAPTER_RECEIVE_PORT -w ip_packet_out.pcap"
    tcpdump_in="sudo tcpdump -i lo port $VUG_J2735_ADAPTER_SEND_PORT -w ip_packet_in.pcap"

fi

timestamp=$(date -d "today" +"%Y%m%d%H%M%S")

logs_folder_name=$VUG_SIM_ID'_'$timestamp

echo
echo "Folder Name: "$logs_folder_name

mkdir -p $VUG_LOG_FILES_ROOT/$logs_folder_name
cd $VUG_LOG_FILES_ROOT/$logs_folder_name

#if we are not a live vehicle then prompt to collect logs 
#(live vehicle is not connected to VOICES network)

if [[ ! $vehicle_type == 'live_vehicle' ]]; then

    echo
    read -p "Would you like to collect the TENA SDO data? [y/n] " save_tdcs_data

    if [[ $save_tdcs_data =~ ^[yY]$ ]]; then
        echo
        echo "Starting TDCS" 
        tdcs_command="$VUG_TDCS_PATH/start.sh -emEndpoints $VUG_EM_ADDRESS:$VUG_EM_PORT -listenEndpoints $VUG_LOCAL_ADDRESS -databaseName $logs_folder_name.sqlite -dbFolder ."
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
        mv $VUG_ADAPTER_LOG_PATH/*.log .

        echo "Copying carma simulation logs"    
        mv $VUG_CARMA_SIM_LOG_PATH/*.log .
    
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

echo
echo "Starting tcpdumps - when finished press [CTRL + C]"
echo
echo $tcpdump_out
echo $tcpdump_in
echo 
$tcpdump_out & $tcpdump_in && fg
