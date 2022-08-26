# import json
import sys
import csv
# import numpy
import datetime
import math


########## LOAD IN SOURCE VEHICLE DATA ##########
source_out_pcap_file = "source_vehicle_data/lead_carma_platform_out_decoded_packets_BSM.csv"

source_vehicle_out_data_infile_obj = open(source_out_pcap_file,'r')
source_vehicle_out_data_infile_reader = csv.DictReader(source_vehicle_out_data_infile_obj,delimiter=',')
source_vehicle_out_data_infile_headers = source_vehicle_out_data_infile_reader.fieldnames
print("\nsource_vehicle_data_infile_headers: " + str(source_vehicle_out_data_infile_headers))

source_vehicle_out_data_list = list(source_vehicle_out_data_infile_reader)
total_source_vehicle_out_packets = len(source_vehicle_out_data_list)

print("Total Packets: " + str(total_source_vehicle_out_packets))

desired_bsm_id = "f03ad610"


# defines the required fields to be used in analysis for each message type
# skip if keys and values are used to skip non-relevant data (collected before run started, for different vehicle)
# match_keys are the data columns that will be used to verify the data matches
source_out_params = {
    "BSM" : {
        "skip_if_neqs"      : [
            {
                "key"           : "bsm id",         # key(column) to check
                "value"         : desired_bsm_id,   # value to check
                "round"         : False,            # round the value before checking (important for TENA data)
                "round_decimals": 0,                # decimal places to round to (only needed if round == True, shown here for example)
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
                "round_decimals": 6,
                "radians"   : False
            },
            {
                "key"       : "longitude",
                "round"     : True,
                "round_decimals": 6,
                "radians"   : False
            },
            {
                "key"       : "heading",
                "round"     : False,
                "radians"   : False
            },
            {
                "key"       : "speed(m/s)",
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

########## LOAD IN V2X HUB DATA ##########

v2xhub_in_pcap_file = "v2xhub_data/v2xhub_in_decoded_packets_BSM.csv"

v2xhub_pcap_in_data_infile_obj = open(v2xhub_in_pcap_file,'r')
v2xhub_pcap_in_data_infile_reader = csv.DictReader(v2xhub_pcap_in_data_infile_obj,delimiter=',')
v2xhub_pcap_in_data_infile_headers = v2xhub_pcap_in_data_infile_reader.fieldnames
print("\nv2xhub_data_infile_headers: " + str(v2xhub_pcap_in_data_infile_headers))

v2xhub_pcap_in_data_list = list(v2xhub_pcap_in_data_infile_reader)
total_v2xhub_in_packets = len(v2xhub_pcap_in_data_list)

print("Total Packets: " + str(total_v2xhub_in_packets))

v2xhub_in_pcap_params = {
    "BSM" : {
        "skip_if_neqs"      : [
            {
                "key"           : "bsm id",
                "value"         : desired_bsm_id,
                "round"         : False,
                "start_only"    : False,
            }

        ],
        
        "skip_if_eqs"       : [
            {
                "key"           : "speed(m/s)",
                "value"         : "0.0",
                "round"         : True,
                "round_decimals": 2,
                "start_only"    : True, 
            }
        ],

        "match_keys"        : [
            {
                "key"       : "latitude",
                "round"     : True,
                "round_decimals": 6,
                "radians"   : False
            },
            {
                "key"       : "longitude",
                "round"     : True,
                "round_decimals": 6,
                "radians"   : False
            },
            {
                "key"       : "heading",
                "round"     : False,
                "radians"   : False
            },
            {
                "key"       : "speed(m/s)",
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

########## LOAD IN V2X HUB TDCS DATA ##########

v2xhub_in_tdcs_file = "v2xhub_data/VUG-Track-BSM-20220822124130.csv"

v2xhub_tdcs_data_infile_obj = open(v2xhub_in_tdcs_file,'r')
v2xhub_tdcs_data_infile_reader = csv.DictReader(v2xhub_tdcs_data_infile_obj,delimiter=',')
v2xhub_tdcs_data_infile_headers = v2xhub_tdcs_data_infile_reader.fieldnames
print("\nv2xhub_tdcs_data_infile_headers: " + str(v2xhub_tdcs_data_infile_headers))

v2xhub_tdcs_data_list = list(v2xhub_tdcs_data_infile_reader)
total_v2xhub_tdcs_packets = len(v2xhub_tdcs_data_list)

desired_tena_identifier = "CARMA-TFHRC-LIVE"

print("Total Packets: " + str(total_v2xhub_tdcs_packets))

v2xhub_tdcs_params = {
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
                "round_decimals": 6,
                "radians"   : False
            },
            {
                "key"       : "tspi.velocity.ltpENU_asTransmitted.srf.longitudeInDegrees,Float64 (optional)",
                "round"     : True,
                "round_decimals": 6,
                "radians"   : False
            },
            {
                "key"       : "tspi.orientation.frdWRTltpENUbodyFixedZYX_asTransmitted.srf.azimuthInRadians,Float64 (optional)",
                "round"     : False,
                "radians"   : True
            },
            {
                "key"       : None,
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

########## INITIALIZE CSV WRITER ##########

outfile = "performance_analysis.csv"
results_outfile_obj = open(outfile,'w',newline='')
results_outfile_writer = csv.writer(results_outfile_obj)

# write headers
results_outfile_writer.writerow(["sv_packet_index","v2x_packet_index","sv_broadcast_latency","sv_to_v2x_latency"])


########## INITIALIZE VARIABLES FOR LOOPS ##########

sv_out_to_v2x_in_offset = None
sv_out_to_v2x_tdcs_offset = None
sv_starting_row = None

# specifies the number of match_keys defined in the params for each data source
num_match_keys = 8

# specifies the message type to be analyzed
J2735_message_type_name = "BSM"


########## SET CLOCK SKEWS ##########

virtual_to_nist_clock_skew = -51.729
live_to_nist_clock_skew = 60.723

v2x_to_virtual_clock_skew = 43.712
v2x_to_second_clock_skew = -213.336
v2x_to_third_clock_skew = -0.990


sv_to_v2x_clock_skew = live_to_nist_clock_skew - (virtual_to_nist_clock_skew + v2x_to_virtual_clock_skew)
print("\nsv_to_v2x_clock_skew: " + str(sv_to_v2x_clock_skew))

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# finds the offset of two sources of data
def find_data_row_offset(source_packet_to_match,source_packet_i,data_to_search_list,source_packet_params,data_to_search_params):
    
    search_starting_row = None
    source_to_match_offset = None
    

    for search_i,search_packet in enumerate(data_to_search_list):

        # iterate through the neqs to check
        all_neqs_pass = True

        # print("\nLooking at data at index: " + source_packet_to_match["packetIndex"] + " : " + search_packet["packetIndex"])

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
            # print("Continuing because not all NEQs passed")
            
            # remove the bad data from the array so we do not encounter it later
            # the pop function is a change in place and therefore the original array is modified
            if source_to_match_offset != None:
                source_to_match_offset -+ 1
            
            data_to_search_list.pop(search_i)
            continue
        
        #iterate through the eqs to check
        all_eqs_pass = True

        for current_eq in data_to_search_params[J2735_message_type_name]["skip_if_eqs"]:

            # skip if values are equal (ex: skip if speed is 0)
            search_packet_eq_value = search_packet[current_eq["key"]]
            eq_param_value = current_eq["value"]

            # print("EQ CHECK: " + str(search_packet_eq_value) + " != " + str(eq_param_value))

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

            data_to_search_list.pop(search_i)
            continue

        if search_starting_row == None:
            search_starting_row = search_i
            print("search_starting_row: " + str(search_starting_row))
        
        
        
        all_fields_match = True

        # the first time all fields match, this is the start of the data we want
        # get the offset between the source start index and the search start index
        if all_fields_match and source_to_match_offset == None:

            for match_i in range(0,5):
                source_packet_key = source_packet_params[J2735_message_type_name]["match_keys"][match_i]["key"]
                search_packet_key = data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["key"]

                # print("source_packet_key: " + str(source_packet_key))
                # print("search_packet_key: " + str(search_packet_key))

                if (
                        source_packet_key == None or
                        search_packet_key == None
                ):
                    # print("Skipping match key " + str(match_i) + " since one or more keys are None: " + str(source_packet_key) + "," + str(search_packet_key))
                    continue

                
                source_packet_value = source_packet_to_match[source_packet_key]
                search_packet_value = search_packet[search_packet_key]

                

                if source_packet_params[J2735_message_type_name]["match_keys"][match_i]["radians"]:
                    source_packet_value = math.degrees(float(source_packet_value))
                
                if data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["radians"]:
                    search_packet_value = math.degrees(float(search_packet_value))

                if source_packet_params[J2735_message_type_name]["match_keys"][match_i]["round"]:
                    source_packet_value = round(float(source_packet_value),source_packet_params[J2735_message_type_name]["match_keys"][match_i]["round_decimals"])
                
                if data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["round"]:
                    search_packet_value = round(float(search_packet_value),data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["round_decimals"])


                if  ( source_packet_value != search_packet_value ):
                    print("[!!!] VALUES DO NOT MATCH [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value))
                    all_fields_match = False
                    break
                else:
                    print("Values Match [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value))
            
        

            source_to_match_offset = search_i - source_packet_i

            print("\nAll Fields match")
            print("\nsource_to_match_offset = " + str(source_to_match_offset))

    return source_to_match_offset




########## LOOP THROUGH SOURCE DATA ##########
print("\n----- ITERATING SOURCE DATA -----")
for sv_out_i,sv_out_packet in enumerate(source_vehicle_out_data_list):
    
    # this block skips configured neq and eq at the beginning of a file
    # we only want this to run at the start
    # if a packet makes it through, sv_starting_row will be set, causing these checks to be skipped

    if sv_starting_row == None:
        # iterate through the neqs to check
        # print("\n----- SKIPPING SOURCE NEQS -----")

        all_neqs_pass = True

        for current_neq in source_out_params[J2735_message_type_name]["skip_if_neqs"]:

            # skip if values are not equal (ex: checking for matching bsm id)
            source_out_packet_neq_value = sv_out_packet[current_neq["key"]]
            neq_param_value = current_neq["value"]

            # print("NEQ CHECK: " + str(source_out_packet_neq_value) + " != " + str(neq_param_value))

            # if the source_packet_value is a number and we want to round, round both values to the same number of decimals
            if is_number(source_out_packet_neq_value) and current_neq["round"]:
                    # print("Rounding NEQ Values")
                    source_out_packet_neq_value = round(float(source_out_packet_neq_value),6)
                    neq_param_value = round(float(neq_param_value),6)

            if source_out_packet_neq_value != neq_param_value:
                # print("Skipping non matching value: " + str(source_out_packet_neq_value) + " != " + str(neq_param_value))
                all_neqs_pass = False
                break
        
        if not all_neqs_pass:
            # print("Continuing because not all NEQs passed")
            continue

        all_eqs_pass = True

        for current_eq in source_out_params[J2735_message_type_name]["skip_if_eqs"]:
            # skip if values are equal (ex: skip if speed is 0)
            source_out_packet_eq_value = sv_out_packet[current_eq["key"]]
            eq_param_value = current_eq["value"]

            # print("EQ CHECK: " + str(source_out_packet_eq_value) + " == " + str(eq_param_value))

            # if the source_packet_value is a number and we want to round, round both values to the same number of decimals
            if current_eq["round"]:
                    # print("Rounding EQ Values")
                    source_out_packet_eq_value = round(float(source_out_packet_eq_value),6)
                    eq_param_value = round(float(eq_param_value),6)

            if source_out_packet_eq_value == eq_param_value:
                # print("Skipping matching value: " + str(source_out_packet_eq_value) + " == " + str(eq_param_value))
                all_eqs_pass = False
                break
        
        if not all_eqs_pass:
            # print("Continuing because not all EQs passed")
            continue

    # record the row where the speed begins to be non 0 on the source data
    if sv_starting_row == None:
        sv_starting_row = sv_out_i
        print("sv_starting_row: " + str(sv_starting_row))

    # calculate the bsm broadcast latency
    secMark = float(sv_out_packet["secMark"])
    packet_timestamp = datetime.datetime.fromtimestamp(int(float(sv_out_packet["packetTimestamp"])))
    roundDownMinTime = datetime.datetime(packet_timestamp.year,packet_timestamp.month,packet_timestamp.day,packet_timestamp.hour,packet_timestamp.minute).timestamp()
    packetSecondsAfterMin = (float(sv_out_packet["packetTimestamp"]) - roundDownMinTime)
    bsm_broadcast_latency = packetSecondsAfterMin*1000 - secMark

    if (bsm_broadcast_latency < 0) :
        # print("[!!!] Minute mismatch")
        bsm_broadcast_latency = bsm_broadcast_latency + 60000

    # get row offset for sv and v2xhub in pcap
    if sv_out_to_v2x_in_offset == None:
        print("\n----- GETTING ROW OFFSET FOR SV AND V2XHUB IN PCAP -----")
        print("Before v2xhub_pcap_in_data_list length: " + str(len(v2xhub_pcap_in_data_list)))
        sv_out_to_v2x_in_offset = find_data_row_offset(sv_out_packet,sv_out_i,v2xhub_pcap_in_data_list,source_out_params,v2xhub_in_pcap_params)
        total_v2xhub_in_packets = len(v2xhub_pcap_in_data_list)
        print("Cleaned v2xhub_pcap_in_data_list length: " + str(total_v2xhub_in_packets))
    
    # get row offset for sv and v2xhub tdcs
    
    if sv_out_to_v2x_tdcs_offset == None:
        print("\n----- GETTING ROW OFFSET FOR SV AND V2XHUB TDCS -----")
        print("Before v2xhub_tdcs_data_list length: " + str(len(v2xhub_tdcs_data_list)))
        sv_out_to_v2x_tdcs_offset = find_data_row_offset(sv_out_packet,sv_out_i,v2xhub_tdcs_data_list,source_out_params,v2xhub_tdcs_params)
        total_v2xhub_tdcs_packets = len(v2xhub_tdcs_data_list)
        print("Cleaned v2xhub_tdcs_data_list length: " + str(total_v2xhub_tdcs_packets))

    # print("\n----- TESTING EARLY EXIT -----")
    # sys.exit()

    # print("sv_out index: " + str(sv_out_i))
    # print("v2x_in index: " + str(sv_out_i + sv_out_to_v2x_in_offset))
    # print("v2x_tdcs index: " + str(sv_out_i + sv_out_to_v2x_tdcs_offset))

    if(
            sv_out_packet["latitude"] == v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["latitude"] and 
            sv_out_packet["longitude"] == v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["longitude"] and 
            sv_out_packet["heading"] == v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["heading"] and
            sv_out_packet["speed(m/s)"] == v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["speed(m/s)"]

    ):
        
        v2x_adjusted_timestamp = float(v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["packetTimestamp"]) + sv_to_v2x_clock_skew

        sv_to_v2x_latency = v2x_adjusted_timestamp - float(sv_out_packet["packetTimestamp"])

        results_outfile_writer.writerow([
            sv_out_packet["packetIndex"],
            v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["packetIndex"],
            sv_out_packet["packetTimestamp"],
            v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["packetTimestamp"],
            v2x_adjusted_timestamp,
            sv_to_v2x_latency,

            bsm_broadcast_latency

        ])

        print("Found matching data [" + sv_out_packet["packetIndex"] + ":" + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["packetIndex"] + "]: ")
        print("  - " + sv_out_packet["latitude"] + " == " + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["latitude"])
        print("  - " + sv_out_packet["longitude"] + " == " + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["longitude"])
        print("  - " + sv_out_packet["heading"] + " == " + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["heading"])
        print("  - " + sv_out_packet["speed(m/s)"] + " == " + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["speed(m/s)"])

    else:
        print("[!!!] Found dropped packet [" + sv_out_packet["packetIndex"] + ":" + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["packetIndex"] + "]: ")
        print("  - " + sv_out_packet["latitude"] + " == " + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["latitude"])
        print("  - " + sv_out_packet["longitude"] + " == " + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["longitude"])
        print("  - " + sv_out_packet["heading"] + " == " + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["heading"])
        print("  - " + sv_out_packet["speed(m/s)"] + " == " + v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["speed(m/s)"])


        results_outfile_writer.writerow([
            sv_out_packet["packetIndex"],
            "",                                     # v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["packetIndex"],
            sv_out_packet["packetTimestamp"],
            "",                                     # v2xhub_pcap_in_data_list[sv_out_i + sv_out_to_v2x_in_offset]["packetTimestamp"],
            "",                                     # v2x_adjusted_timestamp,
            "",                                     # sv_to_v2x_latency,
            bsm_broadcast_latency

        ])

        sv_out_to_v2x_in_offset -= 1
        continue

    

    if (sv_out_i + sv_out_to_v2x_in_offset + 2 > total_v2xhub_in_packets):
        print("\nReached end of v2x in file, exiting")
        sys.exit()


    

