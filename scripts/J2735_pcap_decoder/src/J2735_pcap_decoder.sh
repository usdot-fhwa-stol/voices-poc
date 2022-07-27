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

mkdir data
cd data

mkdir -p tsharkOutput
mkdir -p payloadOutput
mkdir -p decodedOutput

cd $directory

printf "\nWhat type of J2735 message was captured?\n"
printf "MAP\nSPAT\nBSM\nMobility\nTraffic Control\n\n"
IFS= read -r message_type

if [ "$message_type" == "MAP" ]; then
	message_type_id=0012
elif [ "$message_type" == "SPAT" ]; then
	message_type_id=0013
elif [ "$message_type" == "BSM" ]; then
	message_type_id=0014
elif [ "$message_type" == "Mobility" ]; then
	printf "\nRequest, Response, Path, or Operation?\n"
	read message_second
	if [ $message_second == "Request" ]; then
		message_type_id=00f0
	elif [ $message_second == "Response" ]; then
		message_type_id=00f1
	elif [ $message_second == "Path" ]; then	
		message_type_id=00f2
	elif [ $message_second == "Operation" ]; then
		message_type_id=00f3
	else 
		echo "Invalid J2735 message type..."
		exit
	fi
	message_type+=" $message_second"
elif [ "$message_type" == "Traffic Control" ]; then
	echo "Request or Message?"
	read message_second
	if [ $message_second == "Request" ]; then
		message_type_id=00f4
	elif [ $message_second == "Message" ]; then	
		message_type_id=00f5
	else 
		echo "Invalid J2735 message type..."
		exit
	fi
	message_type+=" $message_second"
else echo "Invalid J2735 message type..."
	exit
fi

payloadType="hex"
messageTypeIdFound=false

searchForMessageTypeIdInFile(){
fileToCheck=$1
messageTypeIdToFind=$2
numPacketsToCheck=$3
messageTypeIdFound=false

echo
#check the first 10 packets for the desired message type ID
for (( c=1; c<=$numPacketsToCheck; c++ ))
do
	currentPayload=$(sed '$cq;d' $fileToCheck | awk -F ',' '{print $2}')
#id=int(sys.argv[2])
	if [[ "$currentPayload" == *"$messageTypeIdToFind"* ]]; then
		messageTypeIdFound=true
		echo "Found desired message ID ($messageTypeIdToFind) in packet $c"
		#echo $currentPayload
		break
	fi
done
}


extractPackets(){ 
echo
cd $directory/data
ls *.pcap
echo 

while true; do
	read -rep "Input filename from list: " file_to_read
	file_to_write="${file_to_read//pcap/csv}"
	if [ ! -f $file_to_read ]; then
		echo "File not found!"
	else
		break
	fi
done

tshark -r $file_to_read --disable-protocol wsmp -Tfields -Eseparator=, -e frame.time_epoch -e data.data > $directory/data/tsharkOutput/$file_to_write

searchForMessageTypeIdInFile $directory/data/tsharkOutput/$file_to_write $message_type_id 10

if [ $messageTypeIdFound == true ]; then
        # The first packet contains the message id
        printf "\nSuccessfully decoded pcap into hex payloads\n"
        payloadType="hex"
else
        # The first packet does not contain the message id. This is most likely becuase payload is contained in ASCII
        printf "\nCould not find message ID in hex decoded payloads, trying ascii\n"
        tshark -r $file_to_read -o data.show_as_text:TRUE --disable-protocol wsmp -T fields -E separator=, -e frame.time_epoch -e data.text > $directory/data/tsharkOutput/$file_to_write
        payloadType="ascii"
        
        searchForMessageTypeIdInFile $directory/data/tsharkOutput/$file_to_write $message_type_id 10
        
        if [ $messageTypeIdFound ]; then
        	printf "\nSuccessfully decoded pcap into ascii payloads\n\n"
        else
        	printf "\nDecoding in ascii still resulted in an empty file, exiting...\n"
        	exit
        fi
        
fi 
}


getPayload(){
  cd $directory/data/tsharkOutput
  #parse tshark output to get rid of unnecessary bytes in front of payloads
  for i in *
  do
    python3 $directory/src/tshark_OutputParser.py $i $message_type $payloadType
  done
  mv *_payload.csv $directory/data/payloadOutput
}


decodePackets(){
  cd $directory/data/payloadOutput
  printf 'Decoding...\n'
  for i in $(find . -name "*.csv")
  do
    file=$(basename -- "$i")
    fileName="decoded_${file%.*}.csv"
	echo "$fileName"
    python3 $directory/src/J2735decoder.py $i ${fileName} "$message_type" $message_type_id
  done

  mv *decoded* $directory/data/decodedOutput
  printf 'Complete.\n'
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
}

processing
