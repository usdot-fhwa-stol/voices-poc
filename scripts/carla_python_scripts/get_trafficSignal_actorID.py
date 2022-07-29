import glob
import os
import sys
from os.path import expanduser

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
    
try:
    
    sys.path.append(glob.glob(expanduser("~") + '/carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

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
        world.debug.draw_string(light.get_location(), str(index-1), draw_shadow=False,
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