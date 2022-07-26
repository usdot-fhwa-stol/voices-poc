import json
import sys
from csv import reader, writer


#print("ARGS: " + sys.argv[0] + "," + sys.argv[1] + "," + sys.argv[2] + "," + sys.argv[3] + "," + sys.argv[4])
inFile = sys.argv[1]
payloadType=sys.argv[4]
print("Payload Type: " + payloadType)
fileName = inFile.split(".")

with open(fileName[0]+'.csv') as read_obj, \
open(fileName[0]+'_payload.csv', 'w', newline='') as write_obj:
    csv_reader = reader(read_obj)
    csv_writer = writer(write_obj)

    substr = {
        'map': '0012',
        'spat':'0013',
        'bsm': '0014',
        'req': '00f0',
        'res': '00f1',
        'mop': '00f2',
        'mom': '00f3',
        'tcr': '00f4',
        'tcm': '00f5'
    }

    for row in csv_reader:
        index = {}
        smallerIndex = 10000
        
        #remove newlines for ascii
        if payloadType == "ascii":
            row[1] = row[1].replace("\\n","")
        
        for k in substr:
            if substr[k] in row[1]:
                index[k] = row[1].find(substr[k])
                if index[k] < smallerIndex:
                    smallerIndex = index[k]
                    msg = row[1][smallerIndex:]
        
        csv_writer.writerow([row[0],msg])




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
