#!/bin/bash

echo
echo "Checking for SpatPlugin_West.zip"

eastLs=$(sudo docker exec -it v2xhub ls -1 /home/V2X-Hub/src/v2i-hub | grep SpatPlugin_West.zip)
#echo $eastLs

echo
if [[ -z $eastLs ]]; then
	echo "SpatPlugin_West.zip does not exist, copying to v2xhub and installing..."
	sudo docker cp SpatPlugin_West.zip v2xhub:/home/V2X-Hub/src/v2i-hub
	sudo docker exec -it -w '/home/V2X-Hub/src/v2i-hub/' v2xhub tmxctl --plugin-install SpatPlugin_West.zip
else
	echo "SpatPlugin_West.zip exists..."
fi

echo
echo "Checking for SpatPlugin_East.zip"

eastLs=$(sudo docker exec -it v2xhub ls -1 /home/V2X-Hub/src/v2i-hub | grep SpatPlugin_East.zip)
#echo $eastLs

echo
if [[ -z $eastLs ]]; then
        echo "SpatPlugin_East.zip does not exist, copying to v2xhub and installing..."
        sudo docker cp SpatPlugin_East.zip v2xhub:/home/V2X-Hub/src/v2i-hub
        sudo docker exec -it -w '/home/V2X-Hub/src/v2i-hub/' v2xhub tmxctl --plugin-install SpatPlugin_East.zip
else
        echo "SpatPlugin_East.zip exists..."
fi
