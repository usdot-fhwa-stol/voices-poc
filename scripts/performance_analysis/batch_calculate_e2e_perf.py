import sys
import os
import fnmatch
import json
import csv
import re









############################## DATA LOCATION PARAMETERS ##############################

##### EXP 3 RUN 5 #####
# # LIVE

# live_exported_tcds_dir = None
# live_decoded_pcap_in_dir = "/home/andrew/demo_1b_data/run_5/live/decoded_pcaps_in"
# live_decoded_pcap_out_dir = "/home/andrew/demo_1b_data/run_5/live/decoded_pcaps_out"

# # AUG

# aug_exported_tcds_dir = "/home/andrew/demo_1b_data/run_5/aug/exported_tdcs"
# aug_decoded_pcap_in_dir = "/home/andrew/demo_1b_data/run_5/aug/decoded_pcaps_in"
# aug_decoded_pcap_out_dir = "/home/andrew/demo_1b_data/run_5/aug/decoded_pcaps_out"

# # MITRE

# mitre_exported_tcds_dir = "/home/andrew/demo_1b_data/run_5/mitre/exported_tdcs"
# mitre_decoded_pcap_in_dir = "/home/andrew/demo_1b_data/run_5/mitre/decoded_pcaps_in"
# mitre_decoded_pcap_out_dir = "/home/andrew/demo_1b_data/run_5/mitre/decoded_pcaps_out"

# # V2X Hub

# v2xhub_exported_tcds_dir = "/home/andrew/demo_1b_data/run_5/v2xhub/exported_tdcs"
# v2xhub_decoded_pcap_in_dir = "/home/andrew/demo_1b_data/run_5/v2xhub/decoded_pcaps_in"
# v2xhub_decoded_pcap_out_dir = "/home/andrew/demo_1b_data/run_5/v2xhub/decoded_pcaps_out"

##### EXP 3 RUN 4 #####
# # LIVE

# live_exported_tcds_dir = None
# live_decoded_pcap_in_dir = "/home/andrew/demo_1b_data/run_4/live/decoded_pcaps_in"
# live_decoded_pcap_out_dir = "/home/andrew/demo_1b_data/run_4/live/decoded_pcaps_out"

# # AUG

# aug_exported_tcds_dir = "/home/andrew/demo_1b_data/run_4/aug/exported_tdcs"
# aug_decoded_pcap_in_dir = "/home/andrew/demo_1b_data/run_4/aug/decoded_pcaps_in"
# aug_decoded_pcap_out_dir = "/home/andrew/demo_1b_data/run_4/aug/decoded_pcaps_out"

# # MITRE

# mitre_exported_tcds_dir = "/home/andrew/demo_1b_data/run_4/mitre/exported_tdcs"
# mitre_decoded_pcap_in_dir = "/home/andrew/demo_1b_data/run_4/mitre/decoded_pcaps_in"
# mitre_decoded_pcap_out_dir = "/home/andrew/demo_1b_data/run_4/mitre/decoded_pcaps_out"

# # V2X Hub

# v2xhub_exported_tcds_dir = "/home/andrew/demo_1b_data/run_4/v2xhub/exported_tdcs"
# v2xhub_decoded_pcap_in_dir = "/home/andrew/demo_1b_data/run_4/v2xhub/decoded_pcaps_in"
# v2xhub_decoded_pcap_out_dir = "/home/andrew/demo_1b_data/run_4/v2xhub/decoded_pcaps_out"

# ##### EXP 2 RUN 2 #####
# # LIVE

# live_exported_tcds_dir = None
# live_decoded_pcap_in_dir = "/home/andrew/demo_1a_data/run_2/live/decoded_pcaps_in"
# live_decoded_pcap_out_dir = "/home/andrew/demo_1a_data/run_2/live/decoded_pcaps_out"

# # AUG

# aug_exported_tcds_dir = "/home/andrew/demo_1a_data/run_2/aug/exported_tdcs"
# aug_decoded_pcap_in_dir = "/home/andrew/demo_1a_data/run_2/aug/decoded_pcaps_in"
# aug_decoded_pcap_out_dir = "/home/andrew/demo_1a_data/run_2/aug/decoded_pcaps_out"

# # MITRE

# mitre_exported_tcds_dir = "/home/andrew/demo_1a_data/run_2/mitre/exported_tdcs"
# mitre_decoded_pcap_in_dir = "/home/andrew/demo_1a_data/run_2/mitre/decoded_pcaps_in"
# mitre_decoded_pcap_out_dir = "/home/andrew/demo_1a_data/run_2/mitre/decoded_pcaps_out"

# # V2X Hub

# v2xhub_exported_tcds_dir = "/home/andrew/demo_1a_data/run_2/v2xhub/exported_tdcs"
# v2xhub_decoded_pcap_in_dir = "/home/andrew/demo_1a_data/run_2/v2xhub/decoded_pcaps_in"
# v2xhub_decoded_pcap_out_dir = "/home/andrew/demo_1a_data/run_2/v2xhub/decoded_pcaps_out"

##### EXP 2 RUN 3 #####
# LIVE

live_exported_tcds_dir = None
live_decoded_pcap_in_dir = "/home/andrew/demo_1a_data/run_3/live/decoded_pcaps_in"
live_decoded_pcap_out_dir = "/home/andrew/demo_1a_data/run_3/live/decoded_pcaps_out"

# AUG

aug_exported_tcds_dir = "/home/andrew/demo_1a_data/run_3/aug/exported_tdcs"
aug_decoded_pcap_in_dir = "/home/andrew/demo_1a_data/run_3/aug/decoded_pcaps_in"
aug_decoded_pcap_out_dir = "/home/andrew/demo_1a_data/run_3/aug/decoded_pcaps_out"

# MITRE

mitre_exported_tcds_dir = "/home/andrew/demo_1a_data/run_3/mitre/exported_tdcs"
mitre_decoded_pcap_in_dir = "/home/andrew/demo_1a_data/run_3/mitre/decoded_pcaps_in"
mitre_decoded_pcap_out_dir = "/home/andrew/demo_1a_data/run_3/mitre/decoded_pcaps_out"

# V2X Hub

v2xhub_exported_tcds_dir = "/home/andrew/demo_1a_data/run_3/v2xhub/exported_tdcs"
v2xhub_decoded_pcap_in_dir = "/home/andrew/demo_1a_data/run_3/v2xhub/decoded_pcaps_in"
v2xhub_decoded_pcap_out_dir = "/home/andrew/demo_1a_data/run_3/v2xhub/decoded_pcaps_out"


data_types = {
    "BSM": {
        "pcap_file_pattern" : "BSM",
        "sdo_file_pattern"   : "BSM"
    },
    "Mobility_Path": {
        "pcap_file_pattern" : "Mobility-Path",
        "sdo_file_pattern"   : "Mobility-Path"
    },
    "Mobility_Request": {
        "pcap_file_pattern" : "Mobility-Request",
        "sdo_file_pattern"   : "Platoon"
    },
    "Mobility_Response": {
        "pcap_file_pattern" : "Mobility-Response",
        "sdo_file_pattern"   : "Platoon"
    },
    "Mobility_Operations-INFO": {
        "pcap_file_pattern" : "Mobility-Operations",
        "sdo_file_pattern"   : "Platoon"
    },
    "Mobility_Operations-STATUS": {
        "pcap_file_pattern" : "Mobility-Operations",
        "sdo_file_pattern"   : "Platoon"
    },
    "Traffic_Control_Request": {
        "pcap_file_pattern" : "Traffic-Control-Request",
        "sdo_file_pattern"   : "TrafficControlRequest"
    },
    "Traffic_Control_Message": {
        "pcap_file_pattern" : "Traffic-Control-Message",
        "sdo_file_pattern"   : "TrafficControlMessage"
    },
    # "MAP": {
    #     "pcap_file_pattern" : "MAP",
    #     "sdo_file_pattern"   : "MAP"
    # },
    # "SPAT": {
    #     "pcap_file_pattern" : "SPAT",
    #     "sdo_file_pattern"   : "TrafficLight"
    # },
}




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



def find_data_files(exported_tcds_dir,decoded_pcap_in_dir,decoded_pcap_out_dir):

    data_file_locations = {}
    for data_type in data_types:
        data_file_locations[data_type] = {}
    
    
    if decoded_pcap_out_dir:
        print("\nLocating pcap out files: ")
        for data_type in data_types:
            data_file_locations[data_type]["decoded_pcap_out_file"] = find_file_at_path("*" + data_types[data_type]["pcap_file_pattern"] + "*", decoded_pcap_out_dir)
            print("\t" + data_type + ": " + str(data_file_locations[data_type]["decoded_pcap_out_file"]))
    else:
        print("\nNo pcap out dir specified") 
    
    if decoded_pcap_in_dir:
        print("\nLocating pcap in files: ")
        for data_type in data_types:
            data_file_locations[data_type]["decoded_pcap_in_file"] = find_file_at_path("*" + data_types[data_type]["pcap_file_pattern"] + "*", decoded_pcap_in_dir)
            print("\t" + data_type + ": " + str(data_file_locations[data_type]["decoded_pcap_in_file"]))
    else:
        print("\nNo pcap in dir specified") 
        
    if exported_tcds_dir:
        print("\nLocating exported tdcs files: ")
        for data_type in data_types:
            data_file_locations[data_type]["exported_tcds_file"] = find_file_at_path("*" + data_types[data_type]["sdo_file_pattern"] + "*", exported_tcds_dir)
            print("\t" + data_type + ": " + str(data_file_locations[data_type]["exported_tcds_file"]))
    else:
        print("\nNo exported tdcs dir specified")
    
    return data_file_locations
        
def generate_import_files(source_data_name,v2xhub_data_name,dest_data_name,is_tcr_tcm):
    
    try:
        os.mkdir("generated_import_files")
    except:
        # print("\nDir generated_import_file already exists")
        pass
    
    
    for data_type in data_types:
        
        # do not generate import files for TCM because TCR import and analysis includes both TCR and TCM
        # we dont want to remove it from the data list because we still want to get the data files in find_data_files
        if data_type == "Traffic_Control_Message":
            continue
            
        if is_tcr_tcm:
            
            try:
                os.mkdir("generated_import_files/" + source_data_name + "_tcr_tcm")
            except:
                pass
                # print("Dir generated_import_files/" + source_data_name + "_tcr_tcm" + " already exists")
            
            this_import_folder_name = source_data_name + "_tcr_tcm"
            this_importfile_name = "generated_import_files/" + this_import_folder_name + "/" + source_data_name + "_tcr_tcm"
            this_importfile_name_obj = open(this_importfile_name + ".csv",'w',newline='')
            this_importfile_name_writer = csv.writer(this_importfile_name_obj,quoting=csv.QUOTE_ALL)
            
            if source_data_name == "live":
                this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type"])
                this_importfile_name_writer.writerow(["true",source_data_name + " J2735 TCR platform out pcap",all_data[source_data_name]["Traffic_Control_Request"]["decoded_pcap_out_file"],"pcap","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",source_data_name + " J2735 TCR in to " + v2xhub_data_name + " J2735 TCR in pcap via DSRC",all_data[v2xhub_data_name]["Traffic_Control_Request"]["decoded_pcap_in_file"],"pcap","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",v2xhub_data_name + " J2735 TCR in to " + v2xhub_data_name + " J2735 TCM out pcap",all_data[v2xhub_data_name]["Traffic_Control_Message"]["decoded_pcap_out_file"],"pcap","Traffic_Control_Message"])
                this_importfile_name_writer.writerow(["true",v2xhub_data_name + " J2735 TCM in to " +  source_data_name + " J2735 TCM in pcap via DSRC",all_data[source_data_name]["Traffic_Control_Message"]["decoded_pcap_in_file"],"pcap","Traffic_Control_Message"])
            else:
                this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type"])
                this_importfile_name_writer.writerow(["true",source_data_name + " J2735 TCR platform out pcap",all_data[source_data_name]["Traffic_Control_Request"]["decoded_pcap_out_file"],"pcap","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",source_data_name + " J2735 TCR out to " + source_data_name + " TCR SDO commit",all_data[source_data_name]["Traffic_Control_Request"]["exported_tcds_file"],"tdcs","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",source_data_name + " to " + v2xhub_data_name + " TCR SDO transmit",all_data[v2xhub_data_name]["Traffic_Control_Request"]["exported_tcds_file"],"tdcs","Traffic_Control_Request"])
                this_importfile_name_writer.writerow(["true",v2xhub_data_name + " TCR SDO receipt to " + v2xhub_data_name + " TCM SDO commit",all_data[v2xhub_data_name]["Traffic_Control_Message"]["exported_tcds_file"],"tdcs","Traffic_Control_Message"])
                this_importfile_name_writer.writerow(["true",v2xhub_data_name + " to " + source_data_name + " TCM SDO transmit",all_data[source_data_name]["Traffic_Control_Message"]["exported_tcds_file"],"tdcs","Traffic_Control_Message"])
                this_importfile_name_writer.writerow(["false",source_data_name + " J2735 TCM SDO in to " +  source_data_name + " J2735 TCM in",all_data[source_data_name]["Traffic_Control_Message"]["decoded_pcap_in_file"],"pcap","Traffic_Control_Message"])
        
        elif source_data_name == "live":
            
            try:
                os.mkdir("generated_import_files/" + source_data_name + "_to_" + dest_data_name)
            except:
                pass
                # print("Dir generated_import_file/" + source_data_name + "_to_" + dest_data_name + " already exists")
            
            this_import_folder_name = source_data_name + "_to_" + dest_data_name
            this_importfile_name = "generated_import_files/" + this_import_folder_name + "/" + source_data_name + "_to_" + dest_data_name + "_" + data_type
            this_importfile_name_obj = open(this_importfile_name + ".csv",'w',newline='')
            this_importfile_name_writer = csv.writer(this_importfile_name_obj,quoting=csv.QUOTE_ALL)
            
            this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type"])
            this_importfile_name_writer.writerow(["true",source_data_name + " J2735 platform out pcap",all_data[source_data_name][data_type]["decoded_pcap_out_file"],"pcap",data_type])
            this_importfile_name_writer.writerow(["true",source_data_name + " to v2xhub DSRC in pcap",all_data[v2xhub_data_name][data_type]["decoded_pcap_in_file"],"pcap",data_type])
            this_importfile_name_writer.writerow(["true",v2xhub_data_name + " J2735 in to " + v2xhub_data_name + " SDO commit",all_data[v2xhub_data_name][data_type]["exported_tcds_file"],"tdcs",data_type])
            this_importfile_name_writer.writerow(["true",v2xhub_data_name + " SDO to " + dest_data_name +  " SDO transmit",all_data[dest_data_name][data_type]["exported_tcds_file"],"tdcs",data_type])
            this_importfile_name_writer.writerow(["true",dest_data_name + " SDO to " + dest_data_name + " J2735 in",all_data[dest_data_name][data_type]["decoded_pcap_in_file"],"pcap",data_type])
        
        elif dest_data_name == "live":
            
            try:
                os.mkdir("generated_import_files/" + source_data_name + "_to_" + dest_data_name)
            except:
                pass
                # print("Dir generated_import_file/" + source_data_name + "_to_" + dest_data_name + " already exists")
            
            this_import_folder_name = source_data_name + "_to_" + dest_data_name
            this_importfile_name = "generated_import_files/" + this_import_folder_name + "/" + source_data_name + "_to_" + dest_data_name + "_" + data_type
            this_importfile_name_obj = open(this_importfile_name + ".csv",'w',newline='')
            this_importfile_name_writer = csv.writer(this_importfile_name_obj,quoting=csv.QUOTE_ALL)
            
            this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type",data_type])
            this_importfile_name_writer.writerow(["true",source_data_name + " J2735 platform out pcap",all_data[source_data_name][data_type]["decoded_pcap_out_file"],"pcap",data_type])
            this_importfile_name_writer.writerow(["true",source_data_name + " J2735 in to " + source_data_name + " SDO commit",all_data[source_data_name][data_type]["exported_tcds_file"],"tdcs",data_type])
            this_importfile_name_writer.writerow(["true",source_data_name + " SDO to " + v2xhub_data_name +  " SDO transmit",all_data[v2xhub_data_name][data_type]["exported_tcds_file"],"tdcs",data_type])
            
            if data_type == "BSM":
                print("J2735 messages not generated from constructive vehicles, skipping v2xhub out and live in data")
                continue
            else:
                this_importfile_name_writer.writerow(["true",v2xhub_data_name + " SDO to v2xhub J2735 out pcap",all_data[v2xhub_data_name][data_type]["decoded_pcap_out_file"],"pcap",data_type])
                this_importfile_name_writer.writerow(["true",v2xhub_data_name + " J2735 to " + dest_data_name + " J2735 DSRC in",all_data[dest_data_name][data_type]["decoded_pcap_in_file"],"pcap",data_type])
        
        elif v2xhub_data_name == None:
            
            try:
                os.mkdir("generated_import_files/" + source_data_name + "_to_" + dest_data_name)
            except:
                pass
                # print("Dir generated_import_file/" + source_data_name + "_to_" + dest_data_name + " already exists")
            
            this_import_folder_name = source_data_name + "_to_" + dest_data_name
            this_importfile_name = "generated_import_files/" + this_import_folder_name + "/" + source_data_name + "_to_" + dest_data_name + "_" + data_type
            this_importfile_name_obj = open(this_importfile_name + ".csv",'w',newline='')
            this_importfile_name_writer = csv.writer(this_importfile_name_obj,quoting=csv.QUOTE_ALL)
            
            this_importfile_name_writer.writerow(["load_data","dataset_name","dataset_file_location","dataset_type","message_type"])
            this_importfile_name_writer.writerow(["true",source_data_name + " J2735 platform out pcap",all_data[source_data_name][data_type]["decoded_pcap_out_file"],"pcap",data_type])
            this_importfile_name_writer.writerow(["true",source_data_name + " J2735 in to " + source_data_name + " SDO commit",all_data[source_data_name][data_type]["exported_tcds_file"],"tdcs",data_type])
            this_importfile_name_writer.writerow(["true",source_data_name + " SDO to " + dest_data_name +  " SDO transmit",all_data[dest_data_name][data_type]["exported_tcds_file"],"tdcs",data_type])
            this_importfile_name_writer.writerow(["true",dest_data_name + " J2735 to " + dest_data_name + " J2735 in",all_data[dest_data_name][data_type]["decoded_pcap_in_file"],"pcap",data_type])
        else:
            print("Invalid vehicle configuration. Must be: live to constructive vehicle, constructive to live vehicle, or constructive to constructive vehicle")
            sys.exit()
            
    return this_import_folder_name
        

print("\n########## FINDING ALL DATA FILES ##########")


all_data = {}

print("\nFinding data files for Live")
all_data["live"] = find_data_files(live_exported_tcds_dir,live_decoded_pcap_in_dir,live_decoded_pcap_out_dir)

print("\nFinding data files for Augusta")
all_data["aug"] = find_data_files(aug_exported_tcds_dir,aug_decoded_pcap_in_dir,aug_decoded_pcap_out_dir)

print("\nFinding data files for MITRE")
all_data["mitre"] = find_data_files(mitre_exported_tcds_dir,mitre_decoded_pcap_in_dir,mitre_decoded_pcap_out_dir)

print("\nFinding data files for V2X-Hub")
all_data["v2xhub"] = find_data_files(v2xhub_exported_tcds_dir,v2xhub_decoded_pcap_in_dir,v2xhub_decoded_pcap_out_dir)



# print("\nlive Files: " + str(live_data_files))

# print("\naug Files: " + str(aug_data_files))

# print("\nmitre Files: " + str(mitre_data_files))

# print("\nv2xhub Files: " + str(v2xhub_data_files))

print("\n########## GENERATING IMPORT FILES ##########")

import_file_directory_list = []

import_file_directory_list.append(generate_import_files("live","v2xhub","aug",False))
import_file_directory_list.append(generate_import_files("live","v2xhub","mitre",False))

import_file_directory_list.append(generate_import_files("aug","v2xhub","live",False))
import_file_directory_list.append(generate_import_files("mitre","v2xhub","live",False))

import_file_directory_list.append(generate_import_files("aug",None,"mitre",False))
import_file_directory_list.append(generate_import_files("mitre",None,"aug",False))

import_file_directory_list.append(generate_import_files("live","v2xhub",None,True))
import_file_directory_list.append(generate_import_files("aug","v2xhub",None,True))


print("\n########## RUNNING DATA ANALYSIS ##########")

vehicle_name_to_index = {
    "live" : 1,
    "aug" : 4,
    "mitre" : 5,
    "virt" : 99,
}

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
                loader_file_name = loader_dir
            else:
                # we only want to run analysis on TCR and TCM in specific tcr_tcm loaders 
                continue
        else:
            loader_file_name = loader_dir + "_" + data_type
            
            
        current_dir = os.getcwd()
        loader_file_abs = os.path.join(current_dir, "generated_import_files",loader_dir,loader_file_name + ".csv")
        # print("  Current loader file abs: " + loader_file_abs)

        source_vehicle_search = re.search('^(.*?)_',loader_dir)
                
        if not source_vehicle_search:
            print("ERROR: Could not identify source vehicle from file name: " + loader_dir)
            sys.exit()
            
        source_vehicle_search_result = str(vehicle_name_to_index[source_vehicle_search.group(1)])
        # print("    Found source vehicle: " + source_vehicle_search_result)
        
        analysis_command =  "python3 calculate_e2e_perf.py -i " + loader_file_abs + " -t " + data_type + " -s " + source_vehicle_search_result + " -o " + loader_file_name + "_performance_results.csv"
        print("\nExecuting analysis: " + analysis_command)
        os.system(analysis_command)
        
                    
                    
            
                    
                
                
                
