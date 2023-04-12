#!/usr/bin/env python3
import glob
import os
import sys
import numpy as np
import json
import time

from find_carla_egg import find_carla_egg

carla_egg_file = find_carla_egg()

sys.path.append(carla_egg_file)

import carla












actor_list=[]
try:
    # Initialize
    client = carla.Client('localhost', 2000)
    client.set_timeout(300.0)
    world = client.get_world()
    debug = world.debug
    switch
        line_list = generate_points()
    case
        intersection_map_json = ingest_map_data_from_map_file()
        intersection_map_points = ingest_points_from_map_data(intersection_map_json)


finally:
    print('Cleaning up actors...')
    for actor in actor_list:
        actor.destroy()
    print('Done, Actors cleaned-up successfully!')




def print_pointset():
    for i in range(0,10):
        for line_name, c in line_list.items():

            strt_point = carla.Location(x=c[0][0], y=c[0][1], z=c[0][2])
            stop_point = carla.Location(x=c[1][0], y=c[1][1], z=c[1][2])

            debug.draw_line(strt_point,stop_point,0.3,carla.Color(r=255,g=0,b=0),5)

            strt_point_geo = world.get_map().transform_to_geolocation(strt_point)
            stop_point_geo = world.get_map().transform_to_geolocation(stop_point)

            print("Line " + line_name)
            print("strt_point: " + str(strt_point_geo))
            print("stop_point: " + str(stop_point_geo))

        time.sleep(5)


def ingest_map_data_from_map_file(intersection_map_json_filename):
    return json.load(intersection_map_json_filename)

def ingest_points_from_map_data(intersection_map_json):
    # intersection_map_points = \
intersection_map_json["mapData"]["intersectionGeometry"]["referencePoint"]
intersection_map_json["mapData"]["intersectionGeometry"]["referencePoint"]["referenceLat"]
intersection_map_json["mapData"]["intersectionGeometry"]["referencePoint"]["referenceLon"]
intersection_map_json["mapData"]["intersectionGeometry"]["referencePoint"]["referenceElevation"]

intersection_map_json["mapData"]["intersectionGeometry"]["verifiedPoint"]
intersection_map_json["mapData"]["intersectionGeometry"]["verifiedPoint"]["verifiedMapLat"]
intersection_map_json["mapData"]["intersectionGeometry"]["verifiedPoint"]["verifiedMapLon"]
intersection_map_json["mapData"]["intersectionGeometry"]["verifiedPoint"]["verifiedMapElevation"]

intersection_map_json["mapData"]["intersectionGeometry"]["laneList"]
intersection_map_json["mapData"]["intersectionGeometry"]["laneList"]["approach"]
intersection_map_json["mapData"]["intersectionGeometry"]["laneList"]["approach"]["approachType"]
intersection_map_json["mapData"]["intersectionGeometry"]["laneList"]["approach"]["drivingLanes"]


approachList = intersection_map_json["mapData"]["intersectionGeometry"]["laneList"]["approach"]
for approach in approachList:
    approachID = approach["approachID"]
    approachType = approach["approachType"]
    for lane in approach["drivingLanes"]:
        laneID = lane["laneID"]
        for laneNode in lane["laneNodes"]:
            nodeLat = laneNode["nodeLat"]
            nodeLong = laneNode["nodeLong"]
            nodeElev = laneNode["nodeElev"]

    return intersection_map_points


def generate_points():
    lane_width=3.5
    intersection_length=20.35

    A2a = np.array([ 255.0, -180.65,    1.00])
    B4a = np.array([ 255.2, -301.50,    1.00])

    A2b = A2a + np.array([ lane_width, 0.15, 0])
    B4b = B4a + np.array([ lane_width, 0, 0])

    A4a = A2a + np.array([0, intersection_length, 0])
    A4b = A4a + np.array([ lane_width, 0, 0])

    A1a = A2a + np.array([-(intersection_length / 2.0) + 1.8, (intersection_length / 2.0) - 0.88 + (lane_width / 2.0), 0])
    A3a = A2a + np.array([ (intersection_length / 2.0) + 1.35, (intersection_length / 2.0) + (lane_width / 2.0) - 0.5, 0])
    A1b = A1a + np.array([ 0, -lane_width, 0 ])
    A3b = A3a + np.array([ 0, -lane_width, 0 ])

    C2a = A4a + np.array([ 0, 30.85, 0])
    C2b = C2a + np.array([ lane_width, 0, 0])

    D3a = A1a + np.array([-35.9, 0, 0 ])
    D3b = D3a + np.array([ 0, -lane_width, 0 ])

    E1a = A3a + np.array([ 36.4, 0, 0 ])
    E1b = E1a + np.array([ 0, -lane_width, 0 ])

    return {
        "A2a_B4a": (A2a, B4a),
        "A2b_B4b": (A2b, B4b),

        "A2a_A4a": (A2a, A4a),
        "A2b_A4b": (A2b, A4b),

        "A1a_A3a": (A1a, A3a),
        "A1b_A3b": (A1b, A3b),

        "A4a_C2a": (A4a, C2a),
        "A4b_C2b": (A4b, C2b),

        "A1a_D3a": (A1a, D3a),
        "A1b_D3b": (A1b, D3b),

        "A3a_E1a": (A3a, E1a),
        "A3b_E1b": (A3b, E1b),

    }
