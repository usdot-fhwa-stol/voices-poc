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


import json
import sys
from csv import reader, writer
import re

print("\nARG LIST:")
for i, arg in enumerate(sys.argv):
    print(str(i) + ": " + str(arg))
print("")

#print("ARGS: " + sys.argv[0] + "," + sys.argv[1] + "," + sys.argv[2] + "," + sys.argv[3] + "," + sys.argv[4])
inFile = sys.argv[1]
outfile = sys.argv[2]
# payload_type_id=sys.argv[3]


message_type_list = [
    {
        'name'  : 'MAP',
        'id'    : '0012'
    },
    {
        'name'  : 'SPAT',
        'id'    : '0013'
    },
    {
        'name'  : 'BSM',
        'id'    : '0014'
    },
    {
        'name'  : 'Mobility Request',
        'id'    : '00f0'
    },
    {
        'name'  : 'Mobility Response',
        'id'    : '00f1'
    },
    {
        'name'  : 'Mobility Path',
        'id'    : '00f2'
    },
    {
        'name'  : 'Mobility Operations',
        'id'    : '00f3'
    },
    {
        'name'  : 'TraffiC Control Request',
        'id'    : '00f4'
    },
    {
        'name'  : 'TraffiC Control Message',
        'id'    : '00f5'
    }
]

with open(inFile) as read_obj, \
open(outfile, 'w', newline='') as write_obj:
    csv_reader = reader(read_obj)
    csv_writer = writer(write_obj)

    # substr = {
    #     'map': '0012',
    #     'spat':'0013',
    #     'bsm': '0014',
    #     'req': '00f0',
    #     'res': '00f1',
    #     'mop': '00f2',
    #     'mom': '00f3',
    #     'tcr': '00f4',
    #     'tcm': '00f5'
    # }

    # for row in csv_reader:
    #     index = {}
    #     smallerIndex = 10000
        
    #     #remove newlines for ascii
    #     if payloadType == "ascii":
    #         row[1] = row[1].replace("\\n","")
        
    #     for k in substr:
    #         if substr[k] in row[1]:
    #             index[k] = row[1].find(substr[k])
    #             if index[k] < smallerIndex:
    #                 smallerIndex = index[k]
    #                 msg = row[1][smallerIndex:]
        
    #     csv_writer.writerow([row[0],msg])

    found_packets = 0

    csv_writer.writerow(["packet_index","timestamp","frame_raw","message_type","message_type_id","filtered_payload"])

    #skip first row for headers
    next(csv_reader)

    for row in csv_reader:
        
        packet_index = row[0]
        timestamp = row[1]
        current_packet_frame_raw = row[2]

        # print("packet_index: " + str(packet_index))
        # print("timestamp: " + str(timestamp))
        # print("current_packet_frame_raw: " + str(current_packet_frame_raw))
        
        #this is the message type id which appears closest to the header
        #this starts at an arbitrary value
        closest_message_type = {
            "name"  : "NA",
            "id"    : "0000",
            "pos"   : 99999   
        }

        num_matching_message_types = 0

        for message_type in message_type_list:
            
            j2735_payload_with_header_search = re.search('0380.*'+ message_type['id'],current_packet_frame_raw)

            # print("Search: " + str(j2735_payload_with_header_search))
            
            if j2735_payload_with_header_search != None:
                # print("Found: " + message_type['name'])
                num_matching_message_types += 1

                j2735_payload_with_header = str(j2735_payload_with_header_search.group(0))
                search_result_start = j2735_payload_with_header_search.start()
                search_result_end = j2735_payload_with_header_search.end()
                # print("Start: " + str(search_result_start))
                # print("End: " + str(search_result_end))
                # print("With Header: " + str(j2735_payload_with_header))
                
                if search_result_end < closest_message_type["pos"]:
                    closest_message_type["name"] = message_type['name']
                    closest_message_type["id"] = message_type['id']
                    closest_message_type["pos"] = search_result_end
        # print("num_matching_message_types: " + str(num_matching_message_types))
            
                
        # print("Closest Message Type: " + closest_message_type["name"])

        final_j2735_payload_with_header_search = re.search('0380.*'+ closest_message_type['id'] + '.*',current_packet_frame_raw)
        final_j2735_payload_with_header = str(final_j2735_payload_with_header_search.group(0))
        final_j2735_payload_with_header_cleaned_search = re.search(closest_message_type['id'] + '.*',final_j2735_payload_with_header)
        final_j2735_payload_with_header_cleaned = str(final_j2735_payload_with_header_cleaned_search.group(0))
                
        # print("Timestamp: " + timestamp)
        # print("Clean: " + final_j2735_payload_with_header_cleaned)

        csv_writer.writerow([packet_index,timestamp,current_packet_frame_raw,closest_message_type["name"],closest_message_type["id"],final_j2735_payload_with_header_cleaned])

        # print("")


# Old for Kapsch payloads. Testing with Kapsch payloads needed to include in updated 

        # if "Kapsch" in fileName[0] and bsm_substr in row[2]:
        #     bsm_index = row[2].find(bsm_substr)
        #     bsm_length = len(row[2])

        # elif spat_index < map_index and spat_index < bsm_index and "mk5" in fileName[0] and "rx" in fileName[0]:
        #     spat = row[1][spat_index:spat_length-8]
        #     csv_writer.writerow([row[0], spat])
        # if bsm_index < map_index and bsm_index < spat_index and "CohdaRSU_rx" in fileName[0]:
        #     bsm = row[1][bsm_index:bsm_length-8]
        #     csv_writer.writerow([row[0], bsm])
        # elif bsm_index < map_index and bsm_index < spat_index and "Kapsch" in fileName[0]:
        #     bsm = row[2][bsm_index:]
        #     csv_writer.writerow([row[0], bsm])
