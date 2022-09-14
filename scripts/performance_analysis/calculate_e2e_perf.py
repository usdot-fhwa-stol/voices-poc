import sys
import csv
import datetime
import math
import re
import logging
import glob
import argparse
import json
from pprint import pprint


############################## TODO ##############################
# - change all data param modifiers (round, buffer, radian) to check if key exists, not value
# - add checks for all param modifiers to check for the proper datatype before attempting to perform modifier
# - remove places where underscore is added to message types
# 

# checks if value is a number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# filter dataset based on specified parameters
def filter_dataset(data_to_search,desired_num_of_skipped_packets):

    logging.info("----- FILTERING DATASET: " + dataset["dataset_name"] + " -----")
    logging.debug("Before packets total: " + str(len(dataset["original_data_list"])))
    
    search_starting_row = None
    found_packet_matching_search = False
    cleaned_data_to_search_list = []
   
    
    if data_to_search["data_order"] != 1:
        source_data_obj_index = get_obj_by_key_value(all_data,"data_order",1)
        source_data_obj = all_data[source_data_obj_index]
        source_data_list_filtered = source_data_obj["filtered_data_list"]
        source_packet_to_match = source_data_list_filtered[0]
        source_packet_params = source_data_obj["dataset_params"]

        logging.debug("Looking at source packetIndex: " + source_packet_to_match[source_data_obj["dataset_index_column_name"]])


    data_to_search_list = data_to_search["original_data_list"]
    data_to_search_params = data_to_search["dataset_params"]

    skipped_packets = 0

    for search_i,search_packet in enumerate(data_to_search_list):

        if data_to_search["data_order"] == 1:
            logging.debug("Checking packet index: [" + search_packet[data_to_search["dataset_index_column_name"]] + "]")
        else:
            logging.debug("Checking packet index: [" + source_packet_to_match[source_data_obj["dataset_index_column_name"]] + ":" + search_packet[data_to_search["dataset_index_column_name"]] + "]")
        
        # iterate through the neqs to check
        all_neqs_pass = True

        for current_neq in data_to_search_params[J2735_message_type_name]["skip_if_neqs"]:
            
            neq_bypass = False

            # skip if values are not equal (ex: checking for matching bsm id)
            search_packet_neq_value = search_packet[current_neq["key"]]
            neq_param_value = current_neq["value"]

            logging.debug("  NEQ CHECK: " + str(search_packet_neq_value) + " != " + str(neq_param_value))

            # if we have already found the start of the data set (and therefore the offset),
            # and the current neq is for the start_only, skip this neq
            if not found_packet_matching_search and "start_only" in current_neq and current_neq["start_only"]:
                logging.debug("    Skipping NEQ since it is start only: " + current_neq["key"])
                continue


            # if the source_packet_value is a number and we want to round, round both values to the same number of decimals
            if "round" in current_neq and current_neq["round"]:
                    
                    try:
                        search_packet_neq_value = round(float(search_packet_neq_value),current_neq["round_decimals"])
                    except:
                        logging.error("    Unable to round: " + search_packet_neq_value)
                    try:
                        neq_param_value = round(float(neq_param_value),current_neq["round_decimals"])
                    except:
                        logging.error("    Unable to round: " + neq_param_value)

            
            # the only way to know which vehicle sent the mobility operations is to check if the timestamps are close together
            if "mobility_timestamp_check" in current_neq and current_neq["mobility_timestamp_check"]:
                
                # we need to use this timesstamp check for filtering pcaps in but it breaks if we dont have a first data point
                # if data_to_search["data_order"] == 1:
                #     neq_bypass = True
                
                # if the cleaned data list is empty, this must be the first packet and we need to feed a starting timestamp value
                if len(cleaned_data_to_search_list) == 0:
                    
                    # if we are the first dataset, use the timestamp from the current packet
                    if data_to_search["data_order"] == 1:
                        previous_timestamp = float(search_packet["headerTimestamp"])
                    else:
                        previous_timestamp = float(all_data[0]["filtered_data_list"][0]["headerTimestamp"])
                        
                        if data_to_search["dataset_type"] == "tdcs":
                            previous_timestamp = previous_timestamp * 1000000 # tdcs timestamps are in nanoseconds, mobility header timestamp is in ms

                    
                    
                    
                # if we do have something in the list, we can just use the last timestamp
                else:
                    previous_timestamp = cleaned_data_to_search_list[-1][current_neq["key"]]
                
                logging.debug("    Timestamp check: " + str(previous_timestamp) + " ~ " + str(search_packet_neq_value) )
                # check if difference is greater than 1 second (1000000000 ns)
                if abs(int(float(search_packet_neq_value)) - int(float(previous_timestamp))) > 1000000000:
                    logging.debug("    Skipping because timestamp doesnt match therefore must be other vehicle")
                    all_neqs_pass = False
                    break
                else:
                    neq_bypass = True

            if search_packet_neq_value != neq_param_value and not neq_bypass:
                logging.debug("    Skipping non matching value: " + str(search_packet_neq_value) + " != " + str(neq_param_value))
                all_neqs_pass = False
                break
        
        if not all_neqs_pass:
            logging.debug("  Continuing because not all NEQs passed")
            continue
        
        #iterate through the eqs to check
        all_eqs_pass = True

        for current_eq in data_to_search_params[J2735_message_type_name]["skip_if_eqs"]:
            
            eq_bypass = False
            
            # skip if values are equal (ex: skip if speed is 0)
            search_packet_eq_value = search_packet[current_eq["key"]]
            eq_param_value = current_eq["value"]

            logging.debug("  EQ CHECK: " + str(search_packet_eq_value) + " == " + str(eq_param_value))

            # if we have already found the start of the data set (and therefore the offset),
            # and the current eq is for the start_only, skip this neq
            if found_packet_matching_search and "start_only" in current_eq and current_eq["start_only"]:
                logging.debug("    Skipping EQ since it is start only: " + current_eq["key"])
                continue

            # if the source_packet_value is a number and we want to round, round both values to the same number of decimals
            if "round" in current_eq and current_eq["round"]:
                    
                    try:
                        search_packet_eq_value = round(float(search_packet_eq_value),current_eq["round_decimals"])
                    except:
                        logging.warning("    Unable to round: " + search_packet_eq_value)
                    
                    try:
                        eq_param_value = round(float(eq_param_value),current_eq["round_decimals"])
                    except:
                        logging.warning("    Unable to round: " + eq_param_value )

            if "starts_with" in current_eq and current_eq["starts_with"]:
                logging.debug("    Checking if: " + str(search_packet_eq_value) + " starts with " + str(current_eq["value"]))
                
                starts_with_search = re.search('^' + current_eq["value"],search_packet_eq_value)

                if not starts_with_search:
                    logging.debug("    Value doesnt start with " + str(current_eq["value"]))
                    eq_bypass = True
                else:
                    logging.debug("    Skipping because value starts with " + str(current_eq["value"]))
                    all_eqs_pass = False
                    break
            
            if search_packet_eq_value == eq_param_value and not eq_bypass:
                logging.debug("    Skipping matching value: " + str(search_packet_eq_value) + " == " + str(eq_param_value))
                all_eqs_pass = False
                break
        
        if not all_eqs_pass:
            logging.debug("  Continuing because not all EQs passed")
            continue
        
        # here we are continuing if this packet was not found in other datasets
        # this is accomplished by skipping and counting the number of skipped packets 
        # until it matches the desired skipped packet number
        if data_to_search["data_order"] == 1 and skipped_packets < desired_num_of_skipped_packets:
                        
            logging.debug("Skipping packet to find one that exists in all datasets")
            skipped_packets += 1
            continue         


        # if we are filtering the source data, we are not matching it against anything so skip this bottom part
        if data_to_search["data_order"] == 1 and not found_packet_matching_search :
            found_packet_matching_search = True
            search_starting_row = search_i
            logging.debug("Found source search_starting_row: " + str(search_starting_row))
            logging.debug("Keeping Packet: " + str(search_packet[data_to_search["dataset_index_column_name"]]))
            cleaned_data_to_search_list.append(search_packet)
            continue



        # the first time all fields match, this is the start of the data we want
        # get the offset between the source start index and the search start index
        #
        # UPDATE:   with the new method of filtering out the data lists, ideally all lists index 0 align
        #           this might not always be the case (if the first valid packet was dropped) so we do this anyway

        if not found_packet_matching_search:

            all_fields_match = check_if_data_matches(source_packet_params,data_to_search_params,source_packet_to_match,search_packet)
            
            if all_fields_match:
                logging.debug("All Fields match for " + data_to_search["dataset_name"])
                found_packet_matching_search = True

        # since it was not eliminated from the NEQ and EQs, add the packet to the filtered data list
        if found_packet_matching_search:
            logging.debug("Keeping Packet: " + str(search_packet[data_to_search["dataset_index_column_name"]]))
            cleaned_data_to_search_list.append(search_packet)

    if data_to_search["data_order"] == 1 and search_starting_row == None:
        if desired_num_of_skipped_packets == len(data_to_search_list):
                logging.critical("Unable to find any packets in source dataset that exits in all other datasets. Consider changing the EQ and NEQ")
                print("\nUnable to find any packets in source dataset that exits in all other datasets. Consider changing the EQ and NEQ")
                sys.exit()
        else:
            logging.critical("search_starting_row not set - Unable to find a single packet in source that satisfies the EQ and NEQ. Consider changing the EQ and NEQ to find a starting packet")
            print("\nUnable to find a single packet in source data that satisfies the EQ and NEQ, Consider changing the EQ and NEQ to find a starting packet")
            sys.exit()

        
    if not found_packet_matching_search:
        logging.warning("[!!!] found_packet_matching_search false - Unable to find a single packet that satisfies the EQ and NEQ")
        return

    data_to_search["filtered_data_list"] = cleaned_data_to_search_list
    data_to_search["found_packet_matching_search"] = found_packet_matching_search

    # filtered_data_list = dataset["cleaned_data_to_search_list"]
    filtered_total_packets = len(data_to_search["filtered_data_list"])
    logging.info("Cleaned packets total: " + str(filtered_total_packets))
    logging.debug("Last packetIndex: " + dataset["filtered_data_list"][filtered_total_packets -1][dataset["dataset_index_column_name"]])

def extract_dtd_from_mob_ops(ops_params_value):
    # logging.debug("  EXTRACTING DTD FROM: " + str(ops_params_value))
    mobility_op_type_search = re.search('^(.*)\|',ops_params_value)

    if not mobility_op_type_search:
        # logging.debug("  Error, unable to extract STATUS or INFO from operations params")
        return None

    mobility_op_type = mobility_op_type_search.group(1)

    if mobility_op_type == "INFO":
        # logging.debug("  Got INFO message")
        
        dtd_search = re.search('DTD:(.*),ECEFX:',ops_params_value)

        if not dtd_search:
            logging.debug("  Error, unable to extract DTD from operations params")
            return None
        
        try:
            dtd_value = float(dtd_search.group(1))
        except:
            logging.debug("Unable to convert DTD to float: " + dtd_search.group(1))
            return None
            
        
        # logging.debug("dtd_value: " + str(dtd_value))
        return dtd_value
        
    elif mobility_op_type == "STATUS":
        # logging.debug("Got STATUS message")
        
        dtd_search = re.search('DTD:(.*),SPEED:',ops_params_value)

        if not dtd_search:
            logging.debug("Error, unable to extract DTD from operations params")
            return None
        
        try:
            dtd_value = float(dtd_search.group(1))
        except:
            # logging.debug("Unable to convert DTD to float: " + dtd_search.group(1))
            return None
            
        
        logging.debug("  dtd_value: " + str(dtd_value))

        return dtd_value
    else:
        logging.debug("  Got invalid mobility ops message")


# checks all match params for two give packets
def check_if_data_matches(source_packet_params,data_to_search_params,source_packet_to_match,search_packet):

    all_fields_match = True

    for match_i in range(0,num_match_keys):
        source_packet_key = source_packet_params[J2735_message_type_name]["match_keys"][match_i]["key"]
        search_packet_key = data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["key"]

        logging.debug("  source_packet_key: " + str(source_packet_key))
        logging.debug("  search_packet_key: " + str(search_packet_key))

        # if the source or search packet match key are none. the same index of each match key should align. 
        # see definition at the top of the file for more info
        if (
                source_packet_key == None or
                search_packet_key == None
        ):
            logging.debug("  Skipping match key " + str(match_i) + " since one or more keys are None: " + str(source_packet_key) + "," + str(search_packet_key))
            continue

        
        source_packet_value = source_packet_to_match[source_packet_key]
        search_packet_value = search_packet[search_packet_key]

        if "extract_mobility_dtd" in source_packet_params[J2735_message_type_name]["match_keys"][match_i] and source_packet_params[J2735_message_type_name]["match_keys"][match_i]["extract_mobility_dtd"]:
            
            extracted_dtd = extract_dtd_from_mob_ops(source_packet_value)

            if extracted_dtd != None:
                source_packet_value = extracted_dtd
            else:
                all_fields_match = False
                break



        if "extract_mobility_dtd" in data_to_search_params[J2735_message_type_name]["match_keys"][match_i] and data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["extract_mobility_dtd"]:
            
            extracted_dtd = extract_dtd_from_mob_ops(search_packet_value)

            if extracted_dtd != None:
                search_packet_value = extracted_dtd
            else:
                all_fields_match = False
                break

        if "divide_by" in source_packet_params[J2735_message_type_name]["match_keys"][match_i]:
            source_packet_value = float(source_packet_value)/source_packet_params[J2735_message_type_name]["match_keys"][match_i]["divide_by"]
        
        if "divide_by" in data_to_search_params[J2735_message_type_name]["match_keys"][match_i]:
            search_packet_value = float(search_packet_value)/data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["divide_by"]

        if "multiply_by" in source_packet_params[J2735_message_type_name]["match_keys"][match_i]:
            source_packet_value = float(source_packet_value)*source_packet_params[J2735_message_type_name]["match_keys"][match_i]["multiply_by"]
        
        if "multiply_by" in data_to_search_params[J2735_message_type_name]["match_keys"][match_i]:
            search_packet_value = float(search_packet_value)*data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["multiply_by"]
            
        if "radians" in source_packet_params[J2735_message_type_name]["match_keys"][match_i] and source_packet_params[J2735_message_type_name]["match_keys"][match_i]["radians"]:
            try:
                source_packet_value = math.degrees(float(source_packet_value))
            except:
                logging.error("[!!!] Unable to convert to radians: " + source_packet_value)

        if "radians" in data_to_search_params[J2735_message_type_name]["match_keys"][match_i] and data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["radians"]:
            try:
                search_packet_value = math.degrees(float(search_packet_value))
            except:
                logging.error("[!!!] Unable to convert to radians: " + search_packet_value)

        if "round" in source_packet_params[J2735_message_type_name]["match_keys"][match_i] and source_packet_params[J2735_message_type_name]["match_keys"][match_i]["round"]:
            try:
                source_packet_value = round(float(source_packet_value),source_packet_params[J2735_message_type_name]["match_keys"][match_i]["round_decimals"])
            except:
                logging.error("[!!!] Unable to round: " + source_packet_value)

        if "round" in data_to_search_params[J2735_message_type_name]["match_keys"][match_i] and data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["round"]:
            try:
                search_packet_value = round(float(search_packet_value),data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["round_decimals"])
            except:
                logging.error("[!!!] Unable to round: " + search_packet_value)


        spat_state_mappings = {
            "VUG::Entities::Signals::TrafficLightState_Green" : "green",
            "protected-Movement-Allowed" : "green",

            "VUG::Entities::Signals::TrafficLightState_Red" : "red",
            "stop-And-Remain" : "red",

            "VUG::Entities::Signals::TrafficLightState_Yellow" : "yellow",
            "protected-clearance" : "yellow",            

        }

        if "spat_state" in source_packet_params[J2735_message_type_name]["match_keys"][match_i] and source_packet_params[J2735_message_type_name]["match_keys"][match_i]["spat_state"]:
            source_packet_value = spat_state_mappings[source_packet_value]
        
        if "spat_state" in data_to_search_params[J2735_message_type_name]["match_keys"][match_i] and data_to_search_params[J2735_message_type_name]["match_keys"][match_i]["spat_state"]:
            search_packet_value = spat_state_mappings[search_packet_value]

        if  ( source_packet_value != search_packet_value ):
            
            #TODO this logic could be better 
            if "buffer" in source_packet_params[J2735_message_type_name]["match_keys"][match_i]:
                try:
                    float(search_packet_value)
                    float(source_packet_value)
                except:
                    logging.warning("Unable to apply buffer since one of these is not a number: " + str(search_packet_value) + " : "+ str(source_packet_value))
                    all_fields_match = False
                    break

                source_buffer = source_packet_params[J2735_message_type_name]["match_keys"][match_i]["buffer"]
                if abs(source_packet_value - search_packet_value) >  source_buffer:
                    logging.debug("  [!!!] VALUES DO NOT MATCH WITHIN BUFFER [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value))
                    all_fields_match = False
                    break
                else:
                    logging.debug("  Values Match within buffer [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value) + " +/- " + str(source_buffer))
            
            else:

                logging.debug("  [!!!] VALUES DO NOT MATCH [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value))
                all_fields_match = False
                break
        else:
            logging.debug("  Values Match [" + str(source_packet_key) + "] " + str(source_packet_value) + " == " + str(search_packet_value))
    
    
    return all_fields_match

# prints all the match params and values for two given packets
def print_keys(source_params,check_params,source_packet,check_packet,log_level):
    for match_i in range(0,num_match_keys):
            
        source_key = source_params[J2735_message_type_name]["match_keys"][match_i]["key"]
        check_key = check_params[J2735_message_type_name]["match_keys"][match_i]["key"]

        if (  source_key == None or check_key == None ):
            continue
        if log_level == "debug":
            logging.debug("  - " + source_packet[source_key] + " == " + check_packet[check_key])
        elif log_level == "info":
            logging.info("  - " + source_packet[source_key] + " == " + check_packet[check_key])
        elif log_level == "warning":
            logging.warning("  - " + source_packet[source_key] + " == " + check_packet[check_key])

def clean_name(input_name):
    logging.debug("Dirty Name: " + input_name)
    clean_name = re.sub('\.csv', '', input_name)
    clean_name = re.sub('\.\/data\/.*\/', '', clean_name)
    clean_name = re.sub('[^A-Za-z0-9 _-]+', '', clean_name)
    clean_name = re.sub(' ', '_', clean_name)
    
    clean_name = clean_name.lower()
    
    logging.debug("Clean Name: " + clean_name)
    return clean_name

def load_data(dataset_name,dataset_infile,dataset_type,clock_skew_from_source):

    dataset_name_clean = clean_name(dataset_name)

    logging.info("----- LOADING DATA FOR " + dataset_name_clean + " -----")

    data_infile_obj = open(dataset_infile,'r')
    data_infile_reader = csv.DictReader(data_infile_obj,delimiter=',')
    data_infile_headers = data_infile_reader.fieldnames
    logging.debug("  Data Headers: " + str(data_infile_headers))

    data_list = list(data_infile_reader)
    total_packets = len(data_list)

    logging.info("  Total Packets: " + str(total_packets))

    if dataset_type == "pcap":
        dataset_params = data_params["pcap_params"]
        dataset_index_column_name = "packetIndex"
    elif dataset_type == "tdcs":
        dataset_params = data_params["tdcs_params"]
        dataset_index_column_name = "rowID"


    
    num_datasets_loaded = len(all_data)
    
    all_data.append({
        "dataset_name"                  : dataset_name_clean,
        "data_order"                    : num_datasets_loaded + 1,
        "original_data_list"            : data_list,
        "filtered_data_list"            : [],
        "dataset_type"                  : dataset_type,
        "dataset_params"                : dataset_params,
        "clock_skew_from_source"        : clock_skew_from_source,
        "dataset_index_column_name"     : dataset_index_column_name,
        "found_packet_matching_search"  : False,
    })

def get_obj_by_key_value(obj_array,key,value):
    for index, element in enumerate(obj_array):
        if element[key] == value:
            return index

def check_for_dropped_packets():

    source_data_obj_index = get_obj_by_key_value(all_data,"data_order",1)
    source_data_obj = all_data[source_data_obj_index]
    source_data_list_filtered = source_data_obj["filtered_data_list"]
    source_packet_params = source_data_obj["dataset_params"]

    dropped_packet_counts = {}

    for dataset_i in range(1,len(all_data)):
        dropped_packet_counts[all_data[dataset_i]["dataset_name"]] = 0

    logging.debug("----- CHECKING FOR DROPPED PACKETS -----")
    for source_i,source_packet in enumerate(source_data_list_filtered):
        
        for dataset_i in range(1,len(all_data)):
            
            # i know this is lazy, i already had it written this way before :)
            dataset = all_data[dataset_i]

            # check to make sure we did not reach the end of the file on the dataset 
            if source_i >= len(dataset["filtered_data_list"]):
                logging.debug("Reached end of " + dataset["dataset_name"] + ", stopping dropped packet check")
                
                print("\nDropped Packet Totals: ")
                for dataset_name in dropped_packet_counts:
                    print("\t" + dataset_name + ": " + str(dropped_packet_counts[dataset_name]))

                return
            
            logging.debug("Checking against source packet: " + source_packet[source_data_obj["dataset_index_column_name"]])
            
            current_dataset_packet = dataset["filtered_data_list"][source_i]

            all_fields_match = check_if_data_matches(source_packet_params,dataset["dataset_params"],source_packet,current_dataset_packet)            

            if not all_fields_match:
                logging.warning("  [!!!] Found dropped packet in " + dataset["dataset_name"] +  " [" + source_packet[source_data_obj["dataset_index_column_name"]] + ":" + current_dataset_packet[dataset["dataset_index_column_name"]] + "]: ")
                print_keys(source_packet_params,dataset["dataset_params"],source_packet,current_dataset_packet,"warning")

                dropped_packet_counts[dataset["dataset_name"]] += 1

                # insert a filler row in the data lists with the dropped packet
                dropped_packet_placeholder = {}

                for key in current_dataset_packet:
                    dropped_packet_placeholder[key] = "DROPPED PACKET"

                dataset["filtered_data_list"].insert(source_i ,dropped_packet_placeholder)

            else:
                logging.debug("  Found matching packet in " + dataset["dataset_name"] +  " [" + source_packet[source_data_obj["dataset_index_column_name"]] + ":" + current_dataset_packet[dataset["dataset_index_column_name"]] + "]: ")
                print_keys(source_packet_params,dataset["dataset_params"],source_packet,current_dataset_packet,"debug")
    
    print("\nDropped Packet Totals: ")
    for dataset_name in dropped_packet_counts:
        print("\t" + dataset_name + ": " + str(dropped_packet_counts[dataset_name]))             

def calculate_performance_metrics():

    source_data_obj_index = get_obj_by_key_value(all_data,"data_order",1)
    source_data_obj = all_data[source_data_obj_index]
    source_data_list_filtered = source_data_obj["filtered_data_list"]

    logging.info("----- CALCULATING PERFORMANCE METRICS -----")
    for source_i,source_packet in enumerate(source_data_list_filtered):

        current_row_data = {}

        # add source data packet index
        current_row_data[ source_data_obj["dataset_name"] + "_" + source_data_obj["dataset_index_column_name"] ] = source_packet[source_data_obj["dataset_index_column_name"]]

        source_packet_timestamp = source_packet["packetTimestamp"]
        logging.debug("----- CALCULATING PERFORMANCE FOR SOURCE PACKET " + source_packet[source_data_obj["dataset_index_column_name"]] + " -----")
        logging.debug("source_packet_timestamp: " + str(source_packet_timestamp))

        if J2735_message_type_name == "BSM":

            # calculate the bsm broadcast latency
            secMark = float(source_packet["secMark"])
            packet_timestamp = datetime.datetime.fromtimestamp(int(float(source_packet_timestamp)))
            roundDownMinTime = datetime.datetime(packet_timestamp.year,packet_timestamp.month,packet_timestamp.day,packet_timestamp.hour,packet_timestamp.minute).timestamp()
            packetSecondsAfterMin = (float(source_packet_timestamp) - roundDownMinTime)
            bsm_broadcast_latency = packetSecondsAfterMin*1000 - secMark

            if (bsm_broadcast_latency < 0) :
                logging.debug("[!!!] Minute mismatch")
                bsm_broadcast_latency = bsm_broadcast_latency + 60000

            current_row_data["bsm_broadcast_latency"] = bsm_broadcast_latency
    
        # loop through all datasets except the first (source)
        for dataset_i in range(1,len(all_data)):
            
            # check to make sure we did not reach the end of the file on the dataset 
            if source_i >= len(all_data[dataset_i]["filtered_data_list"]):
                logging.debug("Reached end of " + all_data[dataset_i]["dataset_name"] + ", stopping dropped packet check")
                return

            current_dataset_packet = all_data[dataset_i]["filtered_data_list"][ source_i ]
            # current_dataset_packet = all_data[dataset_i]["filtered_data_list"][ source_i]

            # add dataset packet index
            current_row_data[ all_data[dataset_i]["dataset_name"] + "_" + all_data[dataset_i]["dataset_index_column_name"] ] = current_dataset_packet[all_data[dataset_i]["dataset_index_column_name"]]


            if all_data[dataset_i]["dataset_type"] == "pcap":
                logging.debug("" + all_data[dataset_i]["dataset_name"] + "_packet_index: " + current_dataset_packet["packetIndex"])

                if current_dataset_packet["packetIndex"] == "DROPPED PACKET":
                    dataset_total_latency = "DROPPED PACKET"
                    current_row_data[ all_data[dataset_i]["dataset_name"] + "_timestamp"] = "DROPPED PACKET"
                else:
                    pcap_timestamp = float(current_dataset_packet["packetTimestamp"])
                    logging.debug("pcap_timestamp: " + str(pcap_timestamp))

                    current_row_data[ all_data[dataset_i]["dataset_name"] + "_timestamp"] = pcap_timestamp
        
                    dataset_total_latency = pcap_timestamp - float(source_packet_timestamp)
                    logging.debug("dataset_total_latency: " + str(dataset_total_latency))

                # calculate the incremental latency (latency from previous step to this step)
                # can not calculate incremental latency of the source data (no previous step to subtract from)
                if (dataset_i != 1):
                    if current_dataset_packet["packetIndex"] == "DROPPED PACKET":
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_incremental_latency"] = "DROPPED PACKET"
                    elif current_row_data[ all_data[dataset_i-1]["dataset_name"] + "_latency"] == "DROPPED PACKET":
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_incremental_latency"] = "NA"
                    else:
                        dataset_incremental_latency = dataset_total_latency - current_row_data[ all_data[dataset_i-1]["dataset_name"] + "_latency"]
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_incremental_latency"] = dataset_incremental_latency
                        logging.debug("dataset_incremental_latency: " + str(dataset_incremental_latency))


                current_row_data[ all_data[dataset_i]["dataset_name"] + "_latency"] = dataset_total_latency
            
            elif all_data[dataset_i]["dataset_type"] == "tdcs":
                logging.debug("" + all_data[dataset_i]["dataset_name"] + "_packet_index: " + current_dataset_packet["rowID"])
                            
                # if the previous dataset is from a tdcs, we want to know how long it took to go from created (committed) at the source
                # and received and the dest. this is tdcs_time_of_receipt - tdcs_time_of_commit
                if all_data[dataset_i-1]["dataset_type"] == "tdcs":
                    
                    if current_dataset_packet["rowID"] == "DROPPED PACKET":
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_tdcs_time_of_receipt"] = "DROPPED PACKET"
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_tdcs_commit_to_receipt"] = "DROPPED PACKET"
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_latency"] = "DROPPED PACKET"
                    else:
                        tdcs_time_of_creation = float(current_dataset_packet["const^Metadata,TimeOfCreation"])/1000000000
                        tdcs_time_of_commit = float(current_dataset_packet["Metadata,TimeOfCommit"])/1000000000
                        tdcs_time_of_receipt = float(current_dataset_packet["Metadata,TimeOfReceipt"])/1000000000
                        
                        logging.debug("tdcs_time_of_receipt: " + str(tdcs_time_of_receipt))
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_tdcs_time_of_receipt"] = tdcs_time_of_receipt
                       
                        # this is really a sanity check. it should be the same as the incremental latency
                        tdcs_commit_to_receipt = tdcs_time_of_receipt - tdcs_time_of_commit
                        logging.debug("tdcs_commit_to_receipt: " + str(tdcs_commit_to_receipt))
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_tdcs_commit_to_receipt"] = tdcs_commit_to_receipt

                        dataset_total_latency = tdcs_time_of_receipt - float(source_packet_timestamp)
                        logging.debug("dataset_total_latency: " + str(dataset_total_latency))
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_latency"] = dataset_total_latency


                # if the previous dataset is a pcap, we want to know how long it took from the adapter receiving it to it being committed
                elif all_data[dataset_i-1]["dataset_type"] == "pcap":
                    # if dropped packet, write that row accordingly
                    if current_dataset_packet["rowID"] == "DROPPED PACKET":
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_latency"] = "DROPPED PACKET"
                    else:
                        tdcs_time_of_creation = float(current_dataset_packet["const^Metadata,TimeOfCreation"])/1000000000
                        tdcs_time_of_commit = float(current_dataset_packet["Metadata,TimeOfCommit"])/1000000000
                        tdcs_time_of_receipt = float(current_dataset_packet["Metadata,TimeOfReceipt"])/1000000000
                        
                        logging.debug("tdcs_time_of_commit: " + str(tdcs_time_of_commit))
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "tdcs_time_of_commit"] = tdcs_time_of_commit

                        dataset_total_latency = tdcs_time_of_commit - float(source_packet_timestamp)
                        logging.debug("dataset_total_latency: " + str(dataset_total_latency))
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_latency"] = dataset_total_latency
        
                else:
                    logging.debug("[???] HOW DID WE GET HERE????")
                    sys.exit()

                # calculate the incremental latency (latency from previous step to this step)
                # can not calculate incremental latency of the source data (no previous step to subtract from)

                if (dataset_i != 1):                    
                    if current_dataset_packet["rowID"] == "DROPPED PACKET":
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_incremental_latency"] = "DROPPED PACKET"
                    elif current_row_data[ all_data[dataset_i-1]["dataset_name"] + "_latency"] == "DROPPED PACKET":
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_incremental_latency"] = "NA"
                    else:
                        dataset_incremental_latency = dataset_total_latency - current_row_data[ all_data[dataset_i-1]["dataset_name"] + "_latency"]
                        current_row_data[ all_data[dataset_i]["dataset_name"] + "_incremental_latency"] = dataset_incremental_latency
                        logging.debug("dataset_incremental_latency: " + str(dataset_incremental_latency))
                
        
        # if this is the first iteration, write the headers
        if(source_i) == 0:
            results_outfile_writer.writerow(current_row_data.keys())

        # write the values to a row
        logging.debug("current_row_data: " + str(current_row_data) + "\n")
        results_outfile_writer.writerow(current_row_data.values())
        


#################### LOAD DATA ####################

def load_data_user_input():
        
    still_loading_data = True
    loaded_filenames = []

    if J2735_message_type_name == "Mobility_Operations-INFO" or J2735_message_type_name == "Mobility_Operations-STATUS":
        J2735_message_type_folder_name = "Mobility_Operations"
    else:
        J2735_message_type_folder_name = J2735_message_type_name
    
    while still_loading_data == True:
        if len(all_data) > 0:
            print("\n\n\nCurrently Loaded Datasets: ")
            for dataset in all_data:
                print("\t" + dataset["dataset_name"])



        print("\nAvailable Dataset input files:")

        try:
            available_dataset_list = glob.glob("./data/" + J2735_message_type_folder_name + "/*")
        except:
            print("[!!!] No data found at " + "./data/" + J2735_message_type_folder_name)

        print("\nWhat dataset would you like to load? [#]\n")
        for dataset_i,dataset_path in enumerate(available_dataset_list):
            if dataset_path in loaded_filenames:
                continue
            print("[" + str(dataset_i + 1) + "] " + dataset_path)

        dataset_selection_index = input("\n    --> ")

        try:
            dataset_selected = available_dataset_list[int(dataset_selection_index) -1]
        except:
            print("[!!!] Invalid selection, try again")
            continue

        dataset_type = input("\nWhat type of data is this? [pcap/tdcs] ")

        if not dataset_type in ["pcap","tdcs"]:
            print("[!!!] Invalid selection, try again")
            continue
        
        print("\n Importing " + dataset_selected)
        load_data(dataset_selected,dataset_selected,dataset_type,0)

        loaded_filenames.append(dataset_selected)

        load_another_dataset_yn = input('\nWould load additional datasets? [y/n] ').lower()

        if not load_another_dataset_yn.startswith('y'):
            still_loading_data = False

#################### SELECT SOURCE VEHICLE ####################

voices_vehicles = [
        {
            "tena_host_id"       : "CARMA-TFHRC-LIVE",
            "host_static_id":   "DOT-45243", #CARMA-TFHRC-LIVE",
            "bsm_id"        : "f03ad610",
            "platoon_order" : 1, # this can be used for identifying what fields to look at in platoon sdos 
        },
        {
            "tena_host_id"       : "CARMA-TFHRC",
            "host_static_id":   "CARMA-TFHRC",
            "bsm_id"        : "f03ad608",
        },
        {
            "tena_host_id"       : "CARMA-SPR",
            "host_static_id":   "CARMA-SPR",
            "bsm_id"        : "f03ad612",
        },
        {
            "tena_host_id"       : "CARMA-AUG",
            "host_static_id":   "CARMA-AUG",
            "bsm_id"        : "f03ad614",
            "platoon_order" : 2,
        },
        {
            "tena_host_id"       : "CARMA-MITRE",
            "host_static_id":   "CARMA-MITRE",
            "bsm_id"        : "f03ad616",
            "platoon_order" : 3,
        },
        {
            "tena_host_id"       : "CARLA-MANUAL-1",
            "host_static_id":   "CARLA-MANUAL-1",
            "bsm_id"        : "f03ad618",
        },
    ]

def select_vehicle_user_input():

    print("\nWhat is the source vehicle? [#]\n")
    for vehicle_i,vehicle in enumerate(voices_vehicles):
        print("\n[" + str(vehicle_i + 1) + "] \tHOST ID: " + vehicle["host_static_id"] + " \n\tTENA ID: " + vehicle["tena_host_id"] + " \n\tBSM ID: " + vehicle["bsm_id"])

    vehicle_index = input("\n    --> ")

    try:
        selected_vehicle = voices_vehicles[int(vehicle_index) -1]      
        return selected_vehicle

    except:
        print("[!!!] Invalid selection, try again")
        sys.exit()

#################### SELECT MESSAGE TYPE ####################

def select_message_type_user_input():

    print("\nWhat data type would you like to analyze? [#]\n")
    for type_i,message_type in enumerate(J2735_message_types):
        print("[" + str(type_i + 1) + "] " + message_type)

    J2735_message_type_index = input("\n    --> ")

    try:
        J2735_message_type_name = J2735_message_types[int(J2735_message_type_index) -1]
        J2735_message_type_name = re.sub(" ","_",J2735_message_type_name)
        return J2735_message_type_name
    except:
        print("[!!!] Invalid selection, try again")

############################## DEFINE GENERAL VARIABLES ##############################

# example schema for all_data
# all_data = [
#     {
#         "dataset_name"                    : "some_dataset_name",
#         "data_order"                      : 1,
#         "original_data_list"              : [ {},{},{},{}... ],
#         "filtered_data_list"              : [ {},{},{},{}...  ],
#         "dataset_type"                    : "pcap" or "tdcs"
#         "dataset_params"                  : {},
#         "found_packet_matching_search"    : bool,
#         "clock_skew_from_source"          : float,
#         "dataset_index_column_name"       : packetIndex for pcap, rowID for tdcs,
#     },
#     {
#         "dataset_name"                    : "some_other_dataset_name",
#         "data_order"                      : 2,
#         "original_data_list"              : [ {},{},{},{}... ],
#         "filtered_data_list"              : [ {},{},{},{}...  ],
#         "dataset_type"                    : "pcap" or "tdcs"
#         "dataset_params"                  : {},
#         "found_packet_matching_search"    : bool,
#         "clock_skew_from_source"          : float,
#         "dataset_index_column_name"       : packetIndex for pcap, rowID for tdcs,
#     },
#     ...

# ]


# specifies the number of match_keys defined in the params for each data source
num_match_keys = 5

J2735_message_types = ["MAP","SPAT","BSM","Mobility_Request","Mobility_Response","Mobility_Path","Mobility_Operations-STATUS","Mobility_Operations-INFO","Traffic_Control_Request","Traffic_Control_Message"]

desired_intersection_name = "TFHRC West Intersection"
desired_signal_id = "905"

all_data = []

############################## MAIN ##############################

argparser = argparse.ArgumentParser(
    description='VOICES Performance Calculation Script')
argparser.add_argument(
    '-l', '--log_level',
    metavar='<log_level>',
    type=str,
    dest='log_level',
    default="WARNING",
    help='set the logging level OPTIONS: [DEBUG,INFO,WARNING,ERROR,CRITICAL]')
argparser.add_argument(
    '-t', '--data-type',
    metavar='<data_type>',
    dest='data_type',
    type=str,
    default=None,
    help='Data type to be analyzed OPTIONS: [MAP,SPAT,BSM,Mobility_Request,Mobility_Response,Mobility_Path,Mobility_Operations-STATUS,Mobility_Operations-INFO,Traffic_Control_Request,Traffic_Control_Message]')
argparser.add_argument(
    '-s', '--source-vehicle',
    metavar='<source_vehicle_index>',
    dest='source_vehicle_index',
    type=int,
    default=None,
    help='Index of vehicle to analyze data for: [#]')
# argparser.add_argument(
#     '-p', '--port',
#     metavar='P',
#     default=2000,
#     type=int,
#     help='TCP port to listen to (default: 2000)')
# argparser.add_argument(
#     '-a', '--autopilot',
#     action='store_true',
#     help='enable autopilot')
args = argparser.parse_args()

log_level = getattr(logging, args.log_level)

logging.basicConfig(level=log_level,filename='performance_analysis.log', filemode='w', format='%(name)s:%(levelname)s:%(message)s')


print("\n==========================================================")
print("========== STARTING VOICES PERFORMANCE ANALYSIS ==========")
print("==========================================================\n")

# print("args: " + str(args))

print("Log Level: " + str(args.log_level))

logging.info("========== STARTING VOICES PERFORMANCE ANALYSIS ==========")



############################## SET CLOCK SKEWS ##############################

live_to_nist_clock_skew = 0.060723
virtual_to_nist_clock_skew = -0.051729

live_to_virtual_clock_skew = live_to_nist_clock_skew - virtual_to_nist_clock_skew

virt_to_v2x_clock_skew = -44.806000
virt_to_second_clock_skew = -45.000999
virt_to_third_clock_skew = -45.786999

live_to_v2x_clock_skew = live_to_virtual_clock_skew + virt_to_v2x_clock_skew
live_to_second_clock_skew = live_to_virtual_clock_skew + virt_to_second_clock_skew
live_to_third_clock_skew = live_to_virtual_clock_skew + virt_to_third_clock_skew


############################## USER INPUT ##############################

if args.data_type == None:
    J2735_message_type_name = select_message_type_user_input()
else:
    if not args.data_type in J2735_message_types:
        print("ERROR: selected message type is not valid, try again")
        print("\n\tValid Types: " + str(J2735_message_types) + "\n")
        sys.exit()

    J2735_message_type_name = str(args.data_type)


print("Message Type: " + J2735_message_type_name + " selected")

# we do not need to select a vehicle for spat
if J2735_message_type_name != "SPAT":
    if args.source_vehicle_index == None:
        vehicle_info = select_vehicle_user_input()
    else:
        
        if args.source_vehicle_index > len(voices_vehicles):
            print("ERROR: Source Vehicle index out of bounds, try again")
            print("\nValid Vehicles:")
            for vehicle_i,vehicle in enumerate(voices_vehicles):
                print("\n[" + str(vehicle_i + 1) + "] \tHOST ID: " + vehicle["host_static_id"] + " \n\tTENA ID: " + vehicle["tena_host_id"] + " \n\tBSM ID: " + vehicle["bsm_id"])

            sys.exit()
        
        vehicle_info = voices_vehicles[args.source_vehicle_index - 1]
else:
    # but, we need values for the params, so we put one in as a placeholder...
    # probably can do this better
    vehicle_info = voices_vehicles[0]

desired_bsm_id = vehicle_info["bsm_id"]
desired_tena_identifier = vehicle_info["tena_host_id"]
desired_host_static_id = vehicle_info["host_static_id"]

# there is an export issue with TDCS which needs to be fixed manully for platoon SDOs
# to fix, open in excel and find the column candidateVehicles^trajectoryStart.position.geocentric_asTransmitted.xInMeters,Float64 (1) (optional)
# find any columns with a value and insert one cell, pushing the entire row to the right (from that point to the right)
# insert a cell in the same way at the header
# delete the entire column created with no header
# select all cells and change format to Number
# remove two decimal places 
# save


if vehicle_info["platoon_order"] == 1:
    mob_ops_tdcs_field = "downtrackDistanceInMeters,Float32"
    extract_tdcs_mobility_dtd = False
elif vehicle_info["platoon_order"] == 2:
    mob_ops_tdcs_field = "joinedVehicles^strategyParameters,String (1)"
    extract_tdcs_mobility_dtd = True
elif vehicle_info["platoon_order"] == 3:
    mob_ops_tdcs_field = "joinedVehicles^strategyParameters,String (2)"
    extract_tdcs_mobility_dtd = True
    

print("Source Vehicle: " + desired_tena_identifier + "(" + desired_bsm_id +  ") selected")

############################## SET DATA PARAMS ##############################

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
                    "round_decimals": 6,
                    "buffer"    : 0.000001,
                },
                {
                    "key"       : "longitude",
                    "round"     : True,
                    "round_decimals": 6,
                    "buffer"    : 0.000001,
                },
                {
                    "key"       : "secMark",
                },
                {
                    "key"       : "speed(m/s)",
                    "round"     : True,
                    "round_decimals": 2,
                    "buffer"    : 0.03,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "SPAT" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "intersectionName",
                    "value"         : desired_intersection_name,  
                                                       
                },
            ],
            
            "skip_if_eqs"       : [
                {
                    "key"           : "phase2_eventState",
                    "value"         : "protected-Movement-Allowed",  # only way to align the data is to skip until a value changes
                    "start_only"    : True                         
                },
            ],

            "match_keys"        : [
                {
                    "key"       : "phase2_eventState",
                    "spat_state": True,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Path" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "hostStaticId",
                    "value"         : desired_host_static_id,  
                                                       
                },
                {
                    "key"           : "hostBSMId",      
                    "value"         : desired_bsm_id, 
                }

            ],
            
            "skip_if_eqs"       : [
               
            ],

            "match_keys"        : [
                {
                    "key"       : "hostStaticId",
                },
                {
                    "key"       : "hostBSMId",
                },
                {
                    "key"       : "planId",
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Operations-STATUS" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "hostStaticId",
                    "value"         : desired_host_static_id,             
                },
                {
                    "key"           : "headerTimestamp",
                    "value"         : None,
                    "mobility_timestamp_check" : True,                        
                },
            ],
            
            "skip_if_eqs"       : [
                { # excluding info messages because they are sent at the same time, 
                  # and sometimes tena plugins load them in a different order than the pcap
                    "key"           : "operationParams",
                    "value"         : "INFO",
                    "starts_with"   : True  
                                                       
                },
            ],

            "match_keys"        : [
                {
                    "key"       : "headerTimestamp",
                    "multiply_by"  : 1000000,
                },
                {
                    "key"       : "operationParams",
                    "extract_mobility_dtd" : True,
                    "round"     : True,
                    "round_decimals" : 3,
                    "buffer"    : 0.002,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Operations-INFO" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "hostStaticId",
                    "value"         : desired_host_static_id,                              
                },
            ],
            
            "skip_if_eqs"       : [
                { # excluding status messages because they are sent at the same time, 
                  # and sometimes tena plugins load them in a different order than the pcap
                    "key"           : "operationParams",
                    "value"         : "STATUS",
                    "starts_with"   : True  
                                                       
                },
            ],

            "match_keys"        : [
                {
                    "key"       : "headerTimestamp",
                    "multiply_by"  : 1000000,
                },
                {
                    "key"       : "operationParams",
                    "extract_mobility_dtd" : True,
                    "round"     : True,
                    "round_decimals" : 3,
                    "buffer"    : 0.002,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Request" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "hostStaticId",
                    "value"         : desired_host_static_id,  
                                                       
                },
            ],
            
            "skip_if_eqs"       : [
            ],

            "match_keys"        : [
                {
                    "key"       : "headerTimestamp",
                    "multiply_by"  : 1000000,
                },
                {
                    "key"       : "strategyParams",
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Response" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "hostStaticId",
                    "value"         : desired_host_static_id,  
                                                       
                },
            ],
            
            "skip_if_eqs"       : [
            ],

            "match_keys"        : [
                {
                    "key"       : "headerTimestamp",
                    "multiply_by"  : 1000000,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
    },
    
    "tdcs_params" : {
        "BSM" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "const^identifier,String",
                    "value"         : desired_tena_identifier,
                }

            ],
            
            "skip_if_eqs"       : [
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Discovery",
                },
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Destruction",
                },
            ],

            "match_keys"        : [
                {
                    "key"       : "tspi.position.geodetic_asTransmitted.latitudeInDegrees,Float64 (optional)",
                    "round"     : True,
                    "round_decimals": 6,
                    "buffer"    : 0.000001,
                },
                {
                    "key"       : "tspi.position.geodetic_asTransmitted.longitudeInDegrees,Float64 (optional)",
                    "round"     : True,
                    "round_decimals": 6,
                    "buffer"    : 0.000001,
                },
                {
                    "key"       : "msWithinMinute,UInt16",
                },
                {
                    "key"       : "tspi.velocity.ltpENU_asTransmitted.vxInMetersPerSecond,Float32 (optional)",
                    "round"     : True,
                    "round_decimals": 2,
                    "buffer"    : 0.03,
                },
                
                {
                    "key"       : None,
                }
            ]
        },
        "SPAT" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "const^signalID,String",
                    "value"         : desired_signal_id,
                }

            ],
            
            "skip_if_eqs"       : [
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Discovery",
                },
            ],

            "match_keys"        : [
                {
                    "key"       : "Enum,VUG::Entities::Signals::TrafficLightState,currentState",
                    "spat_state": True,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Path" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "header.hostBSMId,String",
                    "value"         : desired_bsm_id,
                }

            ],

            "skip_if_eqs"       : [
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Discovery",
                },
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Destruction",
                },
            ],

            "match_keys"        : [
                {
                    "key"       : "header.hostStaticId,String",
                },
                {
                    "key"       : "header.hostBSMId,String",
                },
                {
                    "key"       : "header.planId,String",
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Operations-STATUS" : {
            "skip_if_neqs"      : [
                # {
                #     "key"           : "const^hostStaticId,String",
                #     "value"         : desired_host_static_id,
                # },
                {
                    "key"           : "urgency,Int32 (optional)",
                    "value"         : "<UNSET>",
                },
                # {
                #     "key"           : "Vector,requestedVehicles,count",
                #     "value"         : "0",
                # },
                {
                    "key"           : "timestamp.nanosecondsSince1970,Int64",
                    "value"         : None,
                    "mobility_timestamp_check" : True,                        
                },

            ],

            "skip_if_eqs"       : [
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Discovery",
                },
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Destruction",
                },
                { # excluding info messages because they are sent at the same time, 
                  # and sometimes tena plugins load them in a different order than the pcap
                    "key"   : "commandSpeedInMetersPerSecond,Float32 (optional)",
                    "value" : "<UNSET>",
                },
            ],

            "match_keys"        : [
                {
                    "key"       : "timestamp.nanosecondsSince1970,Int64",
                    "multiply_by" : 1,
                },
                {
                    "key"       : mob_ops_tdcs_field,
                    "extract_mobility_dtd" : extract_tdcs_mobility_dtd,
                    "round"     : True,
                    "round_decimals" : 3,
                    "buffer"    : 0.002,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Operations-INFO" : {
            "skip_if_neqs"      : [
                # {
                #     "key"           : "const^hostStaticId,String",
                #     "value"         : desired_host_static_id,
                # },
                {
                    "key"           : "urgency,Int32 (optional)",
                    "value"         : "<UNSET>",
                },
                # {
                #     "key"           : "Vector,requestedVehicles,count",
                #     "value"         : "0",
                # },
                {
                    "key"           : "timestamp.nanosecondsSince1970,Int64",
                    "value"         : None,
                    "mobility_timestamp_check" : True,
                                                       
                },
                { # excluding status messages because they are sent at the same time, 
                  # and sometimes tena plugins load them in a different order than the pcap
                    "key"   : "commandSpeedInMetersPerSecond,Float32 (optional)",
                    "value" : "<UNSET>",
                },

            ],

            "skip_if_eqs"       : [
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Discovery",
                },
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Destruction",
                },
                
            ],

            "match_keys"        : [
                {
                    "key"       : "timestamp.nanosecondsSince1970,Int64",
                    "multiply_by" : 1,
                },
                {
                    "key"       : "downtrackDistanceInMeters,Float32",
                    "round"     : True,
                    "round_decimals" : 3,
                    "buffer"    : 0.002,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Request" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "timestamp.nanosecondsSince1970,Int64",
                    "value"         : None,
                    "mobility_timestamp_check" : True,
                                                       
                },
                { 
                    "key"   : "commandSpeedInMetersPerSecond,Float32 (optional)",
                    "value" : "<UNSET>",
                },

            ],

            "skip_if_eqs"       : [
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Discovery",
                },
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Destruction",
                },
                
            ],

            "match_keys"        : [
                {
                    "key"       : "timestamp.nanosecondsSince1970,Int64",
                    "multiply_by" : 1,
                },
                {
                    "key"       : "requestedVehicles^strategyParameters,String (1)",
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
        "Mobility_Response" : {
            "skip_if_neqs"      : [
                {
                    "key"           : "urgency,Int32 (optional)",
                    "value"         : "0",
                },
                {
                    "key"           : "timestamp.nanosecondsSince1970,Int64",
                    "value"         : None,
                    "mobility_timestamp_check" : True,
                                                       
                },
                { 
                    "key"   : "commandSpeedInMetersPerSecond,Float32 (optional)",
                    "value" : "<UNSET>",
                },

            ],

            "skip_if_eqs"       : [
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Discovery",
                },
                {
                    "key"   : "Metadata,Enum,Middleware::EventType",
                    "value" : "Destruction",
                },
                
            ],

            "match_keys"        : [
                {
                    "key"       : "timestamp.nanosecondsSince1970,Int64",
                    "multiply_by" : 1,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                },
                {
                    "key"       : None,
                }
            ]
        },
    }
}

############################## LOAD DATA ##############################

# load_data_user_input()

# live to second vehicle BSM
# load_data("source vehicle","data/BSM/lead_carma_platform_out_decoded_packets_BSM.csv","pcap",0)
# load_data("v2x in pcap","data/BSM/v2xhub_in_decoded_packets_BSM.csv","pcap",0)
# load_data("v2x tdcs","data/BSM/v2xhub-VUG-Track-BSM-20220822124130.csv","tdcs",0)
# load_data("dest veh tdcs","data/BSM/second-VUG-Track-BSM-20220822125045.csv","tdcs",0)
# load_data("dest veh pcap","data/BSM/second_carma_platform_in_decoded_packets_BSM.csv","pcap",0)

# second to third BSM - blocked by unset speed - can delete rows and remove speed match
# load_data("2nd out pcap","data/BSM/second_carma_platform_out_decoded_packets_BSM.csv","pcap",0)
# load_data("2nd tdcs","data/BSM/second-VUG-Track-BSM-20220822125045.csv","tdcs",0)
# load_data("3rd tdcs","data/BSM/third-VUG-Track-BSM-20220822123937.csv","tdcs",0)
# load_data("3rd in pcap","data/BSM/third_carma_platform_in_decoded_packets_BSM.csv","pcap",0)


#  third to second BSM
# load_data("3rd out pcap","data/BSM/third_carma_platform_out_decoded_packets_BSM.csv","pcap",0)
# load_data("3rd tdcs","data/BSM/third_VUG-Track-BSM-20220822123937.csv","tdcs",0)
# load_data("2nd tdcs","data/BSM/second_VUG-Track-BSM-20220822125045.csv","tdcs",0)
# load_data("2nd in pcap","data/BSM/second_carma_platform_in_decoded_packets_BSM.csv","pcap",0)


#  live to second Mobility Path
# load_data("lead out pcap","data/Mobility_Path/lead_carma_platform_out_decoded_packets_Mobility-Path.csv","pcap",0)
# load_data("v2x in pcap","data/Mobility_Path/v2xhub_in_decoded_packets_Mobility-Path.csv","pcap",0)
# load_data("v2x tdcs","data/Mobility_Path/v2xhub-VUG-CARMA-Mobility-Path-20220822124136.csv","tdcs",0)
# load_data("2nd tdcs","data/Mobility_Path/second-VUG-CARMA-Mobility-Path-20220822125049.csv","tdcs",0)
# load_data("2nd in","data/Mobility_Path/second_carma_platform_in_decoded_packets_Mobility-Path.csv","pcap",0)


#  v2x to second spat
# load_data("v2x out pcap","data/SPAT/v2xhub_out_decoded_packets_SPAT.csv","pcap",0)
# load_data("v2x tdcs","data/SPAT/v2x-VUG-Entities-Signals-TrafficLight-20220822124141.csv","tdcs",0)
# load_data("2nd tdcs","data/SPAT/second-VUG-Entities-Signals-TrafficLight-20220822125033.csv","tdcs",0)

# live to second vehicle BSM
# load_data("source vehicle","data/BSM/lead_carma_platform_out_decoded_packets_BSM.csv","pcap",0)
# load_data("v2x in pcap","data/BSM/v2xhub_in_decoded_packets_BSM.csv","pcap",0)
# load_data("v2x tdcs","data/BSM/v2xhub-VUG-Track-BSM-20220909154522.csv","tdcs",0)
# load_data("dest veh tdcs","data/BSM/second-VUG-Track-BSM-20220909163226.csv","tdcs",0)

# v2x to second mobility operations
# load_data("lead out pcap","data/Mobility_Operations/lead_carma_platform_out_decoded_packets_Moblity-Operations.csv","pcap",0)
# load_data("v2x in pcap","data/Mobility_Operations/v2xhub_in_decoded_packets_Moblity-Operations.csv","pcap",0)
# load_data("v2x tdcs","data/Mobility_Operations/v2xhub-VUG-CARMA-Platoon-20220822124140.csv","tdcs",0)
# load_data("second tdcs","data/Mobility_Operations/second-VUG-CARMA-Platoon-20220822125038.csv","tdcs",0)
# load_data("second in pcap","data/Mobility_Operations/second_carma_platform_in_decoded_packets_Moblity-Operations.csv","pcap",0)

# second to v2x mobility operations - there are no info messages for second 
# load_data("second in pcap","data/Mobility_Operations/second-carma_platform_out_decoded_packets_Moblity-Operations.csv","pcap",0)
# load_data("second tdcs","data/Mobility_Operations/second-VUG-CARMA-Platoon-20220910102020.csv","tdcs",0)
# load_data("v2x tdcs","data/Mobility_Operations/v2xhub-VUG-CARMA-Platoon-20220910101914.csv","tdcs",0)
# load_data("v2x out pcap","data/Mobility_Operations/v2xhub_out_decoded_packets_Moblity-Operations.csv","pcap",0)

#  second to v2x mobility request
# load_data("second out pcap","data/Mobility_Request/second-carma_platform_out_decoded_packets_Mobility-Request.csv","pcap",0)
# load_data("second tdcs","data/Mobility_Request/second-VUG-CARMA-Platoon-20220910102020.csv","tdcs",0)
# load_data("v2x tdcs","data/Mobility_Request/v2xhub-VUG-CARMA-Platoon-20220910101914.csv","tdcs",0)
# load_data("v2x out pcap","data/Mobility_Request/v2xhub_out_decoded_packets_Mobility-Request.csv","pcap",0)

#  second to v2x mobility request
load_data("second out pcap","data/Mobility_Request/second_carma_platform_out_decoded_packets_Mobility-Request.csv","pcap",0)
load_data("second tdcs","data/Mobility_Request/second-VUG-CARMA-Platoon-20220822125038.csv","tdcs",0)
load_data("v2x tdcs","data/Mobility_Request/v2xhub-VUG-CARMA-Platoon-20220822124140.csv","tdcs",0)
load_data("v2x out pcap","data/Mobility_Request/v2xhub_out_decoded_packets_Mobility-Request.csv","pcap",0)

#  v2x to second mobility response
# load_data("v2x in pcap","data/Mobility_Response/v2xhub_in_decoded_packets_Mobility-Response.csv","pcap",0)
# load_data("v2x tdcs","data/Mobility_Response/v2xhub-VUG-CARMA-Platoon-20220910101914.csv","tdcs",0)
# load_data("second tdcs","data/Mobility_Response/second-VUG-CARMA-Platoon-20220910102020.csv","tdcs",0)
# load_data("second in pcap","data/Mobility_Response/second-carma_platform_in_decoded_packets_Mobility-Response.csv","pcap",0)


# print("\ntesting exit early")
# sys.exit()


# we need to get all datasets to align to calculate performance
# this is accomplished by taking the first compliant packet (passes all EQ and NEQ) in the source data and looking for it in all other datasets
# once we find the compliant packet in the other datasets, we can start the comparison from there for all future packets
# if the source packet is not found in one of the datasets (dropped packet or something), we need to try the next packet in the source dataset
# to keep data aligned across all sets, we simply remove that packet from all data sources that have it

source_data_obj_index = get_obj_by_key_value(all_data,"data_order",1)
source_data_obj = all_data[source_data_obj_index]
source_data_list_original = source_data_obj["original_data_list"]
source_data_list_filtered = source_data_obj["filtered_data_list"]

source_packet_params = source_data_obj["dataset_params"]

all_datasets_have_offset = False

packets_to_skip = 0
max_packets_to_skip = 30



# loop through the first 30 packets of the source 
while all_datasets_have_offset == False and packets_to_skip <= max_packets_to_skip:
    logging.info("---------- CHECKING ALL DATASETS HAVE FIRST SOURCE PACKET ----------")
    logging.info("  --> Skipping first " + str(packets_to_skip) + " source packets")

    all_datasets_have_offset = True

    # iterate through all datasets and filter the dataset starting at the matched packet
    for dataset in all_data:

        filter_dataset(dataset,packets_to_skip)
        
        # if we go through the whole dataset and we haven't found the matching packet,
        # break to continue to the next source packet
        if not dataset["found_packet_matching_search"]:
            logging.debug("Could not find offset in: " + dataset["dataset_name"] )
            all_datasets_have_offset = False
            break
    
    # if all datasets found a packet matching the source packet, break to stop looking
    if all_datasets_have_offset == True:
        logging.debug("All datasets found source offset")
        break
    else:
        # if one of the datasets did not find the matching source packet:
        # clear filtered data, reset found_packet_matching_search, and increase the packets to skip
        logging.debug("Some datasets could not find source offset, skipping additional source packets")
        for dataset in all_data:
            dataset["filtered_data_list"] = []
            dataset["found_packet_matching_search"] = False

        packets_to_skip += 1
        
        if packets_to_skip == max_packets_to_skip:
            logging.debug("None of the first 30 packets in the source data could be found in all subsiquent datasets, exiting")
            print("\nNone of the first 30 packets in the source data could be found in all subsiquent datasets, exiting")
            sys.exit()



check_for_dropped_packets()

############################## INITIALIZE CSV WRITER ##############################

outfile = "performance_analysis.csv"
results_outfile_obj = open(outfile,'w',newline='')
results_outfile_writer = csv.writer(results_outfile_obj)

calculate_performance_metrics()


print("\n----- ANALYSIS COMPLETE -----")
sys.exit()

