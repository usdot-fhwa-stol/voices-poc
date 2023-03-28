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

#this looks for the carla python API .egg file in the directory above the executed directory
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:

    #this looks for the carla python API .egg file in ~/carla
    try:
        
        carla_egg_name = 'carla-*' + str(sys.version_info.major) + '.*-' + str('win-amd64' if os.name == 'nt' else 'linux-x86_64') + '.egg'
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

import argparse
import pygame
import carla
import time


def spawn_vehicle(world, blueprint_name, x, y, z, yaw):
    blueprint = world.get_blueprint_library().find(blueprint_name)
    spawn_point = carla.Transform(
        carla.Location(x=x, y=y, z=z),
        carla.Rotation(yaw=yaw)
    )
    vehicle = world.try_spawn_actor(blueprint, spawn_point)
    if vehicle is None:
        print("Error: Vehicle could not be spawned!")
        exit()
    vehicle.set_autopilot(False)
    return vehicle

def move_vehicle_with_point(world, vehicle, point, velocity):
    vehicle.enable_constant_velocity(carla.Vector3D(x=velocity, y=0.0, z=0.0))
    # print(type(vehicle.get_location()))
    #index = next(i for i, x in enumerate(point) if x != 0)
    while True:
        world.tick()
        location = vehicle.get_location()
        velocity = vehicle.get_velocity()
        current_speed = 3.6 * (velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2) ** 0.5
        tmp = [float(i) for i in point]
        # tmp = [0,0,0]
        tmp_loc = [location.x, location.y, location.z]
        # for i in range(len(tmp_loc)):
        #     if i == index:
        #         tmp[i] = point[i]
        #         continue
        #     else:
        #         tmp[i] = tmp_loc[i]

        # tmp = [float(i) for i in tmp]
        print("tmp: " + str(tmp))
        print("tmp_loc: " + str(tmp_loc))

        dist_from_end = ((tmp[0]-tmp_loc[0])**2 + (tmp[1]-tmp_loc[1])**2 + (tmp[2]-tmp_loc[2])**2) ** 0.5
        print("Distance to end point: " + str(dist_from_end))
        if ((tmp[0]-tmp_loc[0])**2 + (tmp[1]-tmp_loc[1])**2 + (tmp[2]-tmp_loc[2])**2) ** 0.5 <= 2:
            print("REACHED END")
            break
        print("-" * 10)
        print(f"Distance to end point: {((tmp[0]-tmp_loc[0])**2 + (tmp[1]-tmp_loc[1])**2 + (tmp[2]-tmp_loc[2])**2) ** 0.5:.2f} meter")
        print(f"Simulation time: {world.get_snapshot().timestamp.elapsed_seconds:.2f} seconds")
        print("Vehicle location: x={}, y={}, z={}".format(location.x, location.y, location.z))
        print("Vehicle speed: {:.2f} km/h".format(current_speed))
        # time.sleep(0.1)
    vehicle.enable_constant_velocity(carla.Vector3D(x=0.0, y=0.0, z=0.0))
    time.sleep(1)
    vehicle.destroy()

def move_vehicle_with_duration(world, vehicle, duration, velocity):
    vehicle.enable_constant_velocity(carla.Vector3D(x=velocity, y=0.0, z=0.0))
    start_time = world.get_snapshot().timestamp.elapsed_seconds
    curr_time = world.get_snapshot().timestamp.elapsed_seconds
    while curr_time - start_time < duration:
        location = vehicle.get_location()
        velocity = vehicle.get_velocity()
        current_speed = 3.6 * (velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2) ** 0.5
        curr_time = world.get_snapshot().timestamp.elapsed_seconds

        print("-" * 10)
        print(f"Simulation time: {curr_time:.2f} seconds")
        print("Vehicle location: x={}, y={}, z={}".format(location.x, location.y, location.z))
        print("Vehicle speed: {:.2f} km/h".format(current_speed))
        time.sleep(0.1)
    vehicle.enable_constant_velocity(carla.Vector3D(x=0.0, y=0.0, z=0.0))
    time.sleep(1)
    vehicle.destroy()


if __name__ == '__main__':
    # Set up argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--x', type=float, default=-9.635131, help='x coordinate of the spawn point')
    parser.add_argument('--y', type=float, default=-146.145798, help='y coordinate of the spawn point')
    parser.add_argument('--z', type=float, default=0.281942, help='z coordinate of the spawn point')
    parser.add_argument('--yaw', type=float, default=89.775162, help='yaw orientation of the vehicle')
    parser.add_argument('--velocity', type=float, default=32.0, help='velocity of the vehicle in km/h')
    parser.add_argument('--stop', type=str, default="point", help='enter stop condition by duration or point')
    parser.add_argument('--duration', type=float, default=15, help='vehilce running duration')
    parser.add_argument('--point', nargs='+', default=[255, -130, 0], help='enter an end point')
    args = parser.parse_args()

    # Connect to the simulator and retrieve the world
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()

    # Spawn the vehicle at the specified location with the initial speed
    vehicle = spawn_vehicle(world, 'vehicle.nissan.micra', args.x, args.y, args.z, args.yaw)
    print("Press SPACE key to start the vehicle")
    running = False

    # Set CARLA simulator as wall clock
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = None # Set a variable time-step
    world.apply_settings(settings)

    # Set up the Pygame window and clock
    pygame.init()

    screen = pygame.display.set_mode((700, 100))
    # Set the font and text for the message
    font = pygame.font.SysFont("monospace", 30)
    text = font.render("Press SPACE to start vehicle movement", True, (255, 255, 255))

    # Draw the message on the screen
    screen.blit(text, (10, 10))
    pygame.display.flip()

    clock = pygame.time.Clock()

    # Game loop
    while True:
        world.tick()
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = True

        # Clear the screen
        screen.fill((255, 255, 255))
        # If the vehicle is running,  move it and draw the speed on the screen
        if running:
            if args.stop == "time":
                move_vehicle_with_duration(world, vehicle, args.duration, args.velocity / 3.6)
            elif args.stop == "point":
                print("STOP POINT: " + str(args.point))
                move_vehicle_with_point(world, vehicle, args.point, args.velocity / 3.6)

            settings.synchronous_mode = False
            world.apply_settings(settings)
            break
