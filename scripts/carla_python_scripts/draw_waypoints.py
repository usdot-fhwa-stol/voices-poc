import os
import sys
import re
import argparse
import json
import math
import time
import pandas as pd



from find_carla_egg import find_carla_egg

carla_egg_file = find_carla_egg()

sys.path.append(carla_egg_file)

import carla

from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.navigation.global_route_planner_dao import GlobalRoutePlannerDAO

argparser = argparse.ArgumentParser(
    description=__doc__)
argparser.add_argument(
    '--host',
    metavar='H',
    default='127.0.0.1',
    help='IP of the host server (default: 127.0.0.1)')
argparser.add_argument(
    '-p', '--port',
    metavar='P',
    default=2000,
    type=int,
    help='TCP port to listen to (default: 2000)')
argparser.add_argument(
    '--follow_vehicle',
    help='Vehicle to be used for the follow cam (default: "TFHRC-MANUAL-1"')
argparser.add_argument(
    '-f', '--file',
    metavar='f',
    type=str,
    help='Import file to read crossing data')
args = argparser.parse_args()

def draw_waypoints(world,map,start_point,end_point):   

    # box_center = carla.Location(x=vru_x, y=vru_y, z=draw_z_height)

    # vru_box = carla.BoundingBox(box_center,carla.Vector3D(1.5,1.5,0))

    # world.debug.draw_box(
    #     vru_box, 
    #     carla.Rotation(0,0,0),
    #     0.2,
    #     # draw_shadow=False,
    #     color=carla.Color(r=255, g=0, b=0), 
    #     life_time=draw_lifetime,
    #     persistent_lines=True)
    # client = carla.Client("localhost", 2000)
    # client.set_timeout(10)
    # world = client.load_world('Town01')
    # map = world.get_map()
    sampling_resolution = 0.5
    dao = GlobalRoutePlannerDAO(map, sampling_resolution)
    grp = GlobalRoutePlanner(dao)
    grp.setup()
    # spawn_points = map.get_spawn_points()
    
    print("\nStart Point XYZ: " + str(start_point))
    start_point_geo = map.transform_to_geolocation(start_point)
    print("Start Point Lat/Long: " + str(start_point_geo))
    print("End Point XYZ: " + str(end_point))
    end_point_geo = map.transform_to_geolocation(end_point)
    print("End Point Lat/Long: " + str(end_point_geo))
    
    w1 = grp.trace_route(start_point, end_point) # there are other funcations can be used to generate a route in GlobalRoutePlanner.
    i = 0

    waypoint_data = {
        "index" : [],
        "x" : [],
        "y" : [],
        "z" : [],
        "latitude" : [],
        "longitude" : [],
        "altitude" : [],
    }

    for w in w1:
        if i % 10 == 0:
            world.debug.draw_string(w[0].transform.location, 'O', draw_shadow=False,color=carla.Color(r=0, g=0, b=255), life_time=drawing_lifetime,persistent_lines=True)
        else:
            world.debug.draw_string(w[0].transform.location, 'O', draw_shadow=False,color = carla.Color(r=0, g=0, b=255), life_time=drawing_lifetime,persistent_lines=True)

        waypoint_data["index"].append(i)
        waypoint_data["x"].append(w[0].transform.location.x)
        waypoint_data["y"].append(w[0].transform.location.y)
        waypoint_data["z"].append(w[0].transform.location.z)

        w_geo = map.transform_to_geolocation(w[0].transform.location)

        waypoint_data["latitude"].append(w_geo.latitude)
        waypoint_data["longitude"].append(w_geo.longitude)
        waypoint_data["altitude"].append(w_geo.altitude)
                
        i += 1
    

    world.debug.draw_string(start_point, 'O', draw_shadow=False,color = carla.Color(r=0, g=255, b=0), life_time=drawing_lifetime,persistent_lines=True)
    world.debug.draw_string(end_point, 'O', draw_shadow=False,color = carla.Color(r=255, g=0, b=0), life_time=drawing_lifetime,persistent_lines=True)

    return waypoint_data

try:
    client = carla.Client(args.host, args.port)
    client.set_timeout(5.0)
    world = client.get_world()
    map = world.get_map()

    event2_spawns = [
        {
            "name" : "FHWA",
            "spawn_point" : carla.Location(x=59.296265, y=67.242165, z=235.812256),
            "end_point" : carla.Location(x=99.357674, y=-83.244278, z=242.828964),
        },
        {
            "name" : "ORNL",
            "spawn_point" : carla.Location(x=57.231377, y=59.069706, z=236.117538),
            "end_point" : carla.Location(x=99.357674, y=-83.244278, z=242.828964),
        },
        {
            "name" : "ANL",
            "spawn_point" : carla.Location(x=56.112572, y=52.548759, z=236.292847),
            "end_point" : carla.Location(x=99.357674, y=-83.244278, z=242.828964),
        },
        {
            "name" : "UCLA",
            "spawn_point" : carla.Location(x=55.125175, y=45.391933, z=236.519577),
            "end_point" : carla.Location(x=99.357674, y=-83.244278, z=242.828964),
        },
    ]

    drawing_lifetime = 3


    if args.follow_vehicle:
        while True:
            world = client.get_world()
            map = world.get_map() 

            end_point = carla.Location(x=99.357674, y=-83.244278, z=242.828964)

            carlaVehicles = world.get_actors().filter('vehicle.*')
            for vehicle in carlaVehicles:
                currentAttributes = vehicle.attributes
                print("Checking vehicle: " + str(currentAttributes["role_name"]))
                if currentAttributes["role_name"] == args.follow_vehicle:
                    player = vehicle
            if not player:
                print("ERROR: Unable to find vehicle with rolename: " + args.follow_vehicle)
                sys.exit()
            
            try:
                draw_waypoints(world,map,player.get_location(),end_point)
            except Exception as errMsg:
                print("UNABLE TO FIND ROUTE")
                print(errMsg)

            time.sleep(drawing_lifetime)
    else:
        for test_spawn in event2_spawns:
            # world.debug.draw_string(test_spawn["spawn_point"], "o", draw_shadow=False,color = carla.Color(r=255, g=255, b=0), life_time=drawing_lifetime,persistent_lines=True)
            print("\nDrawing: " + test_spawn["name"])
            world.debug.draw_string(test_spawn["spawn_point"], "     " + test_spawn["name"], draw_shadow=False,color = carla.Color(r=255, g=255, b=0), life_time=drawing_lifetime,persistent_lines=True)
            waypoint_data = draw_waypoints(world,map,test_spawn["spawn_point"],test_spawn["end_point"])

            df = pd.DataFrame(waypoint_data)
            df.to_csv(test_spawn["name"] + '_waypoints.csv', index=False)

            time.sleep(drawing_lifetime)

finally:
    print('\nDone!')
