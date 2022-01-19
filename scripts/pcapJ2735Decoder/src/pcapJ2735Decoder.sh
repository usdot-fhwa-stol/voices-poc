#!/bin/bash
#this takes the location of the executed script as opposed to the current location
#this allows it to be run anywhere
directory="`dirname \"$0\"`"
directory="`( cd \"$directory\" && cd ../ && pwd )`"
cd $directory

if [ -d data ]; then
	echo
	echo "Existing data folder found, would you like to delete it? [y/n]"
	
	read -p "---> " delete_old_data
	if [[ $delete_old_data =~ ^[Yy]$ ]]; then
		rm -rf data
	else
		echo
		echo "Please move or rename existing data folder and try again"
		exit
	fi
fi

mkdir data
cd data

mkdir -p tsharkOutput
mkdir -p payloadOutput
mkdir -p decodedOutput

cd ../

echo
echo "What type of J2735 message was captured?"
echo "MAP"
echo "SPAT"
echo "BSM"
echo
read -p "--> " message_type

if [ $message_type == "MAP" ]; then
	message_type_id=0012
elif [ $message_type == "SPAT" ]; then
	message_type_id=0013
elif [ $message_type == "BSM" ]; then
	message_type_id=0014
else
	echo "Invalid J2735 message type..."
	exit
fi

payloadType="hex"
messageTypeIdFound=false

searchForMessageTypeIdInFile() { 

fileToCheck=$1
messageTypeIdToFind=$2
numPacketsToCheck=$3

messageTypeIdFound=false

echo
#check the first 10 packets for the desired mesasge type ID
for (( c=1; c<=$numPacketsToCheck; c++ ))
do
	currentPayload=$(sed '$cq;d' $fileToCheck | awk -F ',' '{print $2}')
	echo "Checking packet $c..."
	#echo "Packet $c:" $currentPayload
	
	if [[ "$currentPayload" == *"$messageTypeIdToFind"* ]]; then
		messageTypeIdFound=true
		echo "--> Found desired message ID ($messageTypeIdToFind) in packet $c:"
		#echo $currentPayload
		break
	fi
done


}




extractPackets() { 

echo
ls *.pcap
echo 
while true; do
	read -p "Input Filename: " file_to_read
	if [ ! -f $file_to_read ]; then
		echo "File not found!"
	else
		break
	fi
done

read -p "Output Filename (.csv): " file_to_write

tshark -r $file_to_read --disable-protocol wsmp -Tfields -Eseparator=, -e frame.time_epoch -e data.data > $directory/data/tsharkOutput/$file_to_write  



searchForMessageTypeIdInFile $directory/data/tsharkOutput/$file_to_write $message_type_id 10



if [ $messageTypeIdFound == true ]; then
        # The first packet contains the message id
        echo
        echo "Successfully decoded pcap into hex payloads"
        payloadType="hex"
else
        # The first packet does not contain the message id. This is most likely becuase payload is contained in ASCII
        echo
        echo "Could not find message ID in hex decoded payloads, trying ascii"
        tshark -r $file_to_read -o data.show_as_text:TRUE --disable-protocol wsmp -T fields -E separator=, -e frame.time_epoch -e data.text > $directory/data/tsharkOutput/$file_to_write
        payloadType="ascii"
        
        searchForMessageTypeIdInFile $directory/data/tsharkOutput/$file_to_write $message_type_id 10
        
        if [ $messageTypeIdFound ]; then
        	echo
        	echo "Successfully decoded pcap into ascii payloads"
        else
        	echo
        	echo "Decoding in ascii still resulted in an empty file, exiting..."
        	exit
        fi
        
fi


    
}

getPayload() {
  cd $directory/data/tsharkOutput
  #parse tshark output to get rid of unnecessary bytes in front of BSM/SPAT/MAP
  for i in *
  do
    python3 $directory/src/tshark_OutputParser.py $i $message_type $payloadType
  done
  mv *_payload.csv $directory/data/payloadOutput
}

decodePackets() {

  cd $directory/data/payloadOutput
  
  for i in $(find . -name "*.csv")
  do
    file=$(basename -- "$i")
    fileName="${file%.*}"
    python3 $directory/src/J2735decoder.py $i 0 decoded_${fileName}.csv $message_type
  done

  mv *decoded* $directory/data/decodedOutput
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
  if [ $message_type == "BSM" ]; then
  	generateKml
  fi
}

processing
