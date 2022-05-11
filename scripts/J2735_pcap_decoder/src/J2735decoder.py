#!/usr/bin/env python

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


from binascii import hexlify, unhexlify
import J2735
import json
import sys
import csv
import datetime
import numpy



def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

## read from file and print time for only asked id
##usage pydecoder filename  id outputfile

#print("usage pydecoder filename id outputfile J2735msg[BSM/MAP/SPAT]")

if (len(sys.argv) < 4):
    print("Incomplete Arguments");
    exit(1)

fp1=open(sys.argv[1],'r')
id=int(sys.argv[2])
fout=open(sys.argv[3],'w')#,0)
msgid=""
numSpatPhases = 31 #use one more than desired phases

if(sys.argv[4] == "BSM"):
    msgid="0014"
    fout.write("packet time,secMark,latency,latitude,longitude,speed(m/s),heading,elevation(m),accel_long(m/s^2),hex\n")
elif(sys.argv[4]=="SPAT"):
    msgid="0013"
    columnHeaderString="packetTimestamp,spatTimestamp,intersectionID,intersectionName"
    for headerPhase in range(1,numSpatPhases):
        columnHeaderString = columnHeaderString + ",phase" + str(headerPhase) + "_eventState"
    columnHeaderString = columnHeaderString + "\n"
    #print(columnHeaderString)
    fout.write(columnHeaderString)
elif(sys.argv[4]=="MAP"):
    msgid="0012"
    fout.write("time,intersectionID,hex\n")

fp= csv.reader(fp1,delimiter=',')
list1=list(fp)

latency_array = []
prevSpatTimestamp = 0

for dt in list1:

    if(dt[1][0:4]==msgid):
        msg = J2735.DSRC.MessageFrame
        #print("hex: " + dt[1] + " byte length: " + str(len(dt[1])))
        try:
            msg.from_uper(unhexlify(dt[1]))
        except:
            continue
        
        
        spatPhaseArray = [""] * numSpatPhases
        
        if (msgid == "0013"):
            intersectionID = msg()['value'][1]['intersections'][0]['id']['id']
            intersectionName = msg()['value'][1]['intersections'][0]['name']
            spatTimestamp = msg()['value'][1]['intersections'][0]['timeStamp']
            instersectionPhaseArray = msg()['value'][1]['intersections'][0]['states']
            #print("Length instersectionPhaseArray: " + str(len(instersectionPhaseArray)))
            
            for phase in range(len(instersectionPhaseArray)):
            	
                currentPhase = msg()['value'][1]['intersections'][0]['states'][phase].get('signalGroup')
                currentState = str(msg()['value'][1]['intersections'][0]['states'][phase]['state-time-speed'][0]['eventState'])
                #print("Phase: " + str(currentPhase))
                #print("  State: " + currentState)
                spatPhaseArray[currentPhase] = currentState
            
            spatString = str(dt[0]) + "," + str(spatTimestamp) + "," + str(intersectionID) + "," + intersectionName 
            
            for printPhase in range(1,numSpatPhases):
                spatString = spatString + "," + spatPhaseArray[printPhase]
            spatString = spatString + "\n"
            
            #print(spatString)
            
            fout.write(spatString)

        elif (msgid == "0012"):
            intersectionID = msg()['value'][1]['intersections'][0]['id']['id']
            #if intersectionID == intersection:
            lat = msg()['value'][1]['intersections'][0]['refPoint']['lat']
            long = msg()['value'][1]['intersections'][0]['refPoint']['long']
            laneWidth = msg()['value'][1]['intersections'][0]['laneWidth']
            fout.write(str(dt[0])+','+str(intersectionID)+','+str(lat/10000000.0)+','+str(long/10000000.0)+','+str(laneWidth)+','+str(dt[1])+'\n')

        elif (msgid == "0014"): # if bsm , look for lat, long, speed along with time
            lat= msg()['value'][1]['coreData']['lat']
            long = msg()['value'][1]['coreData']['long']
            speed = msg()['value'][1]['coreData']['speed']
            elevation = msg()['value'][1]['coreData']['elev']
            secMark = msg()['value'][1]['coreData']['secMark']
            heading = msg()['value'][1]['coreData']['heading']
            #print("Heading: " + str(heading))
            speed_converted = speed*0.02 #m/s
            accel_long = msg()['value'][1]['coreData']['accelSet']['long']
            accel_long_converted = accel_long*0.01 #m^s^2
            
            #print(" ")
            #print("dt[0]: " + dt[0])
            #print("secMark: " + str(secMark))
            packet_timestamp = datetime.datetime.fromtimestamp(int(float(dt[0])))
            #print("packet_timestamp: " + str(packet_timestamp))
            roundDownMinTime = datetime.datetime(packet_timestamp.year,packet_timestamp.month,packet_timestamp.day,packet_timestamp.hour,packet_timestamp.minute).timestamp()
            #print("roundDownMinTime: " + str(roundDownMinTime))
            packetSecondsAfterMin = (float(dt[0]) - roundDownMinTime)
            #print("packetSecondsAfterMin: " + str(packetSecondsAfterMin))
            latency = packetSecondsAfterMin*1000 - secMark
            if(latency < 0):
                #print("[!!!] Minute mismatch")
                latency = latency + 60000
            #print("latency: " + str(latency))
            
            latency_array.append(latency);
            
            fout.write(str(dt[0])+','+str(secMark)+','+str(latency)+','+str(lat/10000000.0)+','+str(long/10000000.0)+','+str(speed_converted)+','+str(heading)+','+str(accel_long_converted)+','+ str(elevation)+','+str(dt[1])+'\n')
        else:
            sys.exit("Invalid message type")

if (msgid == "0014"): 
    print("")
    print("---------- Performance Metrics ----------")
    latency_avg = numpy.average(latency_array)
    print("Latency Average: " + str(latency_avg))
    latency_std = numpy.std(latency_array)
    print("Latency Standard Deviation (Jitter): " + str(latency_std))


