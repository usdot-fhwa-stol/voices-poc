#!/bin/bash

# Ensure mysql-client is installed
REQUIRED_PKG="tcpreplay"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
echo Checking for $REQUIRED_PKG: $PKG_OK
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG found. Installing $REQUIRED_PKG."
  sudo apt-get update
  sudo apt-get --yes install $REQUIRED_PKG
fi

echo
echo "Showing pcap files in current directory: "

echo 
{ 
	ls *.pcap
} || { 
	echo
	echo "No pcaps found in current directory" 
	exit 
}

while true; do
	echo
	read -rep "Input filename from list: " pcap_file_to_read
	if [ ! -f $pcap_file_to_read ]; then
		echo "    [!!!] File not found!"
	else
		break
	fi
done
pcap_outfile="rewrite_"$pcap_file_to_read

source_ip="192.168.1.90"
source_mac="52:54:00:b9:4a:db"
dest_ip="192.168.1.80"
dest_mac="04:d4:c4:5b:66:92"


echo
echo "FINAL COMMAND: "
echo tcprewrite --infile=$pcap_file_to_read --outfile=$pcap_outfile --srcipmap=0.0.0.0/0:$dest_ip --enet-smac=$source_mac --dstipmap=0.0.0.0/0:$dest_ip --enet-dmac=$dest_mac --fixcsum

tcprewrite --infile=$pcap_file_to_read --dlt=enet --outfile=$pcap_outfile --srcipmap=0.0.0.0/0:$source_ip --enet-smac=$source_mac --dstipmap=0.0.0.0/0:$dest_ip --enet-dmac=$dest_mac --fixcsum