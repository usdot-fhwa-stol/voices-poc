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

from binascii import unhexlify
# import J2735_201603_combined
import J2735_201603_combined_voices_mr_fix as J2735
import json
import sys
import csv
import numpy
import datetime

print("\n----- DECODING J2735 PACKETS -----")

# print("\nARG LIST:")
# for i, arg in enumerate(sys.argv):
#     print(str(i) + ": " + str(arg))
# print("")

inFile = sys.argv[1]
outfile = sys.argv[2]

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

def convID(id, length):
    id = id.hex()
    i = 0
    if (length == 8):
        while(i<21):
            id = id[:i+2] + " " + id[i+2:]
            i += 3
    else:
        while(i<45):
            id = id[:i+2] + " " + id[i+2:]
            i += 3

    id = list(id.split(" "))

    for x in range(len(id)):
        inted = int(id[x], 16)
        id[x] = inted

    return id


infile_obj = open(inFile,'r')

bsm_outfile_obj         = open(outfile.replace(".csv","_BSM.csv"),'w',newline='')
spat_outfile_obj        = open(outfile.replace(".csv","_SPAT.csv"),'w',newline='')
map_outfile_obj         = open(outfile.replace(".csv","_MAP.csv"),'w',newline='')
mob_req_outfile_obj     = open(outfile.replace(".csv","_Mobility-Request.csv"),'w',newline='')
mob_resp_outfile_obj    = open(outfile.replace(".csv","_Mobility-Response.csv"),'w',newline='')
mob_path_outfile_obj    = open(outfile.replace(".csv","_Mobility-Path.csv"),'w',newline='')
mob_ops_outfile_obj     = open(outfile.replace(".csv","_Mobility-Operations.csv"),'w',newline='')
platooning_outfile_obj  = open(outfile.replace(".csv","_Platooning.csv"),'w',newline='')
tcr_outfile_obj         = open(outfile.replace(".csv","_Traffic-Control-Request.csv"),'w',newline='')
tcm_outfile_obj         = open(outfile.replace(".csv","_Traffic-Control-Message.csv"),'w',newline='')

bsm_outfile_writer         = csv.writer(bsm_outfile_obj)
spat_outfile_writer        = csv.writer(spat_outfile_obj)
map_outfile_writer         = csv.writer(map_outfile_obj)
mob_req_outfile_writer     = csv.writer(mob_req_outfile_obj)
mob_resp_outfile_writer    = csv.writer(mob_resp_outfile_obj)
mob_path_outfile_writer    = csv.writer(mob_path_outfile_obj)
mob_ops_outfile_writer     = csv.writer(mob_ops_outfile_obj)
platooning_outfile_writer  = csv.writer(platooning_outfile_obj)
tcr_outfile_writer         = csv.writer(tcr_outfile_obj)
tcm_outfile_writer         = csv.writer(tcm_outfile_obj)

numSpatPhases = 31 #use one more than desired phases


bsm_outfile_writer.writerow(["packetIndex","packetTimestamp","bsm id","secMark","latency","latitude","longitude","speed(m/s)","heading","elevation(m)","accel_long(m/s^2)","hex"])

spatColumnHeaderList=["packetIndex","packetTimestamp","spatTimestamp","intersectionID","intersectionName"]
for headerPhase in range(1,numSpatPhases):
    spatColumnHeaderList.append("phase" + str(headerPhase) + "_eventState")
spatColumnHeaderList.append("hex")
spat_outfile_writer.writerow(spatColumnHeaderList)

map_outfile_writer.writerow(["packetIndex","packetTimestamp","intersectionID","hex"])  
mob_req_outfile_writer.writerow(["packetIndex","packetTimestamp","headerTimestamp","hostStaticId","hostBSMId","planId","strategy","planType","urgency","strategyParams","trajectoryStart","trajectory","expiration"])
mob_resp_outfile_writer.writerow(["packetIndex","packetTimestamp","headerTimestamp","hostStaticId","hostBSMId","planId","urgency","isAccepted"])
mob_path_outfile_writer.writerow(["packetIndex","packetTimestamp","hostStaticId","hostBSMId","planId","location","trajectory"])
mob_ops_outfile_writer.writerow(["packetIndex","packetTimestamp","headerTimestamp","hostStaticId","hostBSMId","planId","strategy","operationParams"])
platooning_outfile_writer.writerow(["platooningPacketType","packetIndex","packetTimestamp","headerTimestamp","hostStaticId","hostBSMId","planId","strategy","other_params"])
tcr_outfile_writer.writerow(["packetIndex","packetTimestamp","reqid_hex","reqid_dec_list","reqseq","scale","bounds"])
tcm_outfile_writer.writerow(["packetIndex","packetTimestamp","reqid_hex","reqid_dec_list","reqseq","msgtot","msgnum","tcmID_hex","tcmID_dec_list","updated","label","tcID_hex","tcID_dec_list","vclasses","schedule","detail","geometry"])


infile_reader = csv.reader(infile_obj,delimiter=',')
packet_list = list(infile_reader)[1:]

latency_array = []
prevSpatTimestamp = 0

trimmed_packet_column = 5
message_type_id_column = 4

for packet in packet_list:

    msg = J2735.DSRC.MessageFrame
    #print("hex: " + packet[trimmed_packet_column] + " byte length: " + str(len(packet[trimmed_packet_column])))
    try:
        msg.from_uper(unhexlify(packet[trimmed_packet_column]))
    except Exception as e:
        print("\n  DECODING ERROR: " + str(e))
        print("    [" + str(packet[0])+'] ' + str(packet[2]) )
        continue

    if (packet[message_type_id_column] == "0013") :
        # print("Parsing SPAT")

        spatPhaseArray = [""] * numSpatPhases
        intersectionID = msg()['value'][1]['intersections'][0]['id']['id']
        intersectionName = msg()['value'][1]['intersections'][0]['name']
        spatTimestamp = msg()['value'][1]['intersections'][0]['timeStamp']
        instersectionPhaseArray = msg()['value'][1]['intersections'][0]['states']
        
        for phase in range(len(instersectionPhaseArray)):
            currentPhase = msg()['value'][1]['intersections'][0]['states'][phase].get('signalGroup')
            currentState = str(msg()['value'][1]['intersections'][0]['states'][phase]['state-time-speed'][0]['eventState'])
            spatPhaseArray[currentPhase] = currentState
        
        spatRowList = [str(packet[0]),str(packet[1]),str(spatTimestamp),str(intersectionID),intersectionName ]
        
        for printPhase in range(1,numSpatPhases):
            spatRowList.append(spatPhaseArray[printPhase])
        spatRowList.append(str(packet[trimmed_packet_column]))
        
        spat_outfile_writer.writerow(spatRowList)

    elif (packet[message_type_id_column] == "0012") :
        # print("Parsing MAP")

        intersectionID = msg()['value'][1]['intersections'][0]['id']['id']
        #if intersectionID == intersection:
        lat = msg()['value'][1]['intersections'][0]['refPoint']['lat']
        longstr = msg()['value'][1]['intersections'][0]['refPoint']['long']
        laneWidth = msg()['value'][1]['intersections'][0]['laneWidth']
        map_outfile_writer.writerow([str(packet[0]),str(packet[1]),str(intersectionID),str(lat/10000000.0),str(longstr/10000000.0),str(laneWidth),str(packet[trimmed_packet_column])])

    elif (packet[message_type_id_column] == "0014") : # if bsm , look for lat, long, speed along with time
        # print("Parsing BSM")
        bsmId = msg()['value'][1]['coreData']['id']
        lat= msg()['value'][1]['coreData']['lat']
        longstr = msg()['value'][1]['coreData']['long']
        speed = msg()['value'][1]['coreData']['speed']
        elevation = msg()['value'][1]['coreData']['elev']
        secMark = msg()['value'][1]['coreData']['secMark']
        heading = msg()['value'][1]['coreData']['heading']
        speed_converted = speed*0.02 #m/s
        accel_long = msg()['value'][1]['coreData']['accelSet']['long']
        accel_long_converted = accel_long*0.01 #m^s^2
        
        packet_timestamp = datetime.datetime.fromtimestamp(int(float(packet[0])))
        roundDownMinTime = datetime.datetime(packet_timestamp.year,packet_timestamp.month,packet_timestamp.day,packet_timestamp.hour,packet_timestamp.minute).timestamp()
        packetSecondsAfterMin = (float(packet[0]) - roundDownMinTime)
        latency = packetSecondsAfterMin*1000 - secMark
        if (latency < 0) :
            #print("[!!!] Minute mismatch")
            latency = latency + 60000
        #print("latency: " + str(latency))
        
        latency_array.append(latency)
        
        bsm_outfile_writer.writerow([str(packet[0]),str(packet[1]),str(bsmId.hex()),str(secMark),str(latency),str(lat/10000000.0),str(longstr/10000000.0),str(speed_converted),str(heading),str(accel_long_converted), str(elevation),str(packet[trimmed_packet_column])])

    elif (packet[message_type_id_column] == "00f0") :
        # print("Parsing Mobility Request")

        hostStaticId = msg()['value'][1]['header']['hostStaticId']
        hostBSMId = msg()['value'][1]['header']['hostBSMId']
        planId = msg()['value'][1]['header']['planId']
        headerTimestamp = msg()['value'][1]['header']['timestamp']
        strategy = msg()['value'][1]['body']['strategy']
        planType = msg()['value'][1]['body']['planType']
        urgency = msg()['value'][1]['body']['urgency']
        strategyParams = str(msg()['value'][1]['body']['strategyParams'])
        trajectoryStart = str(msg()['value'][1]['body']['trajectoryStart'])
        trajectory = msg()['value'][1]['body']['trajectory']
        expiration = msg()['value'][1]['body']['expiration']

        mob_req_outfile_writer.writerow([str(packet[0]),str(packet[1]), str(headerTimestamp),str(hostStaticId),str(hostBSMId),str(planId),str(strategy),str(planType),str(urgency),str(strategyParams),str(trajectoryStart),str(trajectory),str(expiration)])
        platooning_outfile_writer.writerow(["Mobility_Request" , str(packet[0]),str(packet[1]),str(hostStaticId),str(hostBSMId),str(planId),str(strategy),str(planType),str(urgency),str(strategyParams),str(trajectoryStart),str(trajectory),str(expiration)])

    elif (packet[message_type_id_column] == "00f1") :
        # print("Parsing Mobility Response")

        hostStaticId = msg()['value'][1]['header']['hostStaticId']
        hostBSMId = msg()['value'][1]['header']['hostBSMId']
        planId = msg()['value'][1]['header']['planId']
        headerTimestamp = msg()['value'][1]['header']['timestamp']
        urgency = msg()['value'][1]['body']['urgency']
        isAccepted = msg()['value'][1]['body']['isAccepted']

        mob_resp_outfile_writer.writerow([str(packet[0]),str(packet[1]), str(headerTimestamp),str(hostStaticId),str(hostBSMId),str(planId),str(urgency),str(isAccepted)])
        platooning_outfile_writer.writerow(["Mobility_Response",str(packet[0]),str(packet[1]),str(hostStaticId),str(hostBSMId),str(planId),str(urgency),str(isAccepted)])

    elif (packet[message_type_id_column] == "00f2") :
        # print("Parsing Mobility Path")

        hostStaticId = msg()['value'][1]['header']['hostStaticId']
        hostBSMId = msg()['value'][1]['header']['hostBSMId']
        planId = msg()['value'][1]['header']['planId']
        location = msg()['value'][1]['body']['location']
        trajectory = msg()['value'][1]['body']['trajectory']

        mob_path_outfile_writer.writerow([str(packet[0]),str(packet[1]),str(hostStaticId),str(hostBSMId),str(planId),str(location),str(trajectory)])

    elif (packet[message_type_id_column] == "00f3") :
        # print("Parsing Mobility Operations")

        hostStaticId = msg()['value'][1]['header']['hostStaticId']
        hostBSMId = msg()['value'][1]['header']['hostBSMId']
        planId = msg()['value'][1]['header']['planId']
        headerTimestamp = msg()['value'][1]['header']['timestamp']
        strategy = msg()['value'][1]['body']['strategy']
        operationParams = msg()['value'][1]['body']['operationParams']
        
        mob_ops_outfile_writer.writerow([str(packet[0]),str(packet[1]), str(headerTimestamp) ,str(hostStaticId),str(hostBSMId),str(planId),str(strategy),str(operationParams)])
        platooning_outfile_writer.writerow(["Mobility_Operations",str(packet[0]),str(packet[1]),str(hostStaticId),str(hostBSMId),str(planId),str(strategy),str(operationParams)])

    elif (packet[message_type_id_column] == "00f4") :
        # print("Parsing Mobility TCR")

        reqid = msg()['value'][1]['body'][1]['reqid']
        reqseq = msg()['value'][1]['body'][1]['reqseq']
        scale = msg()['value'][1]['body'][1]['scale']
        bounds = msg()['value'][1]['body'][1]['bounds']

        newReqId = str(convID(reqid, 8)).replace(",", " ")
        reqid = reqid.hex()
        

        tcr_outfile_writer.writerow([str(packet[0]),str(packet[1]),reqid,newReqId,str(reqseq),str(scale),str(bounds),str(packet[trimmed_packet_column])])
    
    elif (packet[message_type_id_column] == "00f5") :
        # print("Parsing TCM")
        
        reqid = msg()['value'][1]['body'][1]['reqid']
        reqseq = msg()['value'][1]['body'][1]['reqseq']
        msgtot = msg()['value'][1]['body'][1]['msgtot']
        msgnum = msg()['value'][1]['body'][1]['msgnum']
        tcmId = msg()['value'][1]['body'][1]['id']
        updated = msg()['value'][1]['body'][1]['updated']
        label = msg()['value'][1]['body'][1]['package']['label']
        tcId = msg()['value'][1]['body'][1]['package']['tcids'][0]
        vclasses = msg()['value'][1]['body'][1]['params']['vclasses']
        schedule = msg()['value'][1]['body'][1]['params']['schedule']
        detail = msg()['value'][1]['body'][1]['params']['detail']
        geometry = msg()['value'][1]['body'][1]['geometry']

        newReqId = str(convID(reqid, 8)).replace(",", " ")
        newTcmId = str(convID(tcmId, 16)).replace(",", " ")
        newtcId = str(convID(tcId, 16)).replace(",", " ")
        
        reqid = reqid.hex()
        tcmId = tcmId.hex()
        tcId = tcId.hex()
        

        tcm_outfile_writer.writerow([str(packet[0]),str(packet[1]),reqid,newReqId,str(reqseq),str(msgtot),str(msgnum),tcmId,newTcmId,str(updated),str(label),tcId,newtcId,str(vclasses),str(schedule),str(detail),str(geometry),str(packet[trimmed_packet_column])])
    else:
        print("\nERROR: NO MATCHING MESSAGE TYPES FOR PAYLOAD: ")
        print("[" + str(packet[0])+'] ' + str(packet[2]) )



# if (payload_type_id == "0014") : 
#     print("")
#     print("---------- Performance Metrics ----------")
#     latency_avg = numpy.average(latency_array)
#     print("Latency Average: " + str(latency_avg))
#     latency_std = numpy.std(latency_array)
#     print("Latency Standard Deviation (Jitter): " + str(latency_std))

