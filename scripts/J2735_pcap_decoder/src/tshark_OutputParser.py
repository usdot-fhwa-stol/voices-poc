import json
import sys
from csv import writer
from csv import reader

inFile = sys.argv[1]
payloadType=sys.argv[3]
#print("Payload Type: " + payloadType)
fileName = inFile.split(".")

with open(fileName[0]+'.csv') as read_obj, \
open(fileName[0]+'_payload.csv', 'w', newline='') as write_obj:
    csv_reader = reader(read_obj)
    csv_writer = writer(write_obj)
    map_substr = "0012"
    spat_substr = "0013"
    bsm_substr = "0014"

    for row in csv_reader:
        bsm_index = 10000
        map_index = 10000
        spat_index = 10000
        
        #remove newlines for ascii
        if( payloadType == "ascii" ):
            row[1] = row[1].replace("\\n","")
        

        if map_substr in row[1]:
            map_index = row[1].find(map_substr)
        if spat_substr in row[1]:
            spat_index = row[1].find(spat_substr)
            spat_length = len(row[1])
        if "Kapsch" in fileName[0] and bsm_substr in row[2]:
            bsm_index = row[2].find(bsm_substr)
            bsm_length = len(row[2])
        if bsm_substr in row[1]:
            bsm_index = row[1].find(bsm_substr)
            bsm_length = len(row[1])

        if map_index < spat_index and map_index < bsm_index:
            map = row[1][map_index:]
            csv_writer.writerow([row[0], map])
        elif spat_index < map_index and spat_index < bsm_index and "mk5" in fileName[0] and "rx" in fileName[0]:
            spat = row[1][spat_index:spat_length-8]
            csv_writer.writerow([row[0], spat])
        elif spat_index < map_index and spat_index < bsm_index:
            spat = row[1][spat_index:]
            csv_writer.writerow([row[0], spat])
        if bsm_index < map_index and bsm_index < spat_index and "CohdaRSU_rx" in fileName[0]:
            bsm = row[1][bsm_index:bsm_length-8]
            csv_writer.writerow([row[0], bsm])
        elif bsm_index < map_index and bsm_index < spat_index and "Kapsch" in fileName[0]:
            bsm = row[2][bsm_index:]
            csv_writer.writerow([row[0], bsm])
        elif bsm_index < map_index and bsm_index < spat_index:
            bsm = row[1][bsm_index:]
            csv_writer.writerow([row[0], bsm])
