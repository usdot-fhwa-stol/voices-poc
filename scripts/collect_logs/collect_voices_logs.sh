#!/bin/bash

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

echo "Folder Name: "$logs_folder_name

mkdir -p ./log_files/$logs_folder_name
cd ./log_files/$logs_folder_name

tcpdump_carma_platorm_out='sudo tcpdump -i lo port 56700 -w carma_platform_out.pcap'

tcpdump_carma_platorm_in='sudo tcpdump -i lo port 5398 -w carma_platform_in.pcap '


trap copyCarmaLogs SIGINT

copyCarmaLogs()
{
    echo
    echo "Copying carma logs"
    latest_logs=$(readlink -f /opt/carma/logs/latest)
    cp -r $latest_logs .
    exit
}

$tcpdump_carma_platorm_out & $tcpdump_carma_platorm_in && fg
