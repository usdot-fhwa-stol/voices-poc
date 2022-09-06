#!/bin/bash

#  *                                                                              
#  * Copyright (C) 2022 LEIDOS.                                              
#  *                                                                              
#  * Licensed under the Apache License, Version 2.0 (the "License"); you may not  
#  * use this file except in compliance with the License. You may obtain a copy o\
# f                                                                               
#  * the License at                                                               
#  *                                                                              
#  * http://www.apache.org/licenses/LICENSE-2.0                                   
#  *                                                                              
#  * Unless required by applicable law or agreed to in writing, software          
#  * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT    
#  * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the     
#  * License for the specific language governing permissions and limitations under                                                                               
#  * the License.                                                                 
#  *

#exit on error
#
set -e
# set -x

#this takes the location of the executed script as opposed to the current location
#this allows it to be run anywhere
directory="`dirname \"$0\"`"
directory="`( cd \"$directory\" && cd ../ && pwd )`"
cd $directory

# Section propably not needed. I'd like to place files in the data folder before running script and the script will just add to the existing data folder
#if [ -d data ]; then
#	printf "\nExisting data folder found, would you like to delete it? [y/n]"
	
#	read delete_old_data
#	if [[ $delete_old_data =~ ^[Yy]$ ]]; then
#		rm -rf data
#	else
#		printf "\nPlease move or rename existing data folder and try again"
#		exit
#	fi
#fi

if [ -d data ]; then
	printf "\nFiles found in data directory:"
else
	mkdir data
fi

cd data

mkdir -p tsharkOutput
mkdir -p payloadOutput
mkdir -p decodedOutput

cd $directory

# REMOVED AS NOW WE DECODE ALL MESSAGE TYPES
#
# printf "\n\nWhat type of J2735 message type would you like to decode?\n"

# message_type_list=("MAP" "SPAT" "BSM" "Mobility Request" "Mobility Response" "Mobility Path" "Mobility Operation" "Traffic Control Request" "Traffic Control Message")

# for i in ${!message_type_list[@]}; do
#   printf "\n[$i] ${message_type_list[$i]}"
# done

# printf "\n\n"
# read -p "--> " message_type_index

# message_type_name=${message_type_list[$message_type_index]}

# if [[ $message_type_name == "MAP" ]]; then
# 	message_type_id=0012
# elif [[ $message_type_name == "SPAT" ]]; then
# 	message_type_id=0013
# elif [[ $message_type_name == "BSM" ]]; then
# 	message_type_id=0014
# elif [[ $message_type_name == "Mobility Request" ]]; then
# 	message_type_id=00f0
# elif [[ $message_type_name == "Mobility Response" ]]; then
# 	message_type_id=00f1
# elif [[ $message_type_name == "Mobility Path" ]]; then	
# 	message_type_id=00f2
# elif [[ $message_type_name == "Mobility Operation" ]]; then
# 	message_type_id=00f3
# elif [[ $message_type_name == "Traffic Control Request" ]]; then
# 	message_type_id=00f4
# elif [[ $message_type_name == "Traffic Control Message" ]]; then	
# 	message_type_id=00f5
# else 
# 	echo "Invalid J2735 message type..."
# 	exit
# fi

# echo "Message Type Name: "$message_type_name
# echo "Message Type ID: "$message_type_id


payloadType="hex"
messageTypeIdFound=false

# REMOVE THIS AS IT IS NO LONGER NEEDED
#
# searchForMessageTypeIdInFile(){
# fileToCheck=$1
# messageTypeIdToFind=$2
# numPacketsToCheck=$3
# messageTypeIdFound=false

# echo
# #check the first 10 packets for the desired message type ID
# for (( c=1; c<=$numPacketsToCheck; c++ ))
# do
# 	currentPayload=$(sed '$cq;d' $fileToCheck | awk -F ',' '{print $2}')
# #id=int(sys.argv[2])
# 	if [[ "$currentPayload" == *"$messageTypeIdToFind"* ]]; then
# 		messageTypeIdFound=true
# 		echo "Found desired message ID ($messageTypeIdToFind) in packet $c"
# 		#echo $currentPayload
# 		break
# 	fi
# done
# }


extractPackets(){ 
echo
cd $directory/data
echo 
ls *.pcap

while true; do
	echo
	read -rep "Input filename from list: " pcap_file_to_read
	if [ ! -f $pcap_file_to_read ]; then
		echo "    [!!!] File not found!"
	else
		break
	fi
done

input_pcap_base_name=${pcap_file_to_read%".pcap"}
#echo $input_pcap_base_name

#tshark -r $pcap_file_to_read --disable-protocol wsmp -Tfields -Eseparator=, -e frame.time_epoch -e data.data > $directory/data/tsharkOutput/$file_to_write

#searchForMessageTypeIdInFile $directory/data/tsharkOutput/$file_to_write $message_type_id 10

#search first 10 packets in text format and look for Payload=
#if this exist, string, we are ascii payloads and can decode that way
#if not, we must grab the payload from the frame_raw (tshark_json_parser)
search_for_ascii=$(tshark -r $pcap_file_to_read -o data.show_as_text:TRUE --disable-protocol wsmp -T fields -E separator=, -e data.text -c 10)
#search_for_ascii=$(tshark -r $pcap_file_to_read -o data.show_as_text:TRUE --disable-protocol wsmp -T fields -E separator=, -e frame.time_epoch -e data.text -c 10 | grep "Payload=")


search_for_ascii=${search_for_ascii//['\t\r\n']}

# echo "Search: " $search_for_ascii



# if [ true ]; then
if [[ $search_for_ascii = *[![:ascii:]]* || $search_for_ascii == "" ]]; then
        # The first packet contains the message id
		printf "\n --> PCAP is HEX\n"
		payloadType="hex"

		tshark_output_file=$input_pcap_base_name"_raw_packet_frames.csv"

		python3 $directory/src/tshark_json_parser.py $pcap_file_to_read $tshark_output_file
		mv $tshark_output_file $directory/data/tsharkOutput
        
else
        # The first packet does not contain the message id. This is most likely becuase payload is contained in ASCII
        printf "\n --> PCAP is in ascii\n"
		payloadType="ascii"

        # tshark -r $pcap_file_to_read -o data.show_as_text:TRUE --disable-protocol wsmp -T fields -E separator=, -e frame.time_epoch -e data.text > $directory/data/tsharkOutput/$raw_packet_output_file

		tshark_output_file=$input_pcap_base_name"_payloads.csv"

		python3 $directory/src/tshark_ascii_parser.py $pcap_file_to_read $tshark_output_file
		mv $tshark_output_file $directory/data/tsharkOutput

        #searchForMessageTypeIdInFile $directory/data/tsharkOutput/$raw_packet_output_file $message_type_id 10
                
fi

# echo
# echo "----- EARLY EXIT FOR TESTING -----"
# exit 

}


getPayload(){
	cd $directory/data/tsharkOutput
	parsed_tshark_file=$input_pcap_base_name"_filtered_packets.csv"
	#parse tshark output to get rid of unnecessary bytes in front of payloads
	python3 $directory/src/tshark_OutputParser.py $tshark_output_file $parsed_tshark_file $payloadType
	mv $parsed_tshark_file $directory/data/payloadOutput
}


decodePackets(){
	cd $directory/data/payloadOutput

	decoded_file=$input_pcap_base_name"_decoded_packets.csv"
	python3 $directory/src/J2735decoder.py $parsed_tshark_file $decoded_file

	decoded_output_file_pattern=$input_pcap_base_name"_decoded_packets*" 

	mv $decoded_output_file_pattern $directory/data/decodedOutput
	
}


generateKml(){ 
echo 
echo "Generating KML from CSV"
	
mkdir -p $directory/data/kmlOutput

cat << EOF > $directory/data/kmlOutput/kmlOutput.kml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <name>BSMs</name>
  <description><![CDATA[KML of decoded BSMs]]></description>
  <Style id="end">
    <IconStyle>
      <Icon>
	<href>http://maps.gstatic.com/intl/en_us/mapfiles/ms/micons/red-dot.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="middle">
    <IconStyle>
      <Icon>
	<href>http://maps.gstatic.com/intl/en_us/mapfiles/ms/micons/blue-dot.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="start">
    <IconStyle>
      <Icon>
	<href>http://maps.gstatic.com/intl/en_us/mapfiles/ms/micons/green-dot.png</href>
      </Icon>
    </IconStyle>
  </Style>

EOF

	rowIndex=1
	last_line=$(wc -l < $directory/data/decodedOutput/*.csv)
	#echo "Last Line: "$last_line
	while IFS=, read time secMark latitude longitude speed elevation accel_long hex
	do
		#echo $rowIndex
		#echo "Lat: "$latitude
		#echo "Long: "$longitude
		if [[ $latitude == "latitude" ]]; then
			continue
		elif [[ $rowIndex == 1 ]]; then
			currentStyle="start"
			currentName="START"
		elif (( $rowIndex >=  $last_line - 1 )); then
			currentStyle="end"
			currentName="END"
		else
			currentStyle="middle"
			currentName="Point "$rowIndex
		fi
		echo '<Placemark><name>'$currentName'</name><styleUrl>#'$currentStyle'</styleUrl><Point><coordinates>'$longitude,$latitude','$elevation'</coordinates></Point></Placemark>' >> $directory/data/kmlOutput/kmlOutput.kml
	
	((rowIndex++))
	
	done < $directory/data/decodedOutput/*.csv


	echo "</Document>" >> $directory/data/kmlOutput/kmlOutput.kml
	echo "</kml>" >> $directory/data/kmlOutput/kmlOutput.kml
}


processing(){
  extractPackets
  getPayload
  decodePackets
  if [ "$message_type" == "BSM" ]; then
  	generateKml
  fi
  printf '\n----- DECODING COMPLETE -----\n'
}

processing

trap 'ERROR: $LINENOE' ERR