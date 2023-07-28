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
    # map = world.get_map()
    # Get actor information (Traffic Lights)
    traffic_light_list = world.get_actors().filter('traffic.traffic_light*')
    # Print all index corresponding to all traffic lights in scene (CarlaUE4)
    for index, light in enumerate(traffic_light_list, start=1):
        print(light.id)
        world.debug.draw_string(light.get_location(), str(light.id), draw_shadow=False,
                                             color=carla.Color(r=255, g=0, b=0), life_time=200,
                                             persistent_lines=True)
        
    ################################################################################################
    # Once you see all index number, you can manually change its states and timimg.
    # Your signal control scripts.
finally:
    print('Cleaning up actors...')
    for actor in actor_list:
        actor.destroy()
    print('Done, Actors cleaned-up successfully!')
