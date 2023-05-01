#!/usr/bin/env python3

import argparse
import json
import re

def process(dataMap, keyRegex, fcn):
    if isinstance(dataMap, dict):
        for k, v in dataMap.items():
            # print(f"key: {k}")
            # if not (re.search(keyRegex, k) is None):
            if k == keyRegex:
                # print(f"updating dataMap[{k}] to:")
                newValue = fcn(v)
                # print(f"newValue {newValue}")
                dataMap[k] = newValue
            else:
                process(v, keyRegex, fcn)
    elif isinstance(dataMap, list):
        for item in dataMap:
            # print(f"item: {item}")
            process(item, keyRegex, fcn)
    # else:
    #     return dataMap

# def fcn(dataMap):
#     return dataMap

if __name__ == '__main__':

    # Input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--t', type=str, default=0, help='Template filename')
    parser.add_argument('--o', type=str, default=0, help='Output filename')
    parser.add_argument('--lat', type=float, default=0, help='Latitude of reference point')
    parser.add_argument('--lon', type=float, default=0, help='Longitude of reference point')
    args = parser.parse_args()

    # Load template
    templateFile = open(args.t)
    dataMap = json.load(templateFile)


    # Compute offsets
    deltaLat = args.lat - dataMap["vectors"]["features"][0]["properties"]["verifiedLat"]
    deltaLon = args.lon - dataMap["vectors"]["features"][0]["properties"]["verifiedLon"]





    with open("dataMap.0.json", "w") as outputFile:
        outputFile.write(json.dumps(dataMap, indent=4))

    process(dataMap, "lat", lambda x: x + deltaLat)
    process(dataMap, "lon", lambda x: x + deltaLon)

    process(dataMap, "verifiedLat", lambda x: x + deltaLat)
    process(dataMap, "verifiedLon", lambda x: x + deltaLon)

    with open("dataMap.1.json", "w") as outputFile:
        outputFile.write(json.dumps(dataMap, indent=4))



    #
    # "verifiedLat"
    # "verifiedLon"
    #
    #
    # "lon"
    # "lat"



    # "geometry": {
    #     "type": "Point",
    #     "coordinates": [
    #         1320909.0795635933,
    #         -533950.4490880023
    #     ]
    # }


    # "geometry": {
    # "type": "Polygon",
    # "coordinates": [
    # [
    #     [
    #         1320915.6856938,
    #         -533951.40081856
    #     ],
    #     [
    #         1320915.6856938,
    #         -533945.13059359
    #     ],


    # "geometry": {
    #     "type": "LineString",
    #     "coordinates": [
    #         [
    #             1320905.0113822275,
    #             -533944.0855560879
    #         ],






    #
    #
    #
    #
    # # Write output file
    # with open(args.o, "w") as outfile:
    #     json.dump(dataMap, outfile)
