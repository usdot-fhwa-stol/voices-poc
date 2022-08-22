import json
import sys
from csv import reader, writer
import subprocess as sp
import re

print("ARGS: " + sys.argv[1] + "," + sys.argv[2])
inFile = sys.argv[1] # sit1_4_v2x_in.pcap
payload_type_id=sys.argv[2]
print("Payload Type: " + payload_type_id)
infile_array = inFile.split(".")
#fileName = inFile.split(".")

print("Getting JSON payloads for packets")
cmds = ["tshark", "-x", "-r",inFile , "-T", "json"]
frames_text = sp.check_output(cmds, text=True)
frames_json = json.loads(frames_text)

found_packets = 0
total_packets = 0


with open(infile_array[0] +'_payload.csv', 'w', newline='') as write_obj:
    csv_writer = writer(write_obj)

    for packet in frames_json:
        # if "data_raw" in packet["_source"]["layers"]:
        #     #print("we raw dawg")
        #     somevar=None
        # elif "adwin_config_raw" in packet["_source"]["layers"]:
        #     #print("we adwin_config_raw dawg?")
        #     somevar=None
        #     #print(packet)
        # else:
        #     print("WHAT IS THIS SHIT")
        #     some
        #     #print(packet)

        frame_raw = str(packet["_source"]["layers"]["frame_raw"][0])
        #print("Frame Raw: " + frame_raw)

        j2735_payload_with_header_search = re.search('0380.*'+ payload_type_id +'.*',frame_raw)
        
        if j2735_payload_with_header_search != None:
            j2735_payload_with_header = str(j2735_payload_with_header_search.group(0))
            found_packets += 1
            #print("Trimmed: " + str(j2735_payload_with_header))
            #print("With Header: " + j2735_payload_with_header)
            j2735_payload_with_header_cleaned_search = re.search(payload_type_id + '.*',j2735_payload_with_header)
            j2735_payload_with_header_cleaned = str(j2735_payload_with_header_cleaned_search.group(0))
            
            timestamp = packet["_source"]["layers"]["frame"]["frame.time_epoch"]

            # print("Timestamp: " + timestamp)
            # print("Clean: " + j2735_payload_with_header_cleaned)
            # print("")

            csv_writer.writerow([timestamp,j2735_payload_with_header_cleaned])

        total_packets += 1

print("Total Found Packets: " + str(found_packets))
print("Total Packets: " + str(total_packets))


