# import json
import sys
import csv
# import numpy
import datetime
import math
import re

print("\n==========================================================")
print(  "========== STARTING VOICES PERFORMANCE ANALYSIS ==========")
print(  "==========================================================")

############################## DEFINE GENERAL VARIABLES ##############################

sv_out_start = 0
sv_out_to_v2xhub_in_offset = 0
sv_out_to_v2xhub_tdcs_offset = 0

all_data = []

# example schema for all_data
# all_data = [
#     {
#         "dataset_name"              : "some_dataset_name",
#         "data_order"                : 1,
#         "original_data_list"        : [ {},{},{},{}... ],
#         "filtered_data_list"        : [ {},{},{},{}...  ],
#         "dataset_params"            : {},
#         "source_to_match_offset"    : int,
#     },
#     {
#         "dataset_name"              : "some_other_dataset_name",
#         "data_order"                : 2,
#         "original_data_list"        : [ {},{},{},{}... ],
#         "filtered_data_list"        : [ {},{},{},{}...  ],
#         "dataset_params"            : {},
#         "source_to_match_offset"    : int,
#     },
#     ...

# ]


# specifies the number of match_keys defined in the params for each data source
num_match_keys = 5

# specifies the message type to be analyzed
J2735_message_type_name = "BSM"

desired_bsm_id = "f03ad610"

desired_tena_identifier = "CARMA-TFHRC-LIVE"

# ############################## LOAD IN SOURCE VEHICLE DATA ##############################

# print("\n----- LOADING DATA FOR SOURCE VEHICLE -----")

# source_out_pcap_file = "source_vehicle_data/lead_carma_platform_out_decoded_packets_BSM.csv"

# source_vehicle_out_data_infile_obj = open(source_out_pcap_file,'r')
# source_vehicle_out_data_infile_reader = csv.DictReader(source_vehicle_out_data_infile_obj,delimiter=',')
# source_vehicle_out_data_infile_headers = source_vehicle_out_data_infile_reader.fieldnames
# # print("source_vehicle_data_infile_headers: " + str(source_vehicle_out_data_infile_headers))

# source_vehicle_out_data_list = list(source_vehicle_out_data_infile_reader)
# total_source_vehicle_out_packets = len(source_vehicle_out_data_list)

# print("Total Source Vehicle Packets: " + str(total_source_vehicle_out_packets))

# ############################## LOAD IN V2X HUB DATA ##############################

# print("\n----- LOADING DATA FOR V2X-HUB IN PCAP DATA -----")

# v2xhub_in_pcap_file = "v2xhub_data/v2xhub_in_decoded_packets_BSM.csv"

# v2xhub_pcap_in_data_infile_obj = open(v2xhub_in_pcap_file,'r')
# v2xhub_pcap_in_data_infile_reader = csv.DictReader(v2xhub_pcap_in_data_infile_obj,delimiter=',')
# v2xhub_pcap_in_data_infile_headers = v2xhub_pcap_in_data_infile_reader.fieldnames
# # print("v2xhub_data_infile_headers: " + str(v2xhub_pcap_in_data_infile_headers))

# v2xhub_pcap_in_data_list = list(v2xhub_pcap_in_data_infile_reader)
# total_v2xhub_in_packets = len(v2xhub_pcap_in_data_list)

# print("Total Packets: " + str(total_v2xhub_in_packets))

# ############################## LOAD IN V2X-HUB TDCS DATA ##############################

# print("\n----- LOADING DATA FOR V2X-HUB TDCS DATA -----")

# v2xhub_in_tdcs_file = "v2xhub_data/VUG-Track-BSM-20220822124130.csv"

# v2xhub_tdcs_data_infile_obj = open(v2xhub_in_tdcs_file,'r')
# v2xhub_tdcs_data_infile_reader = csv.DictReader(v2xhub_tdcs_data_infile_obj,delimiter=',')
# v2xhub_tdcs_data_infile_headers = v2xhub_tdcs_data_infile_reader.fieldnames
# # print("v2xhub_tdcs_data_infile_headers: " + str(v2xhub_tdcs_data_infile_headers))

# v2xhub_tdcs_data_list = list(v2xhub_tdcs_data_infile_reader)
# total_v2xhub_tdcs_packets = len(v2xhub_tdcs_data_list)

# print("Total Packets: " + str(total_v2xhub_tdcs_packets))

# ############################## LOAD IN DEST VEHICLE TDCS DATA ##############################

# print("\n----- LOADING DATA FOR DEST VEH TDCS DATA -----")

# dest_veh_tdcs_file = "destination_vehicle_data/VUG-Track-BSM-20220822125045.csv"

# dest_veh_tdcs_data_infile_obj = open(dest_veh_tdcs_file,'r')
# dest_veh_tdcs_data_infile_reader = csv.DictReader(dest_veh_tdcs_data_infile_obj,delimiter=',')
# dest_veh_tdcs_data_infile_headers = dest_veh_tdcs_data_infile_reader.fieldnames
# # print("dest_veh_tdcs_data_infile_headers: " + str(dest_veh_tdcs_data_infile_headers))

# dest_veh_tdcs_data_list = list(dest_veh_tdcs_data_infile_reader)
# total_dest_veh_tdcs_packets = len(dest_veh_tdcs_data_list)

# print("Total Packets: " + str(total_dest_veh_tdcs_packets))

# ############################## LOAD IN DEST VEH PCAP DATA ##############################

# print("\n----- LOADING DATA FOR DEST VEH IN PCAP DATA -----")

# dest_veh_in_pcap_file = "destination_vehicle_data/second_carma_platform_in_decoded_packets_BSM.csv"

# dest_veh_pcap_in_data_infile_obj = open(dest_veh_in_pcap_file,'r')
# dest_veh_pcap_in_data_infile_reader = csv.DictReader(dest_veh_pcap_in_data_infile_obj,delimiter=',')
# dest_veh_pcap_in_data_infile_headers = dest_veh_pcap_in_data_infile_reader.fieldnames
# # print("dest_veh_data_infile_headers: " + str(dest_veh_pcap_in_data_infile_headers))

# dest_veh_pcap_in_data_list = list(dest_veh_pcap_in_data_infile_reader)
# total_dest_veh_in_packets = len(dest_veh_pcap_in_data_list)

# print("Total Packets: " + str(total_dest_veh_in_packets))


############################## DEFINE DATA PARAMS ##############################

# defines the required fields to be used in analysis for each message type
# skip if keys and values are used to skip non-relevant data (collected before run started, for different vehicle)
# match_keys are the data columns that will be used to verify the data matches

data_params = {
    "pcap_params" :{
        "BSM" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "bsm id",         # key(column) to check
                    "value"         : desired_bsm_id,   # value to check
                    "round"         : False,            # round the value before checking (important for TENA data)
                # "round_decimals": 0,                # decimal places to round to (only needed if round == True, shown here for example)
                    "start_only"    : False,            # only skip through rows matching this condition to align the start of the data set 
                                                        #    had to add this becuase we want to use speed == 0 to find the start of the data (when the vehicle starts moving)
                                                        #    but we do not want to throw out any values which contain speed == 0 (vehicle stops during run)
                }

            ],
            
            "skip_if_eqs"       : [
                {
                    "key"    : "speed(m/s)",
                    "value"  : "0.0",
                    "round" : True,
                    "round_decimals": 2,
                    "start_only" : True, 
                }
            ],

            "match_keys"        : [
                {
                    "key"       : "latitude",
                    "round"     : True,
                    "round_decimals": 7,
                    "buffer"    : 0.0000001,
                    "radians"   : False,
                },
                {
                    "key"       : "longitude",
                    "round"     : True,
                    "round_decimals": 7,
                    "buffer"    : 0.0000001,
                    "radians"   : False,
                },
                {
                    # "key"       : "heading",
                    "key"       : None,
                    "round"     : False,
                    "radians"   : False,
                    "round_decimals": 6,
                    # "buffer"    : 0.0000001,
                    "j2735_heading": True,
                },
                {
                    "key"       : "secMark",
                    "round"     : False,
                    "radians"   : False,
                },
                {
                    "key"       : None,
                    "round"     : False,
                    "radians"   : False,
                }
            ]

            
        }
    },
    "tdcs_params" : {
        "BSM" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "const^identifier,String",
                    "value"         : desired_tena_identifier,
                    "round"         : False,
                    "start_only"    : False, 
                }

            ],
            
            "skip_if_eqs"       : [
                {
                    "key"           : "tspi.velocity.ltpENU_asTransmitted.vxInMetersPerSecond,Float32 (optional)",
                    "value"         : "0.0",
                    "round"         : True,
                    "round_decimals": 2,
                    "start_only"    : True, 
                },
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Discovery",
                    "round" : False,
                    "start_only" : False, 
                }
            ],

            
            
            "match_keys"        : [
                {
                    "key"       : "tspi.velocity.ltpENU_asTransmitted.srf.latitudeInDegrees,Float64 (optional)",
                    "round"     : True,
                    "round_decimals": 7,
                    "buffer"    : 0.0000001,
                    "radians"   : False
                },
                {
                    "key"       : "tspi.velocity.ltpENU_asTransmitted.srf.longitudeInDegrees,Float64 (optional)",
                    "round"     : True,
                    "round_decimals": 7,
                    "buffer"    : 0.0000001,
                    "radians"   : False
                },
                {
                    #"key"       : "tspi.orientation.frdWRTltpENUbodyFixedZYX_asTransmitted.srf.azimuthInRadians,Float64 (optional)",
                    "key"       : None,
                    "round"     : True,
                    "round_decimals": 6,
                    # "buffer"    : 0.0000001,
                    "radians"   : True
                },
                {
                    "key"       : "msWithinMinute,UInt16",
                    "round"     : False,
                    "radians"   : False
                },
                {
                    "key"       : None,
                    "round"     : False,
                    "radians"   : False
                }
            ]
        }
    }
}

pcap_params = {
    "BSM" : {
        "skip_if_neqs"      : [
            {
                "key"           : "bsm id",         # key(column) to check
                "value"         : desired_bsm_id,   # value to check
                "round"         : False,            # round the value before checking (important for TENA data)
              # "round_decimals": 0,                # decimal places to round to (only needed if round == True, shown here for example)
                "start_only"    : False,            # only skip through rows matching this condition to align the start of the data set 
                                                    #    had to add this becuase we want to use speed == 0 to find the start of the data (when the vehicle starts moving)
                                                    #    but we do not want to throw out any values which contain speed == 0 (vehicle stops during run)
            }

        ],
        
        "skip_if_eqs"       : [
            {
                "key"    : "speed(m/s)",
                "value"  : "0.0",
                "round" : True,
                "round_decimals": 2,
                "start_only" : True, 
            }
        ],

        "match_keys"        : [
            {
                "key"       : "latitude",
                "round"     : True,
                "round_decimals": 7,
                "buffer"    : 0.0000001,
                "radians"   : False,
            },
            {
                "key"       : "longitude",
                "round"     : True,
                "round_decimals": 7,
                "buffer"    : 0.0000001,
                "radians"   : False,
            },
            {
                # "key"       : "heading",
                "key"       : None,
                "round"     : False,
                "radians"   : False,
                "round_decimals": 6,
                # "buffer"    : 0.0000001,
                "j2735_heading": True,
            },
            {
                "key"       : "secMark",
                "round"     : False,
                "radians"   : False,
            },
            {
                "key"       : None,
                "round"     : False,
                "radians"   : False,
            }
        ]

        
    }
}

tdcs_params = {
    "BSM" : {
        "skip_if_neqs"      : [
            {
                "key"           : "const^identifier,String",
                "value"         : desired_tena_identifier,
                "round"         : False,
                "start_only"    : False, 
            }

        ],
        
        "skip_if_eqs"       : [
            {
                "key"           : "tspi.velocity.ltpENU_asTransmitted.vxInMetersPerSecond,Float32 (optional)",
                "value"         : "0.0",
                "round"         : True,
                "round_decimals": 2,
                "start_only"    : True, 
            },
            {
                "key"   : "Metadata,Enum,Middleware::EventType",
                "value" : "Discovery",
                "round" : False,
                "start_only" : False, 
            }
        ],

        
        
        "match_keys"        : [
            {
                "key"       : "tspi.velocity.ltpENU_asTransmitted.srf.latitudeInDegrees,Float64 (optional)",
                "round"     : True,
                "round_decimals": 7,
                "buffer"    : 0.0000001,
                "radians"   : False
            },
            {
                "key"       : "tspi.velocity.ltpENU_asTransmitted.srf.longitudeInDegrees,Float64 (optional)",
                "round"     : True,
                "round_decimals": 7,
                "buffer"    : 0.0000001,
                "radians"   : False
            },
            {
                #"key"       : "tspi.orientation.frdWRTltpENUbodyFixedZYX_asTransmitted.srf.azimuthInRadians,Float64 (optional)",
                "key"       : None,
                "round"     : True,
                "round_decimals": 6,
                # "buffer"    : 0.0000001,
                "radians"   : True
            },
            {
                "key"       : "msWithinMinute,UInt16",
                "round"     : False,
                "radians"   : False
            },
            {
                "key"       : None,
                "round"     : False,
                "radians"   : False
            }
        ]
    }
}

############################## INITIALIZE CSV WRITER ##############################

outfile = "performance_analysis.csv"
results_outfile_obj = open(outfile,'w',newline='')
results_outfile_writer = csv.writer(results_outfile_obj)

# write headers

outfile_headers =     [
      "sv_packet_index", "v2x_in_packet_index", "v2x_tdcs_rowID", "dest_veh_tdcs_rowID", 
      "sv_out_timestamp", "v2x_in_timestamp", 
      "v2x_tdcs_time_of_creation", "v2x_tdcs_time_of_commit", "v2x_tdcs_time_of_receipt", 
      "dest_veh_tdcs_time_of_creation", "dest_veh_tdcs_time_of_commit", "dest_veh_tdcs_time_of_receipt", 
      "bsm_broadcast_latency", "v2x_adjusted_timestamp","sv_to_v2x_latency", "j2735_to_sdo_conversion_time", "tena_packet_latency", "sdo_to_j2735_latency"
    ]

results_outfile_writer.writerow(outfile_headers)


############################## SET CLOCK SKEWS ##############################

virtual_to_nist_clock_skew = -51.729
live_to_nist_clock_skew = 60.723

v2x_to_virtual_clock_skew = 43.712
v2x_to_second_clock_skew = -213.336
v2x_to_third_clock_skew = -0.990


sv_to_v2x_clock_skew = live_to_nist_clock_skew - (virtual_to_nist_clock_skew + v2x_to_virtual_clock_skew)
print("\nsv_to_v2x_clock_skew: " + str(sv_to_v2x_clock_skew))

# checks if value is a number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# finds the offset of two sources of data
def find_data_row_offset(data_to_search):
    
    search_starting_row = None
    source_to_match_offset = None
    cleaned_data_to_search_list = []
    
    
    if data_to_search["data_order"] != 1:
        source_data_obj_index = get_obj_by_key_value(all_data,"data_order",1)
        source_data_obj = all_data[source_data_obj_index]
        source_data_list_filtered = source_data_obj["filtered_data_list"]
        source_packet_to_match = source_data_list_filtered[0]
        source_packet_params = source_data_obj["dataset_params"]

    data_to_search_list = data_to_search["original_data_list"]
    data_to_search_params = data_to_search["dataset_params"]



    for search_i,search_packet in enumerate(data_to_search_list):

        # iterate through the neqs to check
        all_neqs_pass = True

        # print("\nLooking at data at index: " + source_packet_to_match["packetIndex"] + " : " + search_packet["packetIndex"])
        # print("\nLooking at data at index: " + str(search_packet))

        for current_neq in data_to_search_params[J2735_message_type_name]["skip_if_neqs"]:

            # skip if values are not equal (ex: checking for matching bsm id)
            search_packet_neq_value = search_packet[current_neq["key"]]
            neq_param_value = current_neq["value"]

            # print("NEQ CHECK: " + str(search_packet_neq_value) + " != " + str(neq_param_value))

            # if we have already found the start of the data set (and therefore the offset),
            # and the current neq is for the start_only, skip this neq
            if source_to_match_offset != None and current_neq["start_only"]:
                # print("Skipping NEQ since it is start only: " + current_neq["key"])
                continue


            # if the source_packet_value is a number and we want to round, round both values to the same number of decimals
            if is_number(search_packet_neq_value) and current_neq["round"]:
                    # print("Rounding NEQ Values")
                    search_packet_neq_value = round(float(search_packet_neq_value),current_neq["round_decimals"])
                    neq_param_value = round(float(neq_param_value),current_neq["round_decimals"])

            if search_packet_neq_value != neq_param_value:
                # print("Skipping non matching value: " + str(search_packet_neq_value) + " != " + str(neq_param_value))
                all_neqs_pass = False
                break
        
        if not all_neqs_pass:
            #print("Continuing because not all NEQs passed")
            
            # remove the bad data from the array so we do not encounter it later
            # the pop function is a change in place and therefore the original array is modified
            if source_to_match_offset != None:
                source_to_match_offset -+ 1
            
            # data_to_search_list.pop(search_i)
            continue
        
        #iterate through the eqs to check
        all_eqs_pass = True

        for current_eq in data_to_search_params[J2735_message_type_name]["skip_if_eqs"]:

            # skip if values are equal (ex: skip if speed is 0)
            search_packet_eq_value = search_packet[current_eq["key"]]
            eq_param_value = current_eq["value"]

            # print("EQ CHECK: " + str(search_packet_eq_value) + " == " + str(eq_param_value))

            # if we have already found the start of the data set (and therefore the offset),
            # and the current eq is for the start_only, skip this neq
            if source_to_match_offset != None and current_eq["start_only"]:
                # print("Skipping EQ since it is start only: " + current_eq["key"])
                continue

            # if the source_packet_value is a number and we want to round, round both values to the same number of decimals
            if current_eq["round"]:
                    # print("Rounding EQ Values")
                    search_packet_eq_value = round(float(search_packet_eq_value),current_eq["round_decimals"])
                    eq_param_value = round(float(eq_param_value),current_eq["round_decimals"])

            if search_packet_eq_value == eq_param_value:
                # print("Skipping matching value: " + str(search_packet_eq_value) + " == " + str(eq_param_value))
                all_eqs_pass = False
                break
        
        if not all_eqs_pass:
            # print("Continuing because not all EQs passed")
            
            #remove the bad data from the array so we do not encounter it later
            # the pop function is a change in place and therefore the original array is modified
            if source_to_match_offset != None:
                source_to_match_offset -+ 1

            # data_to_search_list.pop(search_i)
            continue

        if search_starting_row == None:
            search_starting_row = search_i
            print("search_starting_row: " + str(search_starting_row))
        

        # since it was not eliminated from the NEQ and EQs, add the packet to the filtered data list
        # print("\nKeeping Packet: " + str(search_i))
        cleaned_data_to_search_list.append(search_packet)


        # if we are filtering the source data, we are not matching it against anything so skip this bottom part
        if data_to_search["data_order"] == 1:
            source_to_match_offset = 0
            continue
            # return source_offset



        # the first time all fields match, this is the start of the data we want
        # get the offset between the source start index and the search start index
        #
        # UPDATE:   with the new method of filtering out the data lists, ideally all lists index 0 align
        #           this might not always be the case (if the first valid packet was dropped) so we do this anyway

        if source_to_match_offset == None:

            all_fields_match = check_if_data_matches(source_packet_params,data_to_search_params,source_packet_to_match,search_packet)
            
            if all_fields_match:
                print("\nAll Fields match")
                source_to_match_offset = search_i - search_starting_row
                print("\nsource_to_match_offset = " + str(source_to_match_offset))
    

    # data_to_return = { 
    #     "cleaned_data_to_search_list" : cleaned_data_to_search_list,
    #     "source_to_match_offset" : source_to_match_offset
    # }

    data_to_search["filtered_data_list"] = cleaned_data_to_search_list
    data_to_search["source_to_match_offset"] = source_to_match_offset
    # return data_to_return

# checks all match params for two give packets
def check_if_data_matches(source_packet_params,data_to_search_params,source_packet_to_match,search_packet):

    all_fields_match = True

    for match_i in range(0,num_match_keys):
        source_packet_key = source_packet_params[J2735_message_type_name]["match_keys"][match_i]["key"]
        search_packet_key = data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["key"]

        # print("source_packet_key: " + str(source_packet_key))
        # print("search_packet_key: " + str(search_packet_key))

        # if the source or search packet match key are none. the same index of each match key should align. 
        # see definition at the top of the file for more info
        if (
                source_packet_key == None or
                search_packet_key == None
        ):
            # print("Skipping match key " + str(match_i) + " since one or more keys are None: " + str(source_packet_key) + "," + str(search_packet_key))
            continue

        
        source_packet_value = source_packet_to_match[source_packet_key]
        search_packet_value = search_packet[search_packet_key]

        if "j2735_heading" in source_packet_params[J2735_message_type_name]["match_keys"][match_i]:
            source_packet_value = float(source_packet_value)/80
        
        if "j2735_heading" in data_to_search_params[J2735_message_type_name]["match_keys"][match_i]:
            search_packet_value = float(search_packet_value)/80
            
        if source_packet_params[J2735_message_type_name]["match_keys"][match_i]["radians"]:
            source_packet_value = math.degrees(float(source_packet_value))
        
        if data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["radians"]:
            search_packet_value = math.degrees(float(search_packet_value))

        if source_packet_params[J2735_message_type_name]["match_keys"][match_i]["round"]:
            source_packet_value = round(float(source_packet_value),source_packet_params[J2735_message_type_name]["match_keys"][match_i]["round_decimals"])
        
        if data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["round"]:
            search_packet_value = round(float(search_packet_value),data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["round_decimals"])

        if  ( source_packet_value != search_packet_value ):
            
            #TODO this logic could be better 
            if "buffer" in source_packet_params[J2735_message_type_name]["match_keys"][match_i]:
                
                source_buffer = source_packet_params[J2735_message_type_name]["match_keys"][match_i]["buffer"]
                if abs(source_packet_value - search_packet_value) >  source_buffer:
                    # print("[!!!] VALUES DO NOT MATCH [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value))
                    all_fields_match = False
                    break
                # else:
                #     print("Values Match within buffer [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value) + " +/- " + str(source_buffer))
            
            else:

                # print("[!!!] VALUES DO NOT MATCH [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value))
                all_fields_match = False
                break
        # else:
        #     print("Values Match [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value))
    
    
    return all_fields_match

# prints all the match params and values for two given packets
def print_keys(source_params,check_params,source_packet,check_packet):
    for match_i in range(0,num_match_keys):
            
        source_key = source_params[J2735_message_type_name]["match_keys"][match_i]["key"]
        check_key = check_params[J2735_message_type_name]["match_keys"][match_i]["key"]

        if (  source_key == None or check_key == None ):
            continue

        print("  - " + source_packet[source_key] + " == " + check_packet[check_key])

def clean_name(input_name):
    print("Dirty Name: " + input_name)
    clean_name = re.sub('[^A-Za-z0-9 ]+', '', input_name)
    clean_name = re.sub(' ', '_', clean_name)
    clean_name = clean_name.lower()
    
    print("Clean Name: " + clean_name)
    return clean_name


def load_data(dataset_name,dataset_infile,dataset_type):

    dataset_name_clean = clean_name(dataset_name)

    print("\n----- LOADING DATA FOR " + dataset_name_clean + " -----")

    data_infile_obj = open(dataset_infile,'r')
    data_infile_reader = csv.DictReader(data_infile_obj,delimiter=',')
    data_infile_headers = data_infile_reader.fieldnames
    print("  Data Headers: " + str(data_infile_headers))

    data_list = list(data_infile_reader)
    total_packets = len(data_list)

    print("  Total Packets: " + str(total_packets))

    if dataset_type == "pcap":
        dataset_params = data_params["pcap_params"]
    elif dataset_type == "tdcs":
        dataset_params = data_params["tdcs_params"]

    
    num_datasets_loaded = len(all_data)
    
    all_data.append({
        "dataset_name"              : dataset_name_clean,
        "data_order"                : num_datasets_loaded + 1,
        "original_data_list"        : data_list,
        "filtered_data_list"        : [],
        "dataset_params"            : dataset_params,
    })

def get_obj_by_key_value(obj_array,key,value):
    for index, element in enumerate(obj_array):
        if element[key] == value:
            return index

def get_row_offset(dataset):
    
    print("\n----- GETTING ROW OFFSET: " + dataset["dataset_name"] + " -----")
    print("Before packets total: " + str(len(dataset["original_data_list"])))

    # if we have no other data in the dataset, we have nothing to compare to 
    filtered_data_object = find_data_row_offset(dataset)

    filtered_data_list = filtered_data_object["cleaned_data_to_search_list"]
    filtered_total_packets = len(filtered_data_list)
    print("Cleaned packets total: " + str(filtered_total_packets))

    print("Last packetIndex: " + filtered_data_list[filtered_total_packets -1]["packetIndex"])




load_data("source vehicle","source_vehicle_data/BSM/lead_carma_platform_out_decoded_packets_BSM.csv","pcap")
load_data("v2x in pcap","v2xhub_data/BSM/v2xhub_in_decoded_packets_BSM.csv","pcap")
load_data("v2x tdcs","v2xhub_data/BSM/VUG-Track-BSM-20220822124130.csv","tdcs")
load_data("dest veh tdcs","destination_vehicle_data/BSM/VUG-Track-BSM-20220822125045.csv","tdcs")
load_data("dest veh pcap","destination_vehicle_data/BSM/second_carma_platform_in_decoded_packets_BSM.csv","pcap")

for dataset in all_data:

    get_row_offset(dataset)


print("\n----- TESTING EARLY EXIT -----")
sys.exit()

# # get row offset for sv and v2xhub in pcap
# print("\n----- GETTING ROW OFFSET SOURCE VEHICLE -----")
# print("Before total_source_vehicle_out_packets length: " + str(len(source_vehicle_out_data_list)))
# filtered_source_vehicle_out_data_object = find_data_row_offset(None,None,source_vehicle_out_data_list,None,pcap_params,True)
# filtered_source_vehicle_out_data_list = filtered_source_vehicle_out_data_object["cleaned_data_to_search_list"]
# filtered_total_source_vehicle_out_packets = len(filtered_source_vehicle_out_data_list)
# print("Cleaned total_source_vehicle_out_packets length: " + str(len(filtered_source_vehicle_out_data_list)))
# print("Last packetIndex: " + filtered_source_vehicle_out_data_list[filtered_total_source_vehicle_out_packets -1]["packetIndex"])

# # get row offset for sv and v2xhub in pcap
# print("\n----- GETTING ROW OFFSET FOR SV AND V2XHUB IN PCAP -----")
# print("Before v2xhub_pcap_in_data_list length: " + str(len(v2xhub_pcap_in_data_list)))
# filtered_v2xhub_pcap_in_data_object = find_data_row_offset(filtered_source_vehicle_out_data_list[0],0,v2xhub_pcap_in_data_list,pcap_params,pcap_params,False)
# filtered_v2xhub_pcap_in_data_list = filtered_v2xhub_pcap_in_data_object["cleaned_data_to_search_list"]
# sv_out_to_v2xhub_in_offset = filtered_v2xhub_pcap_in_data_object["source_to_match_offset"]
# filtered_total_v2xhub_in_packets = len(filtered_v2xhub_pcap_in_data_list)
# print("filtered_v2xhub_pcap_in_data_list length: " + str(filtered_total_v2xhub_in_packets))
# print("Last packetIndex: " + filtered_v2xhub_pcap_in_data_list[filtered_total_v2xhub_in_packets -1]["packetIndex"])

# # get row offset for sv and v2xhub tdcs
# print("\n----- GETTING ROW OFFSET FOR SV AND V2XHUB TDCS -----")
# print("Before v2xhub_tdcs_data_list length: " + str(len(v2xhub_tdcs_data_list)))
# filtered_v2xhub_tdcs_data_object = find_data_row_offset(filtered_source_vehicle_out_data_list[0],0,v2xhub_tdcs_data_list,pcap_params,tdcs_params,False)
# filtered_v2xhub_tdcs_data_list = filtered_v2xhub_tdcs_data_object["cleaned_data_to_search_list"]
# sv_out_to_v2xhub_tdcs_offset = filtered_v2xhub_tdcs_data_object["source_to_match_offset"]
# filtered_total_v2xhub_tdcs_packets = len(filtered_v2xhub_tdcs_data_list)
# print("Cleaned v2xhub_tdcs_data_list length: " + str(filtered_total_v2xhub_tdcs_packets))

# # get row offset for sv and dest veh tdcs
# print("\n----- GETTING ROW OFFSET FOR SV AND DEST VEH TDCS -----")
# print("Before dest_veh_tdcs_data_list length: " + str(len(dest_veh_tdcs_data_list)))
# filtered_dest_veh_tdcs_data_object = find_data_row_offset(filtered_source_vehicle_out_data_list[0],0,dest_veh_tdcs_data_list,pcap_params,tdcs_params,False)
# filtered_dest_veh_tdcs_data_list = filtered_dest_veh_tdcs_data_object["cleaned_data_to_search_list"]
# sv_out_to_dest_veh_tdcs_offset = filtered_dest_veh_tdcs_data_object["source_to_match_offset"]
# filtered_total_dest_veh_tdcs_packets = len(filtered_dest_veh_tdcs_data_list)
# print("Cleaned dest_veh_tdcs_data_list length: " + str(filtered_total_dest_veh_tdcs_packets))

# # get row offset for sv and dest veh in pcap
# print("\n----- GETTING ROW OFFSET FOR SV AND DEST VEH IN PCAP -----")
# print("Before dest_veh_pcap_in_data_list length: " + str(len(dest_veh_pcap_in_data_list)))
# filtered_dest_veh_pcap_in_data_object = find_data_row_offset(filtered_source_vehicle_out_data_list[0],0,dest_veh_pcap_in_data_list,pcap_params,pcap_params,False)
# filtered_dest_veh_pcap_in_data_list = filtered_dest_veh_pcap_in_data_object["cleaned_data_to_search_list"]
# sv_out_to_dest_veh_in_offset = filtered_dest_veh_pcap_in_data_object["source_to_match_offset"]
# filtered_total_dest_veh_in_packets = len(filtered_dest_veh_pcap_in_data_list)
# print("filtered_dest_veh_pcap_in_data_list length: " + str(filtered_total_dest_veh_in_packets))
# print("Last packetIndex: " + filtered_dest_veh_pcap_in_data_list[filtered_total_dest_veh_in_packets -1]["packetIndex"])


############################## LOOP THROUGH SOURCE DATA ##############################

print("\n----- ITERATING SOURCE DATA -----")
for sv_out_i,sv_out_packet in enumerate(filtered_source_vehicle_out_data_list):
    
    # this block skips configured neq and eq at the beginning of a file
    # we only want this to run at the start

    # calculate the bsm broadcast latency
    secMark = float(sv_out_packet["secMark"])
    packet_timestamp = datetime.datetime.fromtimestamp(int(float(sv_out_packet["packetTimestamp"])))
    roundDownMinTime = datetime.datetime(packet_timestamp.year,packet_timestamp.month,packet_timestamp.day,packet_timestamp.hour,packet_timestamp.minute).timestamp()
    packetSecondsAfterMin = (float(sv_out_packet["packetTimestamp"]) - roundDownMinTime)
    bsm_broadcast_latency = packetSecondsAfterMin*1000 - secMark

    if (bsm_broadcast_latency < 0) :
        # print("[!!!] Minute mismatch")
        bsm_broadcast_latency = bsm_broadcast_latency + 60000

    sv_out_to_v2xhub_in_index = sv_out_i + sv_out_to_v2xhub_in_offset
    sv_out_to_v2xhub_tdcs_index = sv_out_i + sv_out_to_v2xhub_tdcs_offset
    sv_out_to_dest_veh_tdcs_index = sv_out_i + sv_out_to_dest_veh_tdcs_offset
    sv_out_to_dest_veh_in_index = sv_out_i + sv_out_to_dest_veh_in_offset

    # print("\nsv_out index: " + str(sv_out_i))
    # print("v2x_in index: " + str(sv_out_to_v2xhub_in_index))
    # print("v2x_tdcs index: " + str(sv_out_to_v2xhub_tdcs_index))
    # print("dest_veh_tdcs index: " + str(sv_out_to_dest_veh_tdcs_index))

    ############################## CHECK V2X-HUB PCAP IN DATA ##############################


    all_fields_match = check_if_data_matches(pcap_params,pcap_params,sv_out_packet,filtered_v2xhub_pcap_in_data_list[sv_out_to_v2xhub_in_index])

    if( all_fields_match ):
        
        v2x_pcap_in_timestamp = float(filtered_v2xhub_pcap_in_data_list[sv_out_to_v2xhub_in_index]["packetTimestamp"])
        
        v2x_adjusted_timestamp = v2x_pcap_in_timestamp + sv_to_v2x_clock_skew

        sv_to_v2x_latency = v2x_adjusted_timestamp - float(sv_out_packet["packetTimestamp"])
        
        # print("\nFound matching PCAP data [" + sv_out_packet["packetIndex"] + ":" + filtered_v2xhub_pcap_in_data_list[sv_out_to_v2xhub_in_index]["packetIndex"] + "]: ")
        # print_keys(pcap_params,pcap_params,sv_out_packet,filtered_v2xhub_pcap_in_data_list[sv_out_to_v2xhub_in_index])
        

    else:
        print("\n[!!!] Found dropped packet V2X-Hub IN PCAP [" + sv_out_packet["packetIndex"] + ":" + filtered_v2xhub_pcap_in_data_list[sv_out_to_v2xhub_in_index]["packetIndex"] + "]: ")
        print_keys(pcap_params,pcap_params,sv_out_packet,filtered_v2xhub_pcap_in_data_list[sv_out_to_v2xhub_in_index])

        sv_out_to_v2xhub_in_offset -= 1


    ############################## CHECK V2X-HUB TDCS DATA ##############################

    all_fields_match = check_if_data_matches(pcap_params,tdcs_params,sv_out_packet,filtered_v2xhub_tdcs_data_list[sv_out_to_v2xhub_tdcs_index])

    if( all_fields_match ):
        
        v2x_tdcs_time_of_creation = float(filtered_v2xhub_tdcs_data_list[sv_out_to_v2xhub_tdcs_index]["const^Metadata,TimeOfCreation"])/1000000000
        v2x_tdcs_time_of_commit = float(filtered_v2xhub_tdcs_data_list[sv_out_to_v2xhub_tdcs_index]["Metadata,TimeOfCommit"])/1000000000
        v2x_tdcs_time_of_receipt = float(filtered_v2xhub_tdcs_data_list[sv_out_to_v2xhub_tdcs_index]["Metadata,TimeOfReceipt"])/1000000000

        j2735_to_sdo_conversion_time = (v2x_tdcs_time_of_commit - v2x_pcap_in_timestamp)*1000
        # print("\nFound matching TDCS data [" + sv_out_packet["packetIndex"] + ":" + filtered_v2xhub_tdcs_data_list[sv_out_to_v2xhub_tdcs_index]["rowID"] + "]: ")
        # print_keys(pcap_params,tdcs_params,sv_out_packet,filtered_v2xhub_tdcs_data_list[sv_out_to_v2xhub_tdcs_index])
        

    else:
        print("\n[!!!] Found dropped packet V2X TDCS [" + sv_out_packet["packetIndex"] + ":" + filtered_v2xhub_tdcs_data_list[sv_out_to_v2xhub_tdcs_index]["rowID"] + "]: ")
        print_keys(pcap_params,tdcs_params,sv_out_packet,filtered_v2xhub_tdcs_data_list[sv_out_to_v2xhub_tdcs_index])

        sv_out_to_v2xhub_tdcs_offset -= 1

    ############################## CHECK DEST VEH TDCS DATA ##############################

    all_fields_match = check_if_data_matches(pcap_params,tdcs_params,sv_out_packet,filtered_dest_veh_tdcs_data_list[sv_out_to_dest_veh_tdcs_index])

    if( all_fields_match ):
        
        dest_veh_tdcs_time_of_creation = float(filtered_dest_veh_tdcs_data_list[sv_out_to_dest_veh_tdcs_index]["const^Metadata,TimeOfCreation"])/1000000000
        dest_veh_tdcs_time_of_commit = float(filtered_dest_veh_tdcs_data_list[sv_out_to_dest_veh_tdcs_index]["Metadata,TimeOfCommit"])/1000000000
        dest_veh_tdcs_time_of_receipt = float(filtered_dest_veh_tdcs_data_list[sv_out_to_dest_veh_tdcs_index]["Metadata,TimeOfReceipt"])/1000000000

        tena_packet_latency = (dest_veh_tdcs_time_of_receipt - (dest_veh_tdcs_time_of_commit + v2x_to_second_clock_skew/1000) )*1000
        # print("\nFound matching Dest Veh TDCS data [" + sv_out_packet["packetIndex"] + ":" + filtered_dest_veh_tdcs_data_list[sv_out_to_dest_veh_tdcs_index]["rowID"] + "]: ")
        # print_keys(pcap_params,tdcs_params,sv_out_packet,filtered_dest_veh_tdcs_data_list[sv_out_to_dest_veh_tdcs_index])
        

    else:
        print("\n[!!!] Found dropped packet Dest Veh TDCS [" + sv_out_packet["packetIndex"] + ":" + filtered_dest_veh_tdcs_data_list[sv_out_to_dest_veh_tdcs_index]["rowID"] + "]: ")
        print_keys(pcap_params,tdcs_params,sv_out_packet,filtered_dest_veh_tdcs_data_list[sv_out_to_dest_veh_tdcs_index])

        sv_out_to_dest_veh_tdcs_offset -= 1

    ############################## CHECK V2X-HUB PCAP IN DATA ##############################


    all_fields_match = check_if_data_matches(pcap_params,pcap_params,sv_out_packet,filtered_dest_veh_pcap_in_data_list[sv_out_to_dest_veh_in_index])

    if( all_fields_match ):

        dest_veh_pcap_in_timestamp = float(filtered_dest_veh_pcap_in_data_list[sv_out_to_dest_veh_in_index]["packetTimestamp"])
        
        sdo_to_j2735_latency = (dest_veh_pcap_in_timestamp - dest_veh_tdcs_time_of_receipt)*1000
        
        # print("\nFound matching DEST VEH IN PCAP data [" + sv_out_packet["packetIndex"] + ":" + filtered_dest_veh_pcap_in_data_list[sv_out_to_dest_veh_in_index]["packetIndex"] + "]: ")
        # print_keys(pcap_params,pcap_params,sv_out_packet,filtered_dest_veh_pcap_in_data_list[sv_out_to_dest_veh_in_index])
        

    else:
        print("\n[!!!] Found dropped packet DEST VEH IN PCAP [" + sv_out_packet["packetIndex"] + ":" + filtered_dest_veh_pcap_in_data_list[sv_out_to_dest_veh_in_index]["packetIndex"] + "]: ")
        print_keys(pcap_params,pcap_params,sv_out_packet,filtered_dest_veh_pcap_in_data_list[sv_out_to_dest_veh_in_index])

        sv_out_to_dest_veh_in_offset -= 1

    # write results to the csv

    # [
    #   "sv_packet_index", "v2x_in_packet_index", "v2x_tdcs_rowID", "dest_veh_tdcs_rowID", 
    #   "sv_out_timestamp", "v2x_in_timestamp", 
    #   "v2x_tdcs_time_of_creation", "v2x_tdcs_time_of_commit", "v2x_tdcs_time_of_receipt", 
    #   "dest_veh_tdcs_time_of_creation", "dest_veh_tdcs_time_of_commit", "dest_veh_tdcs_time_of_receipt", 
    #   "bsm_broadcast_latency", "v2x_adjusted_timestamp","sv_to_v2x_latency", "j2735_to_sdo_conversion_time", "tena_packet_latency", "sdo_to_j2735_latency"
    # ]

    results_outfile_writer.writerow([
            sv_out_packet["packetIndex"],
            filtered_v2xhub_pcap_in_data_list[sv_out_to_v2xhub_in_index]["packetIndex"],
            filtered_v2xhub_tdcs_data_list[sv_out_to_v2xhub_tdcs_index]["rowID"],
            filtered_dest_veh_tdcs_data_list[sv_out_to_dest_veh_tdcs_index]["rowID"],

            sv_out_packet["packetTimestamp"],
            v2x_pcap_in_timestamp,

            v2x_tdcs_time_of_creation,
            v2x_tdcs_time_of_commit,
            v2x_tdcs_time_of_receipt,

            v2x_tdcs_time_of_creation,
            v2x_tdcs_time_of_commit,
            v2x_tdcs_time_of_receipt,

            bsm_broadcast_latency,
            v2x_adjusted_timestamp,
            sv_to_v2x_latency,
            j2735_to_sdo_conversion_time,
            tena_packet_latency,
            sdo_to_j2735_latency,

           

            

        ])

    # check to make sure we did not reach the end of the file on any other dataset 
    if (
        sv_out_to_v2xhub_in_index > filtered_total_v2xhub_in_packets or 
        sv_out_to_v2xhub_tdcs_index > filtered_total_v2xhub_tdcs_packets

    ):
        print("\nReached end of one of the files, exiting")
        sys.exit()


