import glob
import os
import sys

from find_carla_egg import find_carla_egg

carla_egg_file = find_carla_egg()

sys.path.append(carla_egg_file)

import carla

actor_list=[]
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)
    world = client.get_world()
    
    stop_bar_north = carla.Location(x=255, y=-180, z=1)
    stop_bar_south = carla.Location(x=255, y=-299.5, z=1)
    
    debug = world.debug
    
    debug.draw_line(stop_bar_north,stop_bar_south,0.3,carla.Color(r=255,g=0,b=0),5)

    stop_bar_north_geo = world.get_map().transform_to_geolocation(stop_bar_north)
    stop_bar_south_geo = world.get_map().transform_to_geolocation(stop_bar_south)
    print("stop_bar_north: " + str(stop_bar_north_geo))
    print("stop_bar_south: " + str(stop_bar_south_geo))

finally:
    print('Cleaning up actors...')
    for actor in actor_list:
        actor.destroy()
    print('Done, Actors cleaned-up successfully!')