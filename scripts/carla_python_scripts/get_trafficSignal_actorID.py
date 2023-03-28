import glob
import os
import sys

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

            egg_selected = input("\nSelect a carla egg file to use: ")

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