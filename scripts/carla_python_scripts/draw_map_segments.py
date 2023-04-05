#!/usr/bin/env python3
import glob
import os
import sys

import numpy as np
import time

import fnmatch
from os.path import expanduser

def find_file(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result 

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%s.%s-%s.egg' % (
        '*',
        '*',
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:

    #this looks for the carla python API .egg file in ~/carla
    try:
        
        carla_egg_name = 'carla-*' + '-' + str('win-amd64' if os.name == 'nt' else 'linux-x86_64') + '.egg'
        print("Looking for CARLA egg: " + carla_egg_name)
        carla_egg_locations = find_file(carla_egg_name,expanduser("~"))
        print("Found carla egg(s): " + str(carla_egg_locations))

        if len(carla_egg_locations) == 1:
            carla_egg_to_use = carla_egg_locations[0]
        else:
            print("\nFound multiple carla egg files: ")
            for i,egg_found in enumerate(carla_egg_locations):
                print("[" + str(i+1) + "]    " + egg_found)

            #egg_selected = input("\nSelect a carla egg file to use: ")
            egg_selected=3

            try:
                egg_selected = int(egg_selected)
            except:
                print("\nInvalid selection, please try again")
                sys.exit()

            if (egg_selected <= len(carla_egg_locations)):
                carla_egg_to_use = carla_egg_locations[egg_selected-1]
            else:
                print("\nInvalid selection, please try again")
                sys.exit()

        sys.path.append(carla_egg_to_use)

        #sys.path.append(glob.glob(expanduser("~") + '/carla/CARLA_0.9.10_TFHRC_Ubuntu_20220301/LinuxNoEditor/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        #    sys.version_info.major,
        #    sys.version_info.minor,
        #    'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    except IndexError:
        pass

import carla

actor_list=[]
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(300.0)
    world = client.get_world()

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
    
    line_list={
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
    
    debug = world.debug

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

finally:
    print('Cleaning up actors...')
    for actor in actor_list:
        actor.destroy()
    print('Done, Actors cleaned-up successfully!')


# Data output 20230405 000
#
# Line A2a_B4a
# strt_point: GeoLocation(latitude=0.001623, longitude=0.002291, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.002708, longitude=0.002293, altitude=1.000000)
# Line A2b_B4b
# strt_point: GeoLocation(latitude=0.001621, longitude=0.002322, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.002708, longitude=0.002324, altitude=1.000000)
# Line A2a_A4a
# strt_point: GeoLocation(latitude=0.001623, longitude=0.002291, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001440, longitude=0.002291, altitude=1.000000)
# Line A2b_A4b
# strt_point: GeoLocation(latitude=0.001621, longitude=0.002322, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001440, longitude=0.002322, altitude=1.000000)
# Line A1a_A3a
# strt_point: GeoLocation(latitude=0.001524, longitude=0.002215, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001520, longitude=0.002394, altitude=1.000000)
# Line A1b_A3b
# strt_point: GeoLocation(latitude=0.001555, longitude=0.002215, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001552, longitude=0.002394, altitude=1.000000)
# Line A4a_C2a
# strt_point: GeoLocation(latitude=0.001440, longitude=0.002291, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001163, longitude=0.002291, altitude=1.000000)
# Line A4b_C2b
# strt_point: GeoLocation(latitude=0.001440, longitude=0.002322, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001163, longitude=0.002322, altitude=1.000000)
# Line A1a_D3a
# strt_point: GeoLocation(latitude=0.001524, longitude=0.002215, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001524, longitude=0.001893, altitude=1.000000)
# Line A1b_D3b
# strt_point: GeoLocation(latitude=0.001555, longitude=0.002215, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001555, longitude=0.001893, altitude=1.000000)
# Line A3a_E1a
# strt_point: GeoLocation(latitude=0.001520, longitude=0.002394, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001520, longitude=0.002721, altitude=1.000000)
# Line A3b_E1b
# strt_point: GeoLocation(latitude=0.001552, longitude=0.002394, altitude=1.000000)
# stop_point: GeoLocation(latitude=0.001552, longitude=0.002721, altitude=1.000000)
