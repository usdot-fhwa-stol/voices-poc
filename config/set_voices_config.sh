#! /bin/bash

echo
echo "Enter a site config from the list below: " 
echo 
{ 
	ls ./site_config/*.config | xargs -n 1 basename
} || { 
	echo
	echo "No config files found in data directory" 
	exit 
}

while true; do
	echo
	read -rep "-->: " site_config_file
	if [ ! -f ./site_config/$site_config_file ]; then
		echo "    [!!!] File not found!"
	else
		site_config_path=$(readlink -f ./site_config/$site_config_file)
        break
	fi
done

ln -sf $site_config_path $HOME/.voices_config

