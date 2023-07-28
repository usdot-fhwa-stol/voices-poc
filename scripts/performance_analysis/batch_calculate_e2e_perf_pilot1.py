import sys
import os
import fnmatch
import json
import csv
import re

## TODO
#   - make import files a json object so name doesnt matter
#       - add types and names to data from different sources
#   - 
#
#
#
#


############################## DATA LOCATION PARAMETERS ##############################

# 10.40.36.12:36403
# 10.40.36.12:38035
# 192.168.2.16:33103
# 192.168.2.16:43477
# 192.168.2.6:39957
# 192.168.2.6:40079
# 192.168.55.231:44619
# 192.168.55.244:41403

# TEST Times 

# test 1: 

# 1681497750.65608

# 1681497950.75627

# Test 2: 

# 1681498024.21446

# 1681498053.31621

# Test 3:

# 1681498301.67224

# 1681498332.77518

test_1_site_list = [
    {
        "site_name" : "eco",
        "lvc" : "constructive",
        "is_v2xhub" : False,
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/econolite-20230414143600/_20230414143600/eco_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/econolite-20230414143600/_20230414143600/pilot1_test1-3_eco_ip_packet_in_decoded_packets",
        "pcap_out_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/econolite-20230414143600/_20230414143600/pilot1_test1-3_eco_ip_packet_out_decoded_packets",
        "start_time" : 1681497807.1860852,
        "end_time" : 1681497950.75627,
        "adapter_addresses_by_type" : {
            "J2735-SPAT" : ["10.40.36.12:36403"],
            "TrafficLight" : ["10.40.36.12:38035"]
        },

    },
    {
        "site_name" : "nissan",
        "lvc" : "constructive",
        "is_v2xhub" : False,
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/nissan_20230414144026/nissan_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/nissan_20230414144026/pilot1_test1-3_nissan_ip_packet_in_decoded_packets",
        "pcap_out_dir" : None,
        "start_time" : 1681497807.1860852,
        "end_time" : 1681497950.75627,
        "adapter_addresses_by_type" : {
            "J2735-BSM" : [
                "192.168.2.16:43477",   # test 1-2
                # "192.168.2.16:33103"  # test 3
            ],
        },

    },
    {
        "site_name" : "ucla",
        "is_v2xhub" : False,
        "lvc" : "constructive",
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/UCLA_logs_20230414/UCLA_logs/ucla_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/UCLA_logs_20230414/UCLA_logs/pilot1_test1-3_ucla_ip_packet_in_decoded_packets",
        "pcap_out_dir" : None,
        "start_time" : 1681497807.1860852,
        "end_time" : 1681497950.75627,
        "adapter_addresses_by_type" : {
            # "J2735-BSM" : [
            #     # "192.168.2.6:39957",  # test 1-2
            #     # "192.168.2.6:40079"   # test 3
            # ],
        },

    },
    {
        "site_name" : "v2xhub",
        "is_v2xhub" : True,
        "lvc" : "constructive",
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/v2x_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/pilot1_test1-3_v2x_ip_packet_in_decoded_packets",
        "pcap_out_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/pilot1_test1-3_v2x_ip_packet_out_decoded_packets",
        "start_time" : 1681497807.1860852,
        "end_time" : 1681497950.75627,
        "adapter_addresses_by_type" : {
            "J2735-MAP" : ["192.168.55.244:41403"],
        },

    },


]

test_2_site_list = [
    {
        "site_name" : "eco",
        "lvc" : "constructive",
        "is_v2xhub" : False,
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/econolite-20230414143600/_20230414143600/eco_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/econolite-20230414143600/_20230414143600/pilot1_test1-3_eco_ip_packet_in_decoded_packets",
        "pcap_out_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/econolite-20230414143600/_20230414143600/pilot1_test1-3_eco_ip_packet_out_decoded_packets",
        "start_time" : 1681498024.21446,
        "end_time" : 1681498053.31621,
        "adapter_addresses_by_type" : {
            "J2735-SPAT" : ["10.40.36.12:36403"],
            "TrafficLight" : ["10.40.36.12:38035"]
        },

    },
    {
        "site_name" : "nissan",
        "lvc" : "constructive",
        "is_v2xhub" : False,
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/nissan_20230414144026/nissan_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/nissan_20230414144026/pilot1_test1-3_nissan_ip_packet_in_decoded_packets",
        "pcap_out_dir" : None,
        "start_time" : 1681498024.21446,
        "end_time" : 1681498053.31621,
        "adapter_addresses_by_type" : {
            # "J2735-BSM" : [
            #     # "192.168.2.16:43477",   # test 1-2
            #     # "192.168.2.16:33103"  # test 3
            # ],
        },

    },
    {
        "site_name" : "ucla",
        "is_v2xhub" : False,
        "lvc" : "constructive",
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/UCLA_logs_20230414/UCLA_logs/ucla_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/UCLA_logs_20230414/UCLA_logs/pilot1_test1-3_ucla_ip_packet_in_decoded_packets",
        "pcap_out_dir" : None,
        "start_time" : 1681498024.21446,
        "end_time" : 1681498053.31621,
        "adapter_addresses_by_type" : {
            "J2735-BSM" : [
                "192.168.2.6:39957",    # test 1-2
                # "192.168.2.6:40079"   # test 3
            ],
        },

    },
    {
        "site_name" : "v2xhub",
        "is_v2xhub" : True,
        "lvc" : "constructive",
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/v2x_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/pilot1_test1-3_v2x_ip_packet_in_decoded_packets",
        "pcap_out_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/pilot1_test1-3_v2x_ip_packet_out_decoded_packets",
        "start_time" : 1681498024.21446,
        "end_time" : 1681498053.31621,
        "adapter_addresses_by_type" : {
            "J2735-MAP" : ["192.168.55.244:41403"],
        },

    },


]

test_3_site_list = [
    {
        "site_name" : "eco",
        "lvc" : "constructive",
        "is_v2xhub" : False,
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/econolite-20230414143600/_20230414143600/eco_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/econolite-20230414143600/_20230414143600/pilot1_test1-3_eco_ip_packet_in_decoded_packets",
        "pcap_out_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/econolite-20230414143600/_20230414143600/pilot1_test1-3_eco_ip_packet_out_decoded_packets",
        "start_time" : 1681498302.0121028,
        "end_time" : 1681498332.77518,
        "adapter_addresses_by_type" : {
            "J2735-SPAT" : ["10.40.36.12:36403"],
            "TrafficLight" : ["10.40.36.12:38035"]
        },

    },
    {
        "site_name" : "nissan",
        "lvc" : "constructive",
        "is_v2xhub" : False,
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/nissan_20230414144026/nissan_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/nissan_20230414144026/pilot1_test1-3_nissan_ip_packet_in_decoded_packets",
        "pcap_out_dir" : None,
        "start_time" : 1681498302.0121028,
        "end_time" : 1681498332.77518,
        "adapter_addresses_by_type" : {
            "J2735-BSM" : [
                # "192.168.2.16:43477",   # test 1-2
                "192.168.2.16:33103"  # test 3
            ],
        },

    },
    {
        "site_name" : "ucla",
        "is_v2xhub" : False,
        "lvc" : "constructive",
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/UCLA_logs_20230414/UCLA_logs/ucla_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/UCLA_logs_20230414/UCLA_logs/pilot1_test1-3_ucla_ip_packet_in_decoded_packets",
        "pcap_out_dir" : None,
        "start_time" : 1681498302.0121028,
        "end_time" : 1681498332.77518,
        "adapter_addresses_by_type" : {
            "J2735-BSM" : [
                # "192.168.2.6:39957",    # test 1-2
                "192.168.2.6:40079"   # test 3
            ],
        },

    },
    {
        "site_name" : "v2xhub",
        "is_v2xhub" : True,
        "lvc" : "constructive",
        "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/v2x_exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/pilot1_test1-3_v2x_ip_packet_in_decoded_packets",
        "pcap_out_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/pilot1_test1-3_v2x_ip_packet_out_decoded_packets",
        "start_time" : 1681498302.0121028,
        "end_time" : 1681498332.77518,
        "adapter_addresses_by_type" : {
            "J2735-MAP" : ["192.168.55.244:41403"],
        },

    },


]


# 10.40.36.12:35777 # tleg
# 10.40.36.12:37627 # j2735
# 192.168.2.6:45747 # test 4a carla
# 192.168.2.6:39119 # test 4b carla
# 192.168.55.244:43655 # v2x
# 192.168.55.231:34505 # test 4a carla
# 192.168.55.231:42251 # test 4b carla
# 192.168.55.231:343655 # scenario 

test_4a_site_list = [
    {
        "site_name" : "eco",
        "lvc" : "constructive",
        "is_v2xhub" : False,
        "tdcs_dir" : "/home/andrew/Downloads/test-4/ECONOLITE_20230511150907/exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/test-4/ECONOLITE_20230511150907/pilot-1_test-4_eco_ip_packet_in_decoded_packets",
        "pcap_out_dir" : "/home/andrew/Downloads/test-4/ECONOLITE_20230511150907/pilot-1_test-4_eco_ip_packet_out_decoded_packets",
        "start_time" : 1683832241.16251,
        "end_time" : 1683832294.14485,
        "adapter_addresses_by_type" : {
            "J2735-SPAT" : ["10.40.36.12:37627"],
            "TrafficLight" : ["10.40.36.12:35777"]
        },

    },
    {
        "site_name" : "ucla",
        "is_v2xhub" : False,
        "lvc" : "constructive",
        "tdcs_dir" : "/home/andrew/Downloads/test-4/CARLA-UCLA_20230511120740/exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/test-4/CARLA-UCLA_20230511120740/fixed_pilot-1_test-4_ucla_ip_packet_in_decoded_packets",
        "pcap_out_dir" : None,
        "start_time" : 1683832241.16251,
        "end_time" : 1683832294.14485,
        "adapter_addresses_by_type" : {
            "J2735-BSM" : [
                "192.168.2.6:45747",      # test 4a
                # "192.168.2.6:39119"         # test 4b
            ],
        },

    },
    {
        "site_name" : "tfhrc",
        "is_v2xhub" : False,
        "lvc" : "constructive",
        "tdcs_dir" : "/home/andrew/Downloads/test-4/CARLA-TFHRC-2_20230511150531-4a/exported_tdcs",
        "pcap_in_dir" : "/home/andrew/Downloads/test-4/CARLA-TFHRC-2_20230511150531-4a/pilot-1_test-4_tfhrc-1_ip_packet_in_decoded_packets",
        "pcap_out_dir" : "/home/andrew/Downloads/test-4/CARLA-TFHRC-2_20230511150531-4a/pilot-1_test-4_thfrc-1_ip_packet_out_decoded_packets",
        "start_time" : 1683832241.16251,
        "end_time" : 1683832294.14485,
        "adapter_addresses_by_type" : {
            # "J2735-BSM" : [
            #     "192.168.55.231:34505",      # test 4a
            #     # "192.168.55.231:42251"         # test 4b
            # ],
        },

    },
    # {
    #     "site_name" : "v2xhub",
    #     "is_v2xhub" : True,
    #     "lvc" : "constructive",
    #     "tdcs_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/v2x_exported_tdcs",
    #     "pcap_in_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/pilot1_test1-3_v2x_ip_packet_in_decoded_packets",
    #     "pcap_out_dir" : "/home/andrew/Downloads/230414_Pilot_1-20230512T163409Z-001/230414_Pilot_1/v2xhub_pilot1/pilot1_test1-3_v2x_ip_packet_out_decoded_packets",
    #     "start_time" : 1683832241.16251,
    #     "end_time" : 1683832294.14485,
    #     "adapter_addresses_by_type" : {
    #         "J2735-MAP" : ["192.168.55.244:41403"],
    #     },

    # },


]

test_list = {
    "pilot_1_test_1" : {
        "name"      : "pilot_1_test_1",
        "site_list" : test_1_site_list
    },
    "pilot_1_test_2" : {
        "name"      : "pilot_1_test_2",
        "site_list" : test_2_site_list
    },
    "pilot_1_test_3" : {
        "name"      : "pilot_1_test_3",
        "site_list" : test_3_site_list
    },
    "pilot_1_test_4a" : {
        "name"      : "pilot_1_test_4a",
        "site_list" : test_4a_site_list
    },
}

test_to_run = "pilot_1_test_4a"

test_name = test_list[test_to_run]["name"]
site_list = test_list[test_to_run]["site_list"]


data_types = {
    "J2735-SPAT": {
        "pcap_file_pattern" : "J2735-Payload",
        "sdo_file_pattern"   : ["TJ2735Msg"]
    },
    "J2735-BSM": {
        "pcap_file_pattern" : "J2735-Payload",
        "sdo_file_pattern"   : ["TJ2735Msg"]
    },
    "J2735-MAP": {
        "pcap_file_pattern" : "J2735-Payload",
        "sdo_file_pattern"   : ["TJ2735Msg"]
    },
    # "BSM": {
    #     "pcap_file_pattern" : "BSM",
    #     "sdo_file_pattern"   : "BSM"
    # },
    # "Mobility_Path": {
    #     "pcap_file_pattern" : "Mobility-Path",
    #     "sdo_file_pattern"   : "Mobility-Path"
    # },
    # "Mobility_Request": {
    #     "pcap_file_pattern" : "Mobility-Request",
    #     "sdo_file_pattern"   : "Platoon"
    # },
    # "Mobility_Response": {
    #     "pcap_file_pattern" : "Mobility-Response",
    #     "sdo_file_pattern"   : "Platoon"
    # },
    # "Mobility_Operations-INFO": {
    #     "pcap_file_pattern" : "Mobility-Operations",
    #     "sdo_file_pattern"   : "Platoon"
    # },
    # "Mobility_Operations-STATUS": {
    #     "pcap_file_pattern" : "Mobility-Operations",
    #     "sdo_file_pattern"   : "Platoon"
    # },
    # "Traffic_Control_Request": {
    #     "pcap_file_pattern" : "Traffic-Control-Request",
    #     "sdo_file_pattern"   : "TrafficControlRequest"
    # },
    # "Traffic_Control_Message": {
    #     "pcap_file_pattern" : "Traffic-Control-Message",
    #     "sdo_file_pattern"   : "TrafficControlMessage"
    # },
    # "MAP": {
    #     "pcap_file_pattern" : "MAP",
    #     "sdo_file_pattern"   : ["MAP"]
    # },
    # "TrafficLight": {
    #     "pcap_file_pattern" : "SPAT",
    #     "sdo_file_pattern"   : ["TJ2735Msg","TrafficLight"]
    # },
}

################################################## MAIN ##################################################
    
def find_file_at_path(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                # return os.path.join(root, name)
                result.append(os.path.join(root, name))
    
    if len(result) == 0:
        print("\nERROR: File not found: " + path + " - " + pattern)
        sys.exit()
    elif len(result) == 1:
        return result[0]
    else:
        print("\nMultiple files found in dir " + path + " for pattern " + pattern + ". Please select the desired file: [#]")
        for filename_i,filename in enumerate(result):
            print("\t[" + str(filename_i) + "] " +  filename)
        file_index_selection = input("--> ")
        return result[int(file_index_selection)]
            
    return result

def get_obj_by_key_value(obj_array,key,value):
    for index, element in enumerate(obj_array):
        if element[key] == value:
            return index

def find_data_files(exported_tcds_dir,decoded_pcap_in_dir,decoded_pcap_out_dir):

    data_file_locations = {}
    for data_type in data_types:
        data_file_locations[data_type] = {}
    
    
    if decoded_pcap_out_dir:
        print("\n  Locating pcap out files: ")
        for data_type in data_types:
            data_file_locations[data_type]["decoded_pcap_out_file"] = find_file_at_path("*" + data_types[data_type]["pcap_file_pattern"] + "*", decoded_pcap_out_dir)
            print("\t" + data_type + ": " + str(data_file_locations[data_type]["decoded_pcap_out_file"]))
    else:
        for data_type in data_types:
            data_file_locations[data_type]["decoded_pcap_out_file"] = None
        print("\n  No pcap out dir specified")
    
    if decoded_pcap_in_dir:
        print("\n  Locating pcap in files: ")
        for data_type in data_types:
            data_file_locations[data_type]["decoded_pcap_in_file"] = find_file_at_path("*" + data_types[data_type]["pcap_file_pattern"] + "*", decoded_pcap_in_dir)
            print("\t" + data_type + ": " + str(data_file_locations[data_type]["decoded_pcap_in_file"]))
    else:
        for data_type in data_types:
            data_file_locations[data_type]["decoded_pcap_in_file"] = None
        print("\n  No pcap in dir specified") 
        
    if exported_tcds_dir:
        print("\n  Locating exported tdcs files: ")
        for data_type in data_types:
            data_file_locations[data_type]["exported_tcds_file"] = []

            for sdo_type_pattern in data_types[data_type]["sdo_file_pattern"]:
                print(sdo_type_pattern)
                found_file = find_file_at_path("*" + sdo_type_pattern + "*", exported_tcds_dir)
                data_file_locations[data_type]["exported_tcds_file"].append(found_file)
                print("\t" + data_type + ": " + str(data_file_locations[data_type]["exported_tcds_file"]))
    else:
        for data_type in data_types:
            data_file_locations[data_type]["exported_tcds_file"] = None
        print("\n  No exported tdcs dir specified")
    
    return data_file_locations
        
def generate_import_files(source_data,v2xhub_data,dest_data,is_tcr_tcm):
    
    try:
        os.mkdir("generated_import_files")
    except:
        # print("\nDir generated_import_file already exists")
        pass
    
    this_import_folder_name = None
    
    for data_type in data_types:
        
        # do not generate import files for TCM because TCR import and analysis includes both TCR and TCM
        # we dont want to remove it from the data list because we still want to get the data files in find_data_files
        if data_type == "Traffic_Control_Message":
            continue
            
        if is_tcr_tcm:
            
            try:
                os.mkdir("generated_import_files/" + source_data["site_name"] + "_tcr_tcm")
            except:
                pass
                # print("Dir generated_import_files/" + source_data["site_name"] + "_tcr_tcm" + " already exists")
            
            this_import_folder_name = source_data["site_name"] + "_tcr_tcm"
            this_importfile_name = "generated_import_files/" + this_import_folder_name + "/" + source_data["site_name"] + "_tcr_tcm"
            this_importfile_name_obj = open(this_importfile_name + ".csv",'w',newline='')
            this_importfile_name_writer = csv.writer(this_importfile_name_obj,quoting=csv.QUOTE_ALL)
            
            if source_data["lvc"] == "live":
                this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type"])
                this_importfile_name_writer.writerow(["true",source_data["site_name"] + " J2735 TCR platform out pcap",all_data[source_data["site_name"]]["Traffic_Control_Request"]["decoded_pcap_out_file"],"pcap","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",source_data["site_name"] + " J2735 TCR in to " + v2xhub_data["site_name"] + " J2735 TCR in pcap via DSRC",all_data[v2xhub_data["site_name"]]["Traffic_Control_Request"]["decoded_pcap_in_file"],"pcap","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",v2xhub_data["site_name"] + " J2735 TCR in to " + v2xhub_data["site_name"] + " J2735 TCM out pcap",all_data[v2xhub_data["site_name"]]["Traffic_Control_Message"]["decoded_pcap_out_file"],"pcap","Traffic_Control_Message"])
                this_importfile_name_writer.writerow(["true",v2xhub_data["site_name"] + " J2735 TCM in to " +  source_data["site_name"] + " J2735 TCM in pcap via DSRC",all_data[source_data["site_name"]]["Traffic_Control_Message"]["decoded_pcap_in_file"],"pcap","Traffic_Control_Message"])
            else:
                this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type"])
                this_importfile_name_writer.writerow(["true",source_data["site_name"] + " J2735 TCR platform out pcap",all_data[source_data["site_name"]]["Traffic_Control_Request"]["decoded_pcap_out_file"],"pcap","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",source_data["site_name"] + " J2735 TCR out to " + source_data["site_name"] + " TCR SDO commit",all_data[source_data["site_name"]]["Traffic_Control_Request"]["exported_tcds_file"],"tdcs","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",source_data["site_name"] + " to " + v2xhub_data["site_name"] + " TCR SDO transmit",all_data[v2xhub_data["site_name"]]["Traffic_Control_Request"]["exported_tcds_file"],"tdcs","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",v2xhub_data["site_name"] + " TCR SDO receipt to " + v2xhub_data["site_name"] + " TCM SDO commit",all_data[v2xhub_data["site_name"]]["Traffic_Control_Message"]["exported_tcds_file"],"tdcs","Traffic_Control_Message"])
                this_importfile_name_writer.writerow(["true",v2xhub_data["site_name"] + " to " + source_data["site_name"] + " TCM SDO transmit",all_data[source_data["site_name"]]["Traffic_Control_Message"]["exported_tcds_file"],"tdcs","Traffic_Control_Message"])
                this_importfile_name_writer.writerow(["false",source_data["site_name"] + " J2735 TCM SDO in to " +  source_data["site_name"] + " J2735 TCM in",all_data[source_data["site_name"]]["Traffic_Control_Message"]["decoded_pcap_in_file"],"pcap","Traffic_Control_Message"])
        
        elif source_data["lvc"] == "live":
            
            try:
                os.mkdir("generated_import_files/" + source_data["site_name"] + "_to_" + dest_data["site_name"])
            except:
                pass
                # print("Dir generated_import_file/" + source_data["site_name"] + "_to_" + dest_data["site_name"] + " already exists")
            
            this_import_folder_name = source_data["site_name"] + "_to_" + dest_data["site_name"]
            this_importfile_name = "generated_import_files/" + this_import_folder_name + "/" + source_data["site_name"] + "_to_" + dest_data["site_name"] + "_" + data_type
            this_importfile_name_obj = open(this_importfile_name + ".csv",'w',newline='')
            this_importfile_name_writer = csv.writer(this_importfile_name_obj,quoting=csv.QUOTE_ALL)
            
            this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type"])
            this_importfile_name_writer.writerow(["true",source_data["site_name"] + " J2735 platform out pcap",all_data[source_data["site_name"]][data_type]["decoded_pcap_out_file"],"pcap",data_type])
            this_importfile_name_writer.writerow(["true",source_data["site_name"] + " to v2xhub DSRC in pcap",all_data[v2xhub_data["site_name"]][data_type]["decoded_pcap_in_file"],"pcap",data_type])
            this_importfile_name_writer.writerow(["true",v2xhub_data["site_name"] + " J2735 in to " + v2xhub_data["site_name"] + " SDO commit",all_data[v2xhub_data["site_name"]][data_type]["exported_tcds_file"],"tdcs",data_type])
            this_importfile_name_writer.writerow(["true",v2xhub_data["site_name"] + " SDO to " + dest_data["site_name"] +  " SDO transmit",all_data[dest_data["site_name"]][data_type]["exported_tcds_file"],"tdcs",data_type])
            this_importfile_name_writer.writerow(["true",dest_data["site_name"] + " SDO to " + dest_data["site_name"] + " J2735 in",all_data[dest_data["site_name"]][data_type]["decoded_pcap_in_file"],"pcap",data_type])
        
        elif dest_data["lvc"] == "live":
            
            try:
                os.mkdir("generated_import_files/" + source_data["site_name"] + "_to_" + dest_data["site_name"])
            except:
                pass
                # print("Dir generated_import_file/" + source_data["site_name"] + "_to_" + dest_data["site_name"] + " already exists")
            
            this_import_folder_name = source_data["site_name"] + "_to_" + dest_data["site_name"]
            this_importfile_name = "generated_import_files/" + this_import_folder_name + "/" + source_data["site_name"] + "_to_" + dest_data["site_name"] + "_" + data_type
            this_importfile_name_obj = open(this_importfile_name + ".csv",'w',newline='')
            this_importfile_name_writer = csv.writer(this_importfile_name_obj,quoting=csv.QUOTE_ALL)
            
            this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type",data_type])
            this_importfile_name_writer.writerow(["true",source_data["site_name"] + " J2735 platform out pcap",all_data[source_data["site_name"]][data_type]["decoded_pcap_out_file"],"pcap",data_type])
            this_importfile_name_writer.writerow(["true",source_data["site_name"] + " J2735 in to " + source_data["site_name"] + " SDO commit",all_data[source_data["site_name"]][data_type]["exported_tcds_file"],"tdcs",data_type])
            this_importfile_name_writer.writerow(["true",source_data["site_name"] + " SDO to " + v2xhub_data["site_name"] +  " SDO transmit",all_data[v2xhub_data["site_name"]][data_type]["exported_tcds_file"],"tdcs",data_type])
            
            if data_type == "BSM":
                print("J2735 messages not generated from constructive vehicles, skipping v2xhub out and live in data")
                continue
            else:
                this_importfile_name_writer.writerow(["true",v2xhub_data["site_name"] + " SDO to v2xhub J2735 out pcap",all_data[v2xhub_data["site_name"]][data_type]["decoded_pcap_out_file"],"pcap",data_type])
                this_importfile_name_writer.writerow(["true",v2xhub_data["site_name"] + " J2735 to " + dest_data["site_name"] + " J2735 DSRC in",all_data[dest_data["site_name"]][data_type]["decoded_pcap_in_file"],"pcap",data_type])
        
        elif v2xhub_data == None:
            
            if not data_type in source_data["adapter_addresses_by_type"]:
                continue
                
            try:
                os.mkdir("generated_import_files/" + source_data["site_name"] + "_to_" + dest_data["site_name"])
            except:
                pass
                # print("Dir generated_import_file/" + source_data["site_name"] + "_to_" + dest_data["site_name"] + " already exists")
            
            for adapter_ip in source_data["adapter_addresses_by_type"][data_type]:

                this_import_folder_name = source_data["site_name"] + "_to_" + dest_data["site_name"]
                this_importfile_name = "generated_import_files/" + this_import_folder_name + "/" + source_data["site_name"] + "_to_" + dest_data["site_name"] + "_" + data_type + "_" + str(adapter_ip.replace(".","-").replace(":","_"))
                this_importfile_name_obj = open(this_importfile_name + ".csv",'w',newline='')
                this_importfile_name_writer = csv.writer(this_importfile_name_obj,quoting=csv.QUOTE_ALL)

                print("  Generating import file: " + this_importfile_name)

                import_data_type = data_type
                
                this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type","adapter_ip","start_time","end_time"])
                
                # TODO - need a better way to organize data inputs to decide when to include pcap when a site has a data type that is in pcap and a data type that isnt
                # this particular logic is always true for pilot 1 but will not always be 
                
                print(str(all_data[source_data["site_name"]][data_type]["decoded_pcap_out_file"]) + " : " +  str(all_data[source_data["site_name"]][data_type]))
                if all_data[source_data["site_name"]][data_type]["decoded_pcap_out_file"] and data_type in ["J2735-SPAT","J2735-MAP","SPAT","TrafficLight"]:
                    
                    if data_type == "TrafficLight":
                        import_data_type = "TrafficLight"

                    this_importfile_name_writer.writerow(["true",source_data["site_name"] + " J2735 pcap out",all_data[source_data["site_name"]][data_type]["decoded_pcap_out_file"],"pcap",import_data_type,None,source_data["start_time"],source_data["end_time"]])
                
                for sdo_type_file_i,sdo_type_file in enumerate(all_data[source_data["site_name"]][data_type]["exported_tcds_file"]):
                    
                    if sdo_type_file_i == 0:
                        if data_type == "TrafficLight":
                            import_data_type = "J2735-SPAT"
                            import_adapter_ip = source_data["adapter_addresses_by_type"]["J2735-SPAT"][0]
                        else:
                            import_data_type = data_type
                            import_adapter_ip = adapter_ip
                        
                        this_importfile_name_writer.writerow(["true",source_data["site_name"] + " J2735 in to " + source_data["site_name"] + " SDO commit",sdo_type_file,"tdcs",import_data_type,import_adapter_ip,source_data["start_time"],source_data["end_time"]])
                    else:
                        this_importfile_name_writer.writerow(["true",source_data["site_name"] + " to " + source_data["site_name"] + " SDO convert",sdo_type_file,"tdcs",data_type,adapter_ip,source_data["start_time"],source_data["end_time"]])
                
                # if data_type in ["SPAT"]:
                #     this_importfile_name_writer.writerow(["true",sourceJ2735-Payload_data["site_name"] + " J2735 in to " + source_data["site_name"] + " SDO commit",all_data[source_data["site_name"]][data_type]["exported_tcds_file"],"tdcs",data_type,adapter_ip,source_data["start_time"],source_data["end_time"]])
                if data_type == "TrafficLight":
                    import_data_file = all_data[dest_data["site_name"]][data_type]["exported_tcds_file"][1]
                else:
                    import_data_file = all_data[dest_data["site_name"]][data_type]["exported_tcds_file"][0]

                this_importfile_name_writer.writerow(["true",source_data["site_name"] + " SDO to " + dest_data["site_name"] +  " SDO transmit",import_data_file,"tdcs",data_type,None,source_data["start_time"],source_data["end_time"]])
                
                if data_type != "TrafficLight":
                    this_importfile_name_writer.writerow(["true",dest_data["site_name"] + " J2735 to " + dest_data["site_name"] + " J2735 pcap in",all_data[dest_data["site_name"]][data_type]["decoded_pcap_in_file"],"pcap",data_type,None,source_data["start_time"],source_data["end_time"]])
        else:
            print("Invalid vehicle configuration. Must be: live to constructive vehicle, constructive to live vehicle, or constructive to constructive vehicle")
            sys.exit()
    
    return this_import_folder_name
        


################################################## MAIN ##################################################

print("\n########## FINDING ALL DATA FILES ##########")


all_data = {}

for test_site in site_list:
    print("\nFinding data files for " + test_site["site_name"])
    all_data[test_site["site_name"]] = find_data_files(test_site["tdcs_dir"],test_site["pcap_in_dir"],test_site["pcap_out_dir"])




print("\n########## GENERATING IMPORT FILES ##########")

import_file_directory_list = []


for src_test_site in site_list:
    
    for dest_test_site in site_list:
        if src_test_site != dest_test_site:

            print("\nGenerating for: " + str(src_test_site["site_name"]) + " to " + str(dest_test_site["site_name"]))

            v2xhub_site = None

            if src_test_site["lvc"] == "live" or dest_test_site["lvc"] == "live":
                
                v2xhub_site = site_list[get_obj_by_key_value(site_list,"is_v2xhub",True)]

            import_file = generate_import_files(src_test_site,v2xhub_site,dest_test_site,False)
            if import_file:
                import_file_directory_list.append(import_file)


print("\n########## RUNNING DATA ANALYSIS ##########")

vehicle_name_to_index = {
    "live" : 1,
    "eco" : 4,
    "nissan" : 5,
    "virt" : 99,
}

try:
    os.mkdir("results")
except:
    pass

results_summary_outfile_obj = open("results/" + test_name + "_results_summary.csv",'w',newline='')
results_summary_outfile_writer = csv.writer(results_summary_outfile_obj)
results_summary_outfile_writer.writerow(["j2735_type","source","source_type","destination","destination_type","step_type","min","max","mean","jitter","std_dev"])
results_summary_outfile_obj.close()

for loader_dir in import_file_directory_list:

    print("\nCurrent analysis direction: " + loader_dir)
    
    for data_type in data_types:
        
        # do not generate import files for TCM because TCR import and analysis includes both TCR and TCM
        # we dont want to remove it from the data list because we still want to get the data files in find_data_files
        if data_type == "Traffic_Control_Message":
            continue
        
        # if the loader dir is tcr_tcm, we are only looking to calculate TCR
        if "tcr_tcm" in loader_dir and data_type != "Traffic_Control_Request":
            continue
        
        if data_type == "Traffic_Control_Request":
            if "tcr_tcm" in loader_dir:
                loader_file_name_start = loader_dir
            else:
                # we only want to run analysis on TCR and TCM in specific tcr_tcm loaders 
                continue
        else:
            loader_file_name_start = loader_dir + "_" + data_type
            
            
        current_dir = os.getcwd()
        abs_loader_dir = os.path.join(current_dir, "generated_import_files",loader_dir)

        matching_loader_files = []

        # Iterate over all files and directories in the given directory
        for root, dirs, files in os.walk(abs_loader_dir):
            # Check if the file matches the datatype file name
            for filename in fnmatch.filter(files, loader_file_name_start + "*"):
                # Append the absolute file path to the list of matching files
                loader_file_to_run_abs = os.path.join(root, filename)

                analysis_command =  "python3 calculate_e2e_perf.py -i " + loader_file_to_run_abs + " -t " + data_type + " -o " + filename + "_performance_results.csv -r " + test_name
                print("\nExecuting analysis: " + analysis_command)
                os.system(analysis_command)
                
            
        
                    
                    
            
                    
                
                
                
