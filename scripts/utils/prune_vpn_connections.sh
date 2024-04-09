#!/usr/bin/bash

# Check if openvpn3 is installed
if ! command -v openvpn3 &> /dev/null
then
    if [ $VUG_FORCE_VPN = true ]
    then
        echo "openvpn3 is not installed but you have set VUG_FORCE_VPN=true in your scenario config."
        echo "Either install openvpn3 and activate a connection or set VUG_FORCE_VPN=false to continue."
        exit 1
    fi
    echo "openvpn3 could not be found. Skipping VPN checks..."
    exit 0
fi


# Get output from openvpn3 sessions-list
text="$(sudo openvpn3 sessions-list)"
vpn_paths=()
path_regex='Path: (.*)'
vpn_statuses=()
status_regex='Status: (.*)'
has_stale_vpn_connections=false
has_active_vpn_connection=false
has_multiple_active_vpn_connections=false
vpn_start_times=()
start_time_regex='Created: (.*) PID: .*'
iterator=0
while read line; do
    if [[ $line =~ $path_regex ]]
    then # Grab VPN path
        vpn_paths+=("${BASH_REMATCH[1]}")
    elif [[ $line =~ $status_regex ]]
    then # Grab VPN status
        if [[ ${BASH_REMATCH[1]} = "Connection, Client connected" ]]
        then
            if $has_active_vpn_connection
            then
                has_multiple_active_vpn_connections=true
            fi
            vpn_statuses+=(1)
            has_active_vpn_connection=true
        else
            vpn_statuses+=(0)
            has_stale_vpn_connections=true
        fi
    elif [[ $line =~ $start_time_regex ]]
    then # Grab VPN start time and convert to unix timestamp
        vpn_start_times+=("$(date -d "${BASH_REMATCH[1]}" +"%s")")
    fi
done <<< "$text"

if $has_stale_vpn_connections
then
    while true; do
        echo ''
        read -p "You have stale VPN connections. Would you like to remove them? [Y/n] " yn
        case $yn in
            [Yy]* | "") for i in $(seq 1 ${#vpn_statuses[@]}); do
                        if [[ ${vpn_statuses[i-1]} = 0 ]]
                        then
                            echo "Removing "${vpn_paths[i-1]}
                            sudo openvpn3 session-manage --session-path ${vpn_paths[i-1]} --disconnect
                        fi
                    done; break;;
            [Nn]* ) echo ''; break;;
            * );;
        esac
    done
else
    echo "No stale VPN connections found."
fi


if $has_multiple_active_vpn_connections
then
    most_recent_start=0
    for i in $(seq 1 ${#vpn_start_times[@]}); do
        if [ ${vpn_start_times[i-1]} -gt $most_recent_start ] && [ ${vpn_statuses[i-1]} = 1 ]; then
            most_recent_start=${vpn_start_times[i-1]}
            echo "Got: "${vpn_start_times[i-1]} " Most Recent: " $most_recent_start
        fi
    done 
    while true; do
        echo ''
        read -p "You have multiple active VPN connections. Would you like to remove all but the most recent? [Y/n] " yn
        case $yn in
            [Yy]* | "") for i in $(seq 1 ${#vpn_statuses[@]}); do
                        if [ ${vpn_statuses[i-1]} = 1 -a ${vpn_start_times[i-1]} != $most_recent_start ]
                        then
                            echo "Removing "${vpn_paths[i-1]}
                            sudo openvpn3 session-manage --session-path ${vpn_paths[i-1]} --disconnect
                        fi
                    done; break;;
            [Nn]* ) echo ''; break;;
            * );;
        esac
    done
elif $has_active_vpn_connection
then
    most_recent_start=0
    for i in $(seq 1 ${#vpn_start_times[@]}); do
        if [ ${vpn_start_times[i-1]} -gt $most_recent_start ] && [ ${vpn_statuses[i-1]} = 1 ]; then
            most_recent_start=${vpn_start_times[i-1]}
            echo "Got: "${vpn_start_times[i-1]} " Most Recent: " $most_recent_start
        fi
    done 
    if [ $VUG_FORCE_VPN = false ]
    then
        while true; do
            echo ''
            read -p "You have an active VPN session but have set VUG_FORCE_VPN=false. Would you like to terminate the session? [y/N] " yn
            case $yn in
                [Yy]*)  for i in $(seq 1 ${#vpn_statuses[@]}); do
                            if [ ${vpn_statuses[i-1]} = 1 -a ${vpn_start_times[i-1]} = $most_recent_start ]
                            then
                                echo "Removing "${vpn_paths[i-1]}
                                sudo openvpn3 session-manage --session-path ${vpn_paths[i-1]} --disconnect
                            fi
                        done; break;;
                [Nn]* | "") echo ''; break;;
                * );;
            esac
        done
    fi
else
    if [ $VUG_FORCE_VPN = true ]
    then
        echo "No active VPN connections found. Please connect to an openvpn3 session or set VUG_FORCE_VPN=false in your scenario config to continue."
        exit 1
    fi
fi