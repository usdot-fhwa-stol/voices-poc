import glob
import os
import sys
import time
import argparse
import pygame
import json

from find_carla_egg import find_carla_egg

carla_egg_file = find_carla_egg()

sys.path.append(carla_egg_file)

import carla

def read_json(json_path):
    try:
        file = open(json_path)
        return json.load(file)
    except:
        print("Config file could not be opened: " + json_path)
        sys.exit()

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
        current_speed = 2.23694 * (velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2) ** 0.5
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
        print("Vehicle speed: {:.2f} mph".format(current_speed))
    vehicle.enable_constant_velocity(carla.Vector3D(x=0.0, y=0.0, z=0.0))
    time.sleep(3)
    #vehicle.destroy()

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
    time.sleep(3)
    #vehicle.destroy()


if __name__ == '__main__':
    # Set up argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--x', type=float, default=0, help='x coordinate of the spawn point')
    parser.add_argument('--y', type=float, default=0, help='y coordinate of the spawn point')
    parser.add_argument('--z', type=float, default=0, help='z coordinate of the spawn point')
    parser.add_argument('--yaw', type=float, default=0, help='yaw orientation of the vehicle')
    parser.add_argument('--velocity', type=float, default=25, help='velocity of the vehicle in km/h')
    parser.add_argument('--stop', type=str, default="point", help='enter stop condition by duration or point')
    parser.add_argument('--duration', type=float, default=15, help='vehilce running duration')
    parser.add_argument('--config', type=str, help='config file to import')
    parser.add_argument('--point', nargs='+', default=[255, -130, 0], help='enter an end point')
    parser.add_argument('--svm_vehicle_name',default="NISSAN-SVM",help='Vehicle to be used for the simple vehicle model (default: "NISSAN-SVM"')
    args = parser.parse_args()
    
    if args.config:

        config = read_json(args.config)
        # Connect to the simulator and retrieve the world
        client = carla.Client(config["CARLAIp"], config["CARLAPort"])
        client.set_timeout(2.0)
        world = client.get_world()
        for vehicle_cfg in config["vehicles"]:
            x_pt = vehicle_cfg["startPt"][0]
            y_pt = vehicle_cfg["startPt"][1]
            z_pt = vehicle_cfg["startPt"][2]
            yaw = vehicle_cfg["yaw"]
            # Spawn the vehicle at the specified location with the initial speed
            #vehicle = spawn_vehicle(world, vehicle_cfg["vehicleModel"], x_pt, y_pt, z_pt, yaw)
            carlaVehicles = world.get_actors().filter('vehicle.*')
            for current_vehicle in carlaVehicles:
                currentAttributes = current_vehicle.attributes
                if currentAttributes["role_name"] == args.svm_vehicle_name:
                        vehicle = current_vehicle
            
            if not current_vehicle:
                print("SVM VEHICLE NOT FOUND")
                sys.exit()

            # Set CARLA simulator as wall clock
            settings = world.get_settings()
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = None # Set a variable time-step
            world.apply_settings(settings)

            vehicle.set_location(carla.Location(x_pt,y_pt,z_pt))
            move_vehicle_with_point(world, vehicle, vehicle_cfg['endPt'], vehicle_cfg['targetSpeedMPH'] / 2.23694)

        settings.synchronous_mode = False
        world.apply_settings(settings)

    elif args.x and args.y and args.z:
        
        client = carla.Client(config["CARLAIp"], config["CARLAPort"])
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
    
        settings.synchronous_mode = False
        world.apply_settings(settings)
    else:
        print("\nNo config file or x,y,z set. Please set a config file or x,y,z")
