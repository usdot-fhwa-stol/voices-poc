#!/bin/bash

. ../../../../config/node_info.config

# Copy the map message file into V2X
if [[ ! -d $v2xRepo/configuration/amd64/MAP/ ]]; then
  mkdir $v2xRepo/configuration/amd64/MAP/
fi

cp ../../../../map_files/pilot1-test4/UCLA_Map_Message/UCLA_Map_Message.b  $v2xRepo/configuration/amd64/MAP/

# Generate secrets files
if [[ ! -f $v2xRepo/configuration/amd64/secrets/mysql_password.txt ]]; then
  echo "password" >$v2xRepo/configuration/amd64/secrets/mysql_password.txt
fi
if [[ ! -f $v2xRepo/configuration/amd64/secrets/mysql_root_password.txt ]]; then
  echo "password" >$v2xRepo/configuration/amd64/secrets/mysql_root_password.txt
fi

## Initialize
#cd $v2xRepo/configuration/amd64
#./initialization.sh

# Start V2X
cd $v2xRepo/configuration/amd64
docker-compose up
