#! /bin/bash

# select site config file
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

# create syn link
while true; do
	echo ""
	read -rep "-->: " site_config_file
	if [ ! -f ./site_config/$site_config_file ]; then
		echo "    File not found!"
	else
		site_config_path=$(readlink -f ./site_config/$site_config_file)
        break
	fi
done

ln -sf $site_config_path $HOME/.voices_site_config

source $HOME/.voices_site_config

if [ ! -f $VUG_SCENARIO_CONFIG_PATH/$VUG_SCENARIO_CONFIG_FILE ]; then
	echo "    Scenario config file not found: $VUG_SCENARIO_CONFIG_PATH/$VUG_SCENARIO_CONFIG_FILE"
	exit
else
	scenario_config_path=$(readlink -f $VUG_SCENARIO_CONFIG_PATH/$VUG_SCENARIO_CONFIG_FILE)
fi

ln -sf $scenario_config_path $HOME/.voices_scenario_config

# remove old config architecture
rm -f $HOME/.voices_config

# add to bash rc
if grep -qx "source ~/.voices_site_config" ~/.bashrc
then
	echo "Source site config command already exists in .bashrc"
else
    echo "Adding site config source command to .bashrc"
	echo "source ~/.voices_site_config" >> ~/.bashrc
fi

if grep -qx "source ~/.voices_scenario_config" ~/.bashrc
then
	echo "Source scenario config command already exists in .bashrc"
else
    echo "Adding scenario config source command to .bashrc"
	echo "source ~/.voices_scenario_config" >> ~/.bashrc
fi

echo
echo "Config successfully set. Please close and reopen the terminal to use the new config."

