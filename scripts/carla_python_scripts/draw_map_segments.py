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
from enum import Enum

class CarlaColor:
    GRAY = carla.Color(r=102,g=153,b=204)
    GREEN = carla.Color(r=0,g=106,b=78)
    YELLOW = carla.Color(r=255,g=225,b=53)
    RED = carla.Color(r=227,g=0,b=34)
    ORGANGE = carla.Color(r=255,g=103,b=0)

class Segment:
    def __init__(self, segment_name, startx, starty, startz, endx, endy, endz, color):
        self.segment_name = segment_name
        self.startx = startx
        self.starty = starty
        self.startz = startz
        self.endx = endx
        self.endy = endy
        self.endz = endz
        self.color = color







actor_list=[]
try:
    # Initialize
    client = carla.Client('localhost', 2000)
    client.set_timeout(300.0)
    world = client.get_world()
    debug = world.debug
    switch
        line_list = generate_points()
        draw_segment_list()
    case
        intersection_map_json = ingest_map_data_from_map_file()
        intersection_map_segment_list = ingest_points_from_map_data(intersection_map_json)
        draw_segment_list(intersection_map_segment_list)


finally:
    print('Cleaning up actors...')
    for actor in actor_list:
        actor.destroy()
    print('Done, Actors cleaned-up successfully!')






def ingest_map_data_from_map_file(intersection_map_json_filename):
    return json.load(intersection_map_json_filename)

def ingest_points_from_map_data(intersection_map_json):
    intersectionID = intersection_map_json["mapData"]["intersectionGeometry"]["referencePoint"]["intersectionID"]
    referenceLat = intersection_map_json["mapData"]["intersectionGeometry"]["referencePoint"]["referenceLat"]
    referenceLon = intersection_map_json["mapData"]["intersectionGeometry"]["referencePoint"]["referenceLon"]
    referenceElevation = intersection_map_json["mapData"]["intersectionGeometry"]["referencePoint"]["referenceElevation"]

    approachList = intersection_map_json["mapData"]["intersectionGeometry"]["laneList"]["approach"]
    return list(approachList.map(lambda approach:
        approach["drivingLanes"].map(lambda lane:
        laneNodeList = lane["laneNodes"]
        segmentPairs = list(zip(laneNodeList[:-1], laneNodeList[1:]))


        for laneNode in lane["laneNodes"]:
            nodeLat = laneNode["nodeLat"]
            nodeLong = laneNode["nodeLong"]
            nodeElev = laneNode["nodeElev"]
            segment_list.append(Segment(
                "approachID-approachID-laneID-laneID",
                A2a[0], A2a[1],
                B4a[0], B4a[1],
                CarlaColor.GREEN if approach["approachType"] == "Ingress" else CarlaColor.ORANGE
    ))

    ))

def draw_segment_list(segmentList):
    for segment in segmentList:
        draw_line_segment(segment)

def draw_line_segment(segment):
    strt_point = carla.Location(x=segment.startx, y=segment.starty, z=segment.startz)
    stop_point = carla.Location(x=segment.endx, y=segment.endy, z=segment.endz)

    debug.draw_line(strt_point, stop_point, 0.3, segment.color, 0)

    strt_point_geo = world.get_map().transform_to_geolocation(strt_point)
    stop_point_geo = world.get_map().transform_to_geolocation(stop_point)

    print("Drawing segment: " + segment.segment_name)
    print("strt_point: " + str(strt_point_geo))
    print("stop_point: " + str(stop_point_geo))

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

    return [
        Segment("A2a_B4a", A2a[0], A2a[1], A2a[2], B4a[0], B4a[1], B4a[2], CarlaColor.GRAY),
        Segment("A2b_B4b", A2b[0], A2b[1], A2b[2], B4b[0], B4b[1], B4b[2], CarlaColor.GRAY),
        Segment("A2a_A4a", A2a[0], A2a[1], A2a[2], A4a[0], A4a[1], A4a[2], CarlaColor.GRAY),
        Segment("A2b_A4b", A2b[0], A2b[1], A2b[2], A4b[0], A4b[1], A4b[2], CarlaColor.GRAY),
        Segment("A1a_A3a", A1a[0], A1a[1], A1a[2], A3a[0], A3a[1], A3a[2], CarlaColor.GRAY),
        Segment("A1b_A3b", A1b[0], A1b[1], A1b[2], A3b[0], A3b[1], A3b[2], CarlaColor.GRAY),
        Segment("A4a_C2a", A4a[0], A4a[1], A4a[2], C2a[0], C2a[1], C2a[2], CarlaColor.GRAY),
        Segment("A4b_C2b", A4b[0], A4b[1], A4b[2], C2b[0], C2b[1], C2b[2], CarlaColor.GRAY),
        Segment("A1a_D3a", A1a[0], A1a[1], A1a[2], D3a[0], D3a[1], D3a[2], CarlaColor.GRAY),
        Segment("A1b_D3b", A1b[0], A1b[1], A1b[2], D3b[0], D3b[1], D3b[2], CarlaColor.GRAY),
        Segment("A3a_E1a", A3a[0], A3a[1], A3a[2], E1a[0], E1a[1], E1a[2], CarlaColor.GRAY),
        Segment("A3b_E1b", A3b[0], A3b[1], A3b[2], E1b[0], E1b[1], E1b[2], CarlaColor.GRAY)
    ]
