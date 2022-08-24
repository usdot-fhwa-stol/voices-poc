# import json
import sys
import csv
# import numpy
import datetime


########## LOAD IN SOURCE VEHICLE DATA ##########
source_out_pcap_file = "source_vehicle_data/lead_carma_platform_out_decoded_packets_BSM.csv"

source_vehicle_out_data_infile_obj = open(source_out_pcap_file,'r')
source_vehicle_out_data_infile_reader = csv.DictReader(source_vehicle_out_data_infile_obj,delimiter=',')
source_vehicle_out_data_infile_headers = source_vehicle_out_data_infile_reader.fieldnames
print("\nsource_vehicle_data_infile_headers: " + str(source_vehicle_out_data_infile_headers))

source_vehicle_out_data_infile_reader_list = list(source_vehicle_out_data_infile_reader)
total_source_vehicle_out_packets = len(source_vehicle_out_data_infile_reader_list)

print("Total Packets: " + str(total_source_vehicle_out_packets))

########## LOAD IN V2X HUB DATA ##########

v2xhub_in_pcap_file = "v2xhub_data/v2xhub_in_decoded_packets_BSM.csv"

v2xhub_pcap_in_data_infile_obj = open(v2xhub_in_pcap_file,'r')
v2xhub_pcap_in_data_infile_reader = csv.DictReader(v2xhub_pcap_in_data_infile_obj,delimiter=',')
v2xhub_pcap_in_data_infile_headers = v2xhub_pcap_in_data_infile_reader.fieldnames
print("\nv2xhub_data_infile_headers: " + str(v2xhub_pcap_in_data_infile_headers))

v2xhub_pcap_in_data_infile_reader_list = list(v2xhub_pcap_in_data_infile_reader)
total_v2xhub_in_packets = len(v2xhub_pcap_in_data_infile_reader_list)

print("Total Packets: " + str(total_v2xhub_in_packets))

########## LOAD IN V2X HUB TDCS DATA ##########

v2xhub_in_tdcs_file = "v2xhub_data/VUG-Track-BSM-20220822124130.csv"

v2xhub_tdcs_data_infile_obj = open(v2xhub_in_tdcs_file,'r')
v2xhub_tdcs_data_infile_reader = csv.DictReader(v2xhub_tdcs_data_infile_obj,delimiter=',')
v2xhub_tdcs_data_infile_headers = v2xhub_tdcs_data_infile_reader.fieldnames
print("\nv2xhub_tdcs_data_infile_headers: " + str(v2xhub_tdcs_data_infile_headers))

v2xhub_tdcs_data_infile_reader_list = list(v2xhub_tdcs_data_infile_reader)
total_v2xhub_tdcs_packets = len(v2xhub_tdcs_data_infile_reader_list)

print("Total Packets: " + str(total_v2xhub_tdcs_packets))

########## INITIALIZE CSV WRITER ##########

outfile = "performance_analysis.csv"
results_outfile_obj = open(outfile,'w',newline='')
results_outfile_writer = csv.writer(results_outfile_obj)

# write headers
results_outfile_writer.writerow(["sv_packet_index","v2x_packet_index","sv_broadcast_latency","sv_to_v2x_latency"])


########## INITIALIZE VARIABLES FOR LOOPS ##########

sv_out_to_v2x_in_offset = None
sv_starting_row = None
v2x_starting_row = None

desired_bsm_id = "f03ad610"

desired_tena_identifier = "CARMA-TFHRC-LIVE"


########## SET CLOCK SKEWS ##########

virtual_to_nist_clock_skew = -51.729
live_to_nist_clock_skew = 60.723

v2x_to_virtual_clock_skew = 43.712
v2x_to_second_clock_skew = -213.336
v2x_to_third_clock_skew = -0.990


sv_to_v2x_clock_skew = live_to_nist_clock_skew - (virtual_to_nist_clock_skew + v2x_to_virtual_clock_skew)
print("\nsv_to_v2x_clock_skew: " + str(sv_to_v2x_clock_skew))

########## LOOP THROUGH SOURCE DATA ##########

for sv_out_i,sv_out_packet in enumerate(source_vehicle_out_data_infile_reader_list):

    # we are only interested in a specific BSM ID
    if sv_out_packet["bsm id"] != desired_bsm_id:
        # print("Skipping non matching BSM ID: " + sv_out_packet["bsm id"] + " != " + desired_bsm_id)
        continue

    #we dont care about anything before we start moving
    if sv_out_packet["speed(m/s)"] == str(0.0):
        # print("Skipping 0 speed: " + sv_out_packet["speed(m/s)"])
        continue

    # record the row where the speed begins to be non 0 on the source data
    if sv_starting_row == None:
        sv_starting_row = sv_out_i
        print("sv_starting_row: " + str(sv_starting_row))


    secMark = float(sv_out_packet["secMark"])
    packet_timestamp = datetime.datetime.fromtimestamp(int(float(sv_out_packet["packetTimestamp"])))
    roundDownMinTime = datetime.datetime(packet_timestamp.year,packet_timestamp.month,packet_timestamp.day,packet_timestamp.hour,packet_timestamp.minute).timestamp()
    packetSecondsAfterMin = (float(sv_out_packet["packetTimestamp"]) - roundDownMinTime)
    bsm_broadcast_latency = packetSecondsAfterMin*1000 - secMark

    if (bsm_broadcast_latency < 0) :
        # print("[!!!] Minute mismatch")
        bsm_broadcast_latency = bsm_broadcast_latency + 60000

    if sv_out_to_v2x_in_offset == None:
        
        
        for v2x_in_i,v2x_in_packet in enumerate(v2xhub_pcap_in_data_infile_reader_list):
            # we are only interested in a specific BSM ID
            if v2x_in_packet["bsm id"] != desired_bsm_id:
                # print("Skipping non matching BSM ID: " + sv_out_packet["bsm id"] + " != " + desired_bsm_id)
                continue

            #we dont care about anything before we start moving
            if v2x_in_packet["speed(m/s)"] == str(0.0):
                # print("Skipping 0 speed: " + sv_out_packet["speed(m/s)"])
                continue

            if v2x_starting_row == None:
                v2x_starting_row = v2x_in_i
                print("v2x_starting_row: " + str(v2x_starting_row))
            
            # print("Looking at data: " + sv_out_packet["latitude"] + " == " + v2x_in_packet["latitude"])
            if  (    
                    sv_out_packet["latitude"] == v2x_in_packet["latitude"] and
                    sv_out_packet["longitude"] == v2x_in_packet["longitude"] and
                    sv_out_packet["heading"] == v2x_in_packet["heading"]
            ):

                sv_out_to_v2x_in_offset = v2x_in_i - sv_out_i

                print("\nFound matching data: ")
                print("  - " + sv_out_packet["latitude"] + " == " + v2x_in_packet["latitude"])
                print("  - " + sv_out_packet["longitude"] + " == " + v2x_in_packet["longitude"])
                print("  - " + sv_out_packet["heading"] + " == " + v2x_in_packet["heading"])

                print("\nsv_out_to_v2x_in_offset = " + str(sv_out_to_v2x_in_offset))

                for v2x_tdcs_i,v2x_tdcs_packet in enumerate(v2xhub_tdcs_data_infile_reader_list):
                    
                    # we dont care about packet discoveries
                    if v2x_tdcs_packet["Metadata,Enum,Middleware::EventType"] == "Discovery":
                        print("Skipping packet discovery")
                        continue

                    # we are only interested in a specific BSM ID
                    print("v2x_tdcs_packet_speed: " + str(v2x_tdcs_packet["tspi.velocity.ltpENU_asTransmitted.vxInMetersPerSecond,Float32 (optional)"]))
                    v2x_tdcs_packet_speed = round(float(v2x_tdcs_packet["tspi.velocity.ltpENU_asTransmitted.vxInMetersPerSecond,Float32 (optional)"]),2)
                    print("v2x_tdcs_packet_speed: " + str(v2x_tdcs_packet_speed))

                    # if sv_out_packet["bsm id"] != desired_bsm_id:
                    #     # print("Skipping non matching BSM ID: " + sv_out_packet["bsm id"] + " != " + desired_bsm_id)
                    #     continue

                    # we dont care about anything before we start moving
                    if v2x_tdcs_packet_speed == 0.0:
                        print("Skipping 0 speed: " + str(v2x_tdcs_packet_speed))
                        continue

                    # if v2x_starting_row == None:
                    #     v2x_starting_row = v2x_in_i
                    #     print("v2x_starting_row: " + str(v2x_starting_row))
                    
                    # print("Looking at data: " + sv_out_packet["latitude"] + " == " + v2x_in_packet["latitude"])
                    # if  (    
                    #         sv_out_packet["latitude"] == v2x_in_packet["latitude"] and
                    #         sv_out_packet["longitude"] == v2x_in_packet["longitude"] and
                    #         sv_out_packet["heading"] == v2x_in_packet["heading"]
                    # ):

                    #     sv_out_to_v2x_in_offset = v2x_in_i - sv_out_i
                        
                    #     print("\nFound matching data: ")
                    #     print("  - " + sv_out_packet["latitude"] + " == " + v2x_in_packet["latitude"])
                    #     print("  - " + sv_out_packet["longitude"] + " == " + v2x_in_packet["longitude"])
                    #     print("  - " + sv_out_packet["heading"] + " == " + v2x_in_packet["heading"])

                    #     print("\nsv_out_to_v2x_in_offset = " + str(sv_out_to_v2x_in_offset))
                    #     break    


    if(
            sv_out_packet["latitude"] == v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["latitude"] and 
            sv_out_packet["longitude"] == v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["longitude"] and 
            sv_out_packet["heading"] == v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["heading"] and
            sv_out_packet["speed(m/s)"] == v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["speed(m/s)"]

    ):
        
        v2x_adjusted_timestamp = float(v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["packetTimestamp"]) + sv_to_v2x_clock_skew

        sv_to_v2x_latency = v2x_adjusted_timestamp - float(sv_out_packet["packetTimestamp"])

        results_outfile_writer.writerow([
            sv_out_packet["packetIndex"],
            v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["packetIndex"],
            sv_out_packet["packetTimestamp"],
            v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["packetTimestamp"],
            v2x_adjusted_timestamp,
            sv_to_v2x_latency,

            bsm_broadcast_latency

        ])
        # print("Found matching data: ")
        # print("  - " + sv_out_packet["latitude"] + " == " + v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["latitude"])
        # print("  - " + sv_out_packet["longitude"] + " == " + v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["longitude"])
        # print("  - " + sv_out_packet["heading"] + " == " + v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["heading"])
        # print("  - " + sv_out_packet["speed(m/s)"] + " == " + v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["speed(m/s)"])

    else:
        print("[!!!] Found dropped packet: ")
        print("  - " + sv_out_packet["latitude"] + " == " + v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["latitude"])
        print("  - " + sv_out_packet["longitude"] + " == " + v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["longitude"])
        print("  - " + sv_out_packet["heading"] + " == " + v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["heading"])
        print("  - " + sv_out_packet["speed(m/s)"] + " == " + v2xhub_pcap_in_data_infile_reader_list[sv_out_i + sv_out_to_v2x_in_offset]["speed(m/s)"])

        sv_out_to_v2x_in_offset -= 1
        continue


    if (sv_out_i + sv_out_to_v2x_in_offset + 2 > total_v2xhub_in_packets):
        print("\nReached end of v2x in file, exiting")
        sys.exit()


    # print("\n----- TESTING EARLY EXIT -----")
    # sys.exit()

