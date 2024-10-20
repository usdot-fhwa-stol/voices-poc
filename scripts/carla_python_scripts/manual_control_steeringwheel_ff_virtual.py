#!/usr/bin/env python3

# Copyright (c) 2019 University of Leicester
# Copyright (c) 2019 University of Sao Paulo
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# Allows controlling a vehicle with a keyboard and steering wheel. For a simpler and more
# documented example, please take a look at tutorial.py.

"""
Welcome to CARLA manual control with steering wheel Logitech G29.

To drive start by pressing the brake pedal.
Change your wheel_config.ini according to your steering wheel.

To find out the values of your steering wheel use jstest-gtk in Ubuntu.

"""

from __future__ import print_function


# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys
import evdev
from evdev import ecodes, InputDevice, ff

from find_carla_egg import find_carla_egg

carla_egg_file = find_carla_egg()

sys.path.append(carla_egg_file)

# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================


import carla

from carla import ColorConverter as cc

#from srunner.scenariomanager.atomic_scenario_criteria import ScenarioInfo
#from srunner.scenariomanager.timer import ScenarioTimer


import argparse
import collections
import datetime
import logging
import math
import time
import random
import re
import weakref

if sys.version_info >= (3, 0):

    from configparser import ConfigParser

else:

    from ConfigParser import RawConfigParser as ConfigParser

try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import KMOD_SHIFT
    from pygame.locals import K_0
    from pygame.locals import K_9
    from pygame.locals import K_BACKQUOTE
    from pygame.locals import K_BACKSPACE
    from pygame.locals import K_COMMA
    from pygame.locals import K_DOWN
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_F1
    from pygame.locals import K_LEFT
    from pygame.locals import K_PERIOD
    from pygame.locals import K_RIGHT
    from pygame.locals import K_SLASH
    from pygame.locals import K_SPACE
    from pygame.locals import K_TAB
    from pygame.locals import K_UP
    from pygame.locals import K_a
    from pygame.locals import K_c
    from pygame.locals import K_d
    from pygame.locals import K_h
    from pygame.locals import K_m
    from pygame.locals import K_p
    from pygame.locals import K_q
    from pygame.locals import K_r
    from pygame.locals import K_s
    from pygame.locals import K_w
    from pygame.locals import K_KP_ENTER
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')


# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================


def find_weather_presets():
    rgx = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    name = lambda x: ' '.join(m.group(0) for m in rgx.finditer(x))
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]
    return [(getattr(carla.WeatherParameters, x), name(x)) for x in presets]


def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name


# ==============================================================================
# -- World ---------------------------------------------------------------------
# ==============================================================================


class World(object):
    def __init__(self, carla_world, hud, actor_filter,args):
        self._actor_filter = actor_filter
        
        self.world = carla_world
        self.hud = hud
        self.player = None
        self._init_spawn = None
        self.map = self.world.get_map()
        counter = 3
        #Find hero spanwed by the scenario
        # Get a random blueprint.
        
        self._blueprint_index = 0
        self._blueprint_list = self.world.get_blueprint_library().filter(self._actor_filter)
        blueprint = self._blueprint_list[self._blueprint_index]
        blueprint.set_attribute('role_name', 'hero')
        while self.player is None:
            #spawn_points = self.world.get_map().get_spawn_points()
            #spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            #self.player = self.world.try_spawn_actor(blueprint, spawn_point)
            carlaVehicles = self.world.get_actors().filter('vehicle.*')
            for vehicle in carlaVehicles:
                currentAttributes = vehicle.attributes
                print("Checking vehicle: " + str(currentAttributes["role_name"]))
                if currentAttributes["role_name"] == args.follow_vehicle:
                    self.player = vehicle
            if not self.player:
                print("ERROR: Unable to find vehicle with rolename: " + args.follow_vehicle)

#        while self.player is None:
#            for event in pygame.event.get():
#                if(event.type == pygame.KEYUP and event.key == K_ESCAPE):
#                    raise KeyboardInterrupt("Closed before starting scenario")
#            font = pygame.font.Font('freesansbold.ttf',32)
#            text = font.render("Loading"+("."*(counter % 4))+(" "*(4-counter % 4)),True,(255,255,255),(0,0,0))
#            textRect = text.get_rect()
#            surf = pygame.display.get_surface()
#            textRect.center = (surf.get_width() // 2, surf.get_height() // 2)
#            surf.blit(text,textRect)
#            pygame.display.update()
#            time.sleep(1)
#            possible_vehicles = self.world.get_actors().filter('vehicle.*')
#            counter += 1
#            for vehicle in possible_vehicles:
#                if vehicle.attributes['role_name'] == "hero":
#                    self.player = vehicle
#                    break
                    
                    
        self.player_name = self.player.type_id
        self.collision_sensor = CollisionSensor(self.player, self.hud)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.hud)
        self.gnss_sensor = GnssSensor(self.player)
        self.camera_manager = CameraManager(self.player, self.hud)
        self.camera_manager.transform_index = 0
        self.camera_manager.set_sensor(0, notify=False)

        self._weather_presets = find_weather_presets()
        self._weather_index = 0
        self._actor_filter = actor_filter
        self.world.on_tick(hud.on_world_tick)

    def next_weather(self, reverse=False):
        self._weather_index += -1 if reverse else 1
        self._weather_index %= len(self._weather_presets)
        preset = self._weather_presets[self._weather_index]
        self.hud.notification('Weather: %s' % preset[1])
        self.player.get_world().set_weather(preset[0])

    def tick(self, clock):
        #if len(self.world.get_actors().filter(self.player_name)) < 1:
        #    print("No actors -- waiting for respawn")
        #    return True

        self.hud.tick(self, clock)
        return True

    def nextVehicle(self):
        # Get a random blueprint.
        self._blueprint_index += 1
        self._blueprint_index %= len(self._blueprint_list)
        blueprint = self._blueprint_list[self._blueprint_index]
        blueprint.set_attribute('role_name', 'hero')
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        self.restart(blueprint)
    
    def prevVehicle(self):
        # Get a random blueprint.
        self._blueprint_index += -1
        self._blueprint_index %= len(self._blueprint_list)
        blueprint = self._blueprint_list[self._blueprint_index]
        blueprint.set_attribute('role_name', 'hero')
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        self.restart(blueprint)

    def render(self, display):
        self.camera_manager.render(display)
        self.hud.render(display)
    
    def restart(self,blueprint):
        #self.player_max_speed = 1.589
        #self.player_max_speed_fast = 3.713
        # Keep same camera config if the camera manager exists.
        cam_index = self.camera_manager.index if self.camera_manager is not None else 0
        cam_pos_index = self.camera_manager.transform_index if self.camera_manager is not None else 0
        
        if blueprint.has_attribute('driver_id'):
            driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
            blueprint.set_attribute('driver_id', driver_id)
        if blueprint.has_attribute('is_invincible'):
            blueprint.set_attribute('is_invincible', 'true')
        # set the max speed
        #if blueprint.has_attribute('speed'):
        #    self.player_max_speed = float(blueprint.get_attribute('speed').recommended_values[1])
        #    self.player_max_speed_fast = float(blueprint.get_attribute('speed').recommended_values[2])
        #else:
        #    print("No recommended values for 'speed' attribute")
        # Spawn the player.
        if self.player is not None:
            spawn_point = self.player.get_transform()
            spawn_point.location.z += 2.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            carlaVehicles = self.world.get_actors().filter('vehicle.*')
            for vehicle in carlaVehicles:
                currentAttributes = vehicle.attributes
                if currentAttributes["role_name"] == "CARLA-MANUAL-1":
                    self.player = vehicle
        while self.player is None:
            carlaVehicles = self.world.get_actors().filter('vehicle.*')
            for vehicle in carlaVehicles:
                currentAttributes = vehicle.attributes
                if currentAttributes["role_name"] == "CARLA-MANUAL-1":
                    self.player = vehicle
        # Set up the sensors.
        self.collision_sensor = CollisionSensor(self.player, self.hud)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.hud)
        self.gnss_sensor = GnssSensor(self.player)
        #self.imu_sensor = IMUSensor(self.player)
        self.camera_manager = CameraManager(self.player, self.hud)
        self.camera_manager.transform_index = cam_pos_index
        self.camera_manager.set_sensor(cam_index, notify=False)
        actor_type = get_actor_display_name(self.player)
        self.hud.notification(actor_type)
        
        #controller = DualControl(self, False)
        
    def destroy(self):
        actors = [
            self.camera_manager.sensor,
            self.collision_sensor.sensor,
            self.lane_invasion_sensor.sensor,
            self.gnss_sensor.sensor,
            self.player]
        for actor in actors:
            if actor is not None:
                actor.destroy()


# ==============================================================================
# -- DualControl -----------------------------------------------------------
# ==============================================================================


class DualControl(object):
    def __init__(self, world, start_in_autopilot):
        self._autopilot_enabled = start_in_autopilot
        if isinstance(world.player, carla.Vehicle):
            self._control = carla.VehicleControl()
            world.player.set_autopilot(self._autopilot_enabled)
        elif isinstance(world.player, carla.Walker):
            self._control = carla.WalkerControl()
            self._autopilot_enabled = False
            self._rotation = world.player.get_transform().rotation
        else:
            raise NotImplementedError("Actor type not supported")
        self._steer_cache = 0.0
        # world.hud.notification("Press 'H' or '?' for help.", seconds=4.0)

        # initialize steering wheel
        pygame.joystick.init()

        try:
            self._joystick = pygame.joystick.Joystick(1)
        except:
            try:
                self._joystick = pygame.joystick.Joystick(0)
            except:
                print("\nERROR: NO JOYSTICK FOUND")


        self._joystick.init()
        # evdev references to the steering wheel (force feedback)
        self._device = evdev.list_devices()[0]
        self._evtdev = InputDevice(self._device)
        self._evtdev.write(ecodes.EV_FF, ecodes.FF_AUTOCENTER, int(65535*.75))
        time.sleep(1)

        self._parser = ConfigParser()
        self._parser.read('wheel_config.ini')
        self._steer_idx = int(
            self._parser.get('G29 Racing Wheel', 'steering_wheel'))
        self._throttle_idx = int(
            self._parser.get('G29 Racing Wheel', 'throttle'))
        self._brake_idx = int(self._parser.get('G29 Racing Wheel', 'brake'))
        self._reverse_idx = int(self._parser.get('G29 Racing Wheel', 'reverse'))
        self._handbrake_idx = int(self._parser.get('G29 Racing Wheel', 'handbrake'))
        self._respawn_idx = int(self._parser.get('G29 Racing Wheel', 'respawn'))
        
        self._nextVehicle_idx = int(self._parser.get('G29 Racing Wheel', 'nextVehicle'))
        self._prevVehicle_idx = int(self._parser.get('G29 Racing Wheel', 'prevVehicle'))
        
        self._shiftUp_idx = int(self._parser.get('G29 Racing Wheel', 'shiftUp'))
        self._shiftDown_idx = int(self._parser.get('G29 Racing Wheel', 'shiftDown'))
        
        self._manualAutoToggle_idx = int(self._parser.get('G29 Racing Wheel', 'manualAutoToggle'))
	
        self._nextWeather_idx = int(self._parser.get('G29 Racing Wheel', 'nextWeather'))
        self._prevWeather_idx = int(self._parser.get('G29 Racing Wheel', 'prevWeather'))
	
        self._hudToggle_idx = int(self._parser.get('G29 Racing Wheel', 'hudToggle'))
	
        
    def parse_events(self, world, clock, args):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.JOYBUTTONDOWN:
                # if event.button == 1:
                #     world.hud.toggle_info()
                # elif event.button == 2:
                #     world.camera_manager.toggle_camera()
                # elif event.button == 3:
                #     world.next_weather()
                if event.button == self._respawn_idx:
                    if world.player is not None:
                        transform = world.player.get_transform()
                        transform.location.z += 2
                        transform.rotation.roll = 0
                        transform.rotation.pitch = 0
                        world.player.set_transform(transform)
                elif event.button == self._reverse_idx:
                    self._control.gear = 1 if self._control.reverse else -1
                elif event.button == self._handbrake_idx:
                    self._control.hand_brake
                elif event.button == self._nextVehicle_idx:
                    world.nextVehicle()
                elif event.button == self._prevVehicle_idx:
                    world.prevVehicle()
                elif event.button == self._shiftUp_idx:
                    self._control.gear = self._control.gear + 1
                elif event.button == self._shiftDown_idx:
                    self._control.gear = max(-1, self._control.gear - 1)
                elif event.button == self._manualAutoToggle_idx:
                    self._control.manual_gear_shift = not self._control.manual_gear_shift
                    self._control.gear = world.player.get_control().gear
                    world.hud.notification('%s Transmission' % ('Manual' if self._control.manual_gear_shift else 'Automatic'))
                elif event.button == self._nextWeather_idx:
                    world.next_weather()
                elif event.button == self._prevWeather_idx:
                    world.next_weather(reverse=True)
                elif event.button == self._hudToggle_idx:
                    world.hud.toggle_info()
                # elif event.button == 23:
                #     world.camera_manager.next_sensor()
            elif event.type == pygame.JOYHATMOTION:
                self._parse_camera(world)

            elif event.type == pygame.KEYUP:
                if self._is_quit_shortcut(event.key):
                    return True
                elif event.key == K_F1:
                    world.hud.toggle_info()
                elif event.key == K_h or (event.key == K_SLASH and pygame.key.get_mods() & KMOD_SHIFT):
                    world.hud.help.toggle()
                elif event.key == K_c:
                    world.camera_manager.toggle_camera()
                elif event.key == K_w and pygame.key.get_mods() & KMOD_SHIFT:
                    world.next_weather(reverse=True)
                elif event.key == K_w:
                    world.next_weather()
                elif event.key == K_BACKQUOTE:
                    world.camera_manager.next_sensor()
                elif event.key > K_0 and event.key <= K_9:
                    world.camera_manager.set_sensor(event.key - 1 - K_0)
                elif event.key == K_r:
                    world.camera_manager.toggle_recording()
                if isinstance(self._control, carla.VehicleControl):
                    if event.key == K_q:
                        self._control.gear = 1 if self._control.reverse else -1
                    elif event.key == K_m:
                        self._control.manual_gear_shift = not self._control.manual_gear_shift
                        self._control.gear = world.player.get_control().gear
                        world.hud.notification('%s Transmission' %
                                               ('Manual' if self._control.manual_gear_shift else 'Automatic'))
                    elif self._control.manual_gear_shift and event.key == K_COMMA:
                        self._control.gear = max(-1, self._control.gear - 1)
                    elif self._control.manual_gear_shift and event.key == K_PERIOD:
                        self._control.gear = self._control.gear + 1
                    elif event.key == K_p:
                        self._autopilot_enabled = not self._autopilot_enabled
                        world.player.set_autopilot(self._autopilot_enabled)
                        world.hud.notification('Autopilot %s' % ('On' if self._autopilot_enabled else 'Off'))

        if not self._autopilot_enabled:
            if isinstance(self._control, carla.VehicleControl):
                self._parse_vehicle_keys(pygame.key.get_pressed(), clock.get_time())
                self._parse_vehicle_wheel(world,args)
                self._parse_speedToWheel(world)
                self._control.reverse = self._control.gear < 0
            elif isinstance(self._control, carla.WalkerControl):
                self._parse_walker_keys(pygame.key.get_pressed(), clock.get_time())
            world.player.apply_control(self._control)

    def _parse_speedToWheel(self,world):
        # adjusts steering wheel autocenter using speed

        v = world.player.get_velocity()
        speed = (3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2))

        # speed limit that influences the autocenter
        S2W_THRESHOLD = 90
        if(speed > S2W_THRESHOLD):
            speed = S2W_THRESHOLD
        # autocenterCmd  \in [0,65535]
        autocenterCmd = 60000 * math.sin(speed/S2W_THRESHOLD)

        # send autocenterCmd to the steeringwheel
        self._evtdev.write(ecodes.EV_FF, ecodes.FF_AUTOCENTER, int(autocenterCmd))

    def _parse_vehicle_keys(self, keys, milliseconds):
        self._control.throttle = 1.0 if keys[K_UP] or keys[K_w] else 0.0
        steer_increment = 5e-4 * milliseconds
        if keys[K_LEFT] or keys[K_a]:
            self._steer_cache -= steer_increment
        elif keys[K_RIGHT] or keys[K_d]:
            self._steer_cache += steer_increment
        else:
            self._steer_cache = 0.0
        self._steer_cache = min(0.7, max(-0.7, self._steer_cache))
        self._control.steer = round(self._steer_cache, 1)
        self._control.brake = 1.0 if keys[K_DOWN] or keys[K_s] else 0.0
        self._control.hand_brake = keys[K_SPACE]


    def _parse_camera(self,world):
        jsInputs = [item for item in self._joystick.get_hat(0)]

        # Custom function to limit
        # pad to interval [-1, 1]
        hPos = jsInputs[0]
        vPos = jsInputs[1]
        world.camera_manager.toggle_camera(horizPos=hPos, vertiPos=vPos)

    def _parse_vehicle_wheel(self, world, args):
        numAxes = self._joystick.get_numaxes()
        jsInputs = [float(self._joystick.get_axis(i)) for i in range(numAxes)]
        jsButtons = [float(self._joystick.get_button(i)) for i in
                     range(self._joystick.get_numbuttons())]

        # Custom function to map range of inputs [1, -1] to outputs [0, 1] i.e 1 from inputs means nothing is pressed
        # For the steering, it seems fine as it is
        K1 = 1.0  # 0.55

        # limiting wheel rotation to +/- 0.65
        steerPos = jsInputs[self._steer_idx]
        if (steerPos > .65): steerPos = .65
        if (steerPos < -.65): steerPos = -.65
        steerCmd = K1 * math.tan(1.1 * steerPos)


        K2 = 1.6  # 1.6

        v = world.player.get_velocity()
        speed = (3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2))

        if (jsInputs[self._throttle_idx] == 0.0 or speed > args.speed_limit ):
            throttleCmd = 0
        else:
            throttleCmd = K2 + (2.05 * math.log10(-0.7 * jsInputs[self._throttle_idx] + 1.4) - 1.2) / 0.92

        if throttleCmd <= 0:
            throttleCmd = 0
        elif throttleCmd > 1:
            throttleCmd = 1

        # v = world.player.get_velocity()
        # actual_v = (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2))
        # print("actual_v: " + str(actual_v))
        # if actual_v > 10:
        #     throttleCmd = 0

        if (jsInputs[self._brake_idx] == 0.0):
            brakeCmd = 0
        else:
            brakeCmd = 1.6 + (2.05 * math.log10(-0.7 * jsInputs[self._brake_idx] + 1.4) - 1.2) / 0.92

        if brakeCmd <= 0:
            brakeCmd = 0
        elif brakeCmd > 1:
            brakeCmd = 1

        self._control.steer = steerCmd
        self._control.brake = brakeCmd
        self._control.throttle = throttleCmd

        #toggle = jsButtons[self._reverse_idx]

        self._control.hand_brake = bool(jsButtons[self._handbrake_idx])

    def _parse_walker_keys(self, keys, milliseconds):
        self._control.speed = 0.0
        if keys[K_DOWN] or keys[K_s]:
            self._control.speed = 0.0
        if keys[K_LEFT] or keys[K_a]:
            self._control.speed = .01
            self._rotation.yaw -= 0.08 * milliseconds
        if keys[K_RIGHT] or keys[K_d]:
            self._control.speed = .01
            self._rotation.yaw += 0.08 * milliseconds
        if keys[K_UP] or keys[K_w]:
            self._control.speed = 5.556 if pygame.key.get_mods() & KMOD_SHIFT else 2.778
        self._control.jump = keys[K_SPACE]
        self._rotation.yaw = round(self._rotation.yaw, 1)
        self._control.direction = self._rotation.get_forward_vector()

    @staticmethod
    def _is_quit_shortcut(key):
        return (key == K_ESCAPE) or (key == K_q and pygame.key.get_mods() & KMOD_CTRL)


# ==============================================================================
# -- HUD -----------------------------------------------------------------------
# ==============================================================================


class HUD(object):
    def __init__(self, width, height):
        self.dim = (width, height)
        self.display = None
        pygame.mouse.set_pos(width, height)
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        fonts = [x for x in pygame.font.get_fonts() if 'mono' in x]
        default_font = 'ubuntumono'
        if len(fonts) == 0:
            fonts = [pygame.font.get_fonts()]
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)
        self._font_mono = pygame.font.Font(mono, 20)
        self._notifications = textHUD(font, width, height)
        self._image = FadingImage(font, width, height)
        self.help = HelpText(pygame.font.Font(mono, 24), width, height)

        self.server_fps = 0
        self.frame_number = 0
        self.simulation_time = 0
        self._show_info = True
        self._info_text = []
        self._server_clock = pygame.time.Clock()

    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame_number = timestamp.frame_count


    def tick(self, world, clock):
        self._notifications.tick(world, clock)

        t = world.player.get_transform()
        v = world.player.get_velocity()
        c = world.player.get_control()
        
        #p = world.player.get_physics_control()

        # TODO: proper simulation
        # It is still unclear to me how the gears are modeled in CARLA:
        #   -1 reverse
        #   0  neutral
        # But how does this map to the gear ratios?
        #engine_rpm = p.max_rpm * c.throttle
        #if c.gear > 0:
        #    gear = p.forward_gears[c.gear]
        #    engine_rpm *= gear.ratio

        if isinstance(c, carla.VehicleControl):
            if c.reverse:
                self.notification("      REVERSE MODE", seconds=0.1)
            #     self._image.set_image(pygame.image.load('utils/images/r_icon.png').convert(),seconds=1)
            #     self._image.tick(world, clock)
            # else:
            #     self._image.set_image(None)


        if not self._show_info:
            return
        heading = 'N' if abs(t.rotation.yaw) < 89.5 else ''
        heading += 'S' if abs(t.rotation.yaw) > 90.5 else ''
        heading += 'E' if 179.5 > t.rotation.yaw > 0.5 else ''
        heading += 'W' if -0.5 > t.rotation.yaw > -179.5 else ''
        colhist = world.collision_sensor.get_collision_history()
        collision = [colhist[x + self.frame_number - 200] for x in range(0, 200)]
        max_col = max(1.0, max(collision))
        collision = [x / max_col for x in collision]
        vehicles = world.world.get_actors().filter('vehicle.*')
        self._info_text = [
            # 'Server:  % 6.0f FPS' % self.server_fps,
            # 'Client:  % 6.0f FPS' % clock.get_fps(),
            # '',
            # 'Vehicle: % 20s' % get_actor_display_name(world.player, truncate=20),
            # 'Map:     % 20s' % world.map.name,
            # 'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
            # '',
            'Speed:   % 6.0f km/h' % (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)),
            # u'Heading:% 16.0f\N{DEGREE SIGN} % 2s' % (t.rotation.yaw, heading),
            # 'Location:% 20s' % ('(% 5.1f, % 5.1f)' % (t.location.x, t.location.y)),
            # 'GNSS:% 24s' % ('(% 2.6f, % 3.6f)' % (world.gnss_sensor.lat, world.gnss_sensor.lon)),
            # 'Height:  % 18.0f m' % t.location.z,
            '']
        if isinstance(c, carla.VehicleControl):
            self._info_text += [
                ('Throttle:  ', c.throttle, 0.0, 1.0),
                ('Steer:  ', c.steer, -1.0, 1.0),
                ('Brake:  ', c.brake, 0.0, 1.0),
                ('Reverse:', c.reverse),
                ('HBrake:', c.hand_brake),
                ('Manual:', c.manual_gear_shift),
               # ('RPM:  % 6.0f' % engine_rpm),
                'Gear:   %s' % {-1: 'R', 0: 'N'}.get(c.gear, c.gear),
                '']
        elif isinstance(c, carla.WalkerControl):
            self._info_text += [
                ('Speed:', c.speed, 0.0, 5.556),
                ('Jump:', c.jump)]
        self._info_text += [
            # '',
            # '',
#            'Time Left: ' + str(math.ceil(ScenarioTimer.timeLeft)) + ' seconds',
#            "Completed Route: " + str(math.floor(ScenarioInfo.routePercentageCompleted)) + "%",
            # '',
            # '',
            # 'Collision Sensor:',
            # collision,
            # '',
            # '',
            # 'Number of vehicles: % 8d' % len(vehicles),
            '']
        # image = pygame.image.load('utils/images/UniOfLeicester.png').convert()
        # scale = .35
        # rect = (
        #     int(self.dim[0]*scale),
        #     int(
        #         self.dim[0]*scale*image.get_height()/
        #         image.get_width()
        #     )
        # )
        # image = pygame.transform.scale(image, rect)
        # image.set_alpha(100)
        # self._image.set_image(image, seconds=2)

    # if len(vehicles) > 1:
            # self._info_text += ['Nearby vehicles:']
            # distance = lambda l: math.sqrt((l.x - t.location.x)**2 + (l.y - t.location.y)**2 + (l.z - t.location.z)**2)
            # vehicles = [(distance(x.get_location()), x) for x in vehicles if x.id != world.player.id]
            # for d, vehicle in sorted(vehicles):
            #     if d > 200.0:
            #         break
            #     vehicle_type = get_actor_display_name(vehicle, truncate=22)
            #     self._info_text.append('% 4dm %s' % (d, vehicle_type))

    def toggle_info(self):
        self._show_info = not self._show_info

    def notification(self, text, seconds=2.0):
        self._notifications.set_text(text, seconds=seconds)

    def notification_image(self, image, seconds=2.0):
        self._image.set_image(image, seconds=seconds)


    def error(self, text):
        self._notifications.set_text('Error: %s' % text, (255, 0, 0))

    def render(self, display):

        # image = pygame.image.load('utils/images/UniOfLeicester.png').convert()
        # scale = .35
        # rect = (
        #     int(self.dim[0]*scale),
        #     int(
        #         self.dim[0]*scale*image.get_height()/
        #         image.get_width()
        #     )
        # )
        # image = pygame.transform.scale(image, rect)
        # image.set_alpha(100)
        # display.blit(image, (self.dim[0]-image.get_width()-5,5))
        if self._show_info:
            # info_surface = pygame.Surface((220, self.dim[1]))
            info_surface = pygame.Surface((220, 300))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))
            v_offset = 4
            bar_h_offset = 100
            bar_width = 106
            for item in self._info_text:
                if v_offset + 18 > self.dim[1]:
                    break
                if isinstance(item, list):
                    if len(item) > 1:
                        points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                        pygame.draw.lines(display, (255, 136, 0), False, points, 2)
                    item = None
                    v_offset += 18
                elif isinstance(item, tuple):
                    if isinstance(item[1], bool):
                        rect = pygame.Rect((bar_h_offset, v_offset + 8), (6, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect, 0 if item[1] else 1)
                    else:
                        rect_border = pygame.Rect((bar_h_offset, v_offset + 8), (bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect_border, 1)
                        f = (item[1] - item[2]) / (item[3] - item[2])
                        if item[2] < 0.0:
                            rect = pygame.Rect((bar_h_offset + f * (bar_width - 6), v_offset + 8), (6, 6))
                        else:
                            rect = pygame.Rect((bar_h_offset, v_offset + 8), (f * bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect)
                    item = item[0]
                if item:  # At this point has to be a str.
                    surface = self._font_mono.render(item, True, (255, 255, 255))
                    display.blit(surface, (8, v_offset))
                v_offset += 18
        self._notifications.render(display)
        self._image.render(display)
        self.help.render(display)


# ==============================================================================
# -- FadingText ----------------------------------------------------------------
# ==============================================================================


class FadingText(object):
    def __init__(self, font, dim, pos):
        self.font = font
        self.dim = dim
        self.pos = pos
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)

    def set_text(self, text, color=(255, 255, 255), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))

    def tick(self, _, clock):
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(500.0 * self.seconds_left)

    def render(self, display):
        display.blit(self.surface, self.pos)


# ==============================================================================
# -- HelpText ------------------------------------------------------------------
# ==============================================================================


class HelpText(object):
    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self.dim = (680, len(lines) * 22 + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * 22))
            self._render = False
        self.surface.set_alpha(220)

    def toggle(self):
        self._render = not self._render

    def render(self, display):
        if self._render:
            display.blit(self.surface, self.pos)


# ==============================================================================
# -- textHUD ------------------------------------------------------------------
# ==============================================================================

class textHUD(object):
    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self.dim = (250, len(lines) * 4 + 12)
        self.pos = (0.52 * width - 0.5 * self.dim[0], 0.15 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * 22))
            self._render = False
        self.surface.set_alpha(150)

    def set_text(self, text, color=(255, 255, 255), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))

    def tick(self, _, clock):
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(300.0 * self.seconds_left)

    def render(self, display):
        display.blit(self.surface, self.pos)

# ==============================================================================
# -- FadingImage ------------------------------------------------------------------
# ==============================================================================


class FadingImage(object):
    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self._screen_res = [width, height]
        self.dim = (680, len(lines) * 22 + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self._image = None

    def set_image(self, image, seconds=2.0):
        self._image = image
        if self._image is not None:
            x_centered = self._screen_res[0] / 2 - self._image.get_width() / 2
            y_centered = self._screen_res[1] / 2 - self._image.get_height() / 2
            self.pos = (x_centered, y_centered)
            self.seconds_left = seconds


    def tick(self, _, clock):
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        if self._image is not None:
            self._image.set_alpha(500.0 * self.seconds_left)

    def render(self, display):
        if self._image is not None:
            display.blit(self._image, self.pos)



# ==============================================================================
# -- CollisionSensor -----------------------------------------------------------
# ==============================================================================


class CollisionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.history = []
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: CollisionSensor._on_collision(weak_self, event))


    def get_collision_history(self):
        history = collections.defaultdict(int)
        for frame, intensity in self.history:
            history[frame] += intensity
        return history

    @staticmethod
    def _on_collision(weak_self, event):
        self = weak_self()
        if not self:
            return
        actor_type = get_actor_display_name(event.other_actor)
        # self.hud.notification('Collision with %r' % actor_type)
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x**2 + impulse.y**2 + impulse.z**2)
        self.history.append((event.frame_number, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)


# ==============================================================================
# -- LaneInvasionSensor --------------------------------------------------------
# ==============================================================================


class LaneInvasionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.lane_invasion')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: LaneInvasionSensor._on_invasion(weak_self, event))

    @staticmethod
    def _on_invasion(weak_self, event):
        self = weak_self()
        if not self:
            return
        lane_types = set(x.type for x in event.crossed_lane_markings)
        text = ['%r' % str(x).split()[-1] for x in lane_types]
        # self.hud.notification('Crossed line %s' % ' and '.join(text))

# ==============================================================================
# -- GnssSensor --------------------------------------------------------
# ==============================================================================


class GnssSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.lat = 0.0
        self.lon = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.gnss')
        self.sensor = world.spawn_actor(bp, carla.Transform(carla.Location(x=1.0, z=2.8)), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: GnssSensor._on_gnss_event(weak_self, event))

    @staticmethod
    def _on_gnss_event(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.lat = event.latitude
        self.lon = event.longitude


# ==============================================================================
# -- CameraManager -------------------------------------------------------------
# ==============================================================================


class CameraManager(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.surface = None
        self._parent = parent_actor
        self.hud = hud
        self.recording = False
        self._camera_transforms = [
            carla.Transform(carla.Location(x=0.15, y=-0.30, z=1.25)),
            carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15)),
            carla.Transform(carla.Location(x=0.150, y=-0.30, z=1.25), carla.Rotation(yaw=-55)),
            carla.Transform(carla.Location(x=0.150, y=-0.30, z=1.25), carla.Rotation(yaw=55)),
            carla.Transform(carla.Location(x=0.150, y=0, z=1.25), carla.Rotation(yaw=180))
            # carla.Transform(carla.Location(x=1.6, z=1.7)),
            # carla.Transform(carla.Location(x=0.150, y= -0.30, z=1.25), carla.Rotation(pitch=-5)),
            # carla.Transform(carla.Location(x=-1.6, z=1.7))
        ]
        self.transform_index = 1
        self.sensors = [
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB']

            # Removing the other cameras improves performance. Allows for 1080p resolution.

            #['sensor.camera.depth', cc.Raw, 'Camera Depth (Raw)'],
            #['sensor.camera.depth', cc.Depth, 'Camera Depth (Gray Scale)'],
            #['sensor.camera.depth', cc.LogarithmicDepth, 'Camera Depth (Logarithmic Gray Scale)'],
            #['sensor.camera.semantic_segmentation', cc.Raw, 'Camera Semantic Segmentation (Raw)'],
            #['sensor.camera.semantic_segmentation', cc.CityScapesPalette,
            #    'Camera Semantic Segmentation (CityScapes Palette)'],
            #['sensor.lidar.ray_cast', None, 'Lidar (Ray-Cast)']
            ]
        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()
        for item in self.sensors:
            bp = bp_library.find(item[0])
            if item[0].startswith('sensor.camera'):
                bp.set_attribute('image_size_x', str(hud.dim[0]))
                bp.set_attribute('image_size_y', str(hud.dim[1]))
                bp.set_attribute('fov', '110')
            elif item[0].startswith('sensor.lidar'):
                bp.set_attribute('range', '5000')
            item.append(bp)
        self.index = None

    def toggle_camera(self, horizPos=None, vertiPos=None):
        
        if horizPos is None and vertiPos is None:
            self.transform_index = (self.transform_index + 1) % 2
            self.sensor.set_transform(self._camera_transforms[self.transform_index])
        else:
            if horizPos < -.5:
                self.sensor.set_transform(self._camera_transforms[2])
            elif horizPos > .5:
                self.sensor.set_transform(self._camera_transforms[3])
            elif vertiPos > .5:
                self.transform_index = (self.transform_index + 1) % 2
                self.sensor.set_transform(self._camera_transforms[self.transform_index])
                
                #self.sensor.set_transform(self._camera_transforms[4])
            elif vertiPos < -.5:
              
                self.sensor.set_transform(self._camera_transforms[4])
            else:
                self.sensor.set_transform(self._camera_transforms[self.transform_index])

    def set_sensor(self, index, notify=True):
        index = index % len(self.sensors)
        needs_respawn = True if self.index is None \
            else self.sensors[index][0] != self.sensors[self.index][0]
        if needs_respawn:
            if self.sensor is not None:
                self.sensor.destroy()
                self.surface = None
            self.sensor = self._parent.get_world().spawn_actor(
                self.sensors[index][-1],
                self._camera_transforms[self.transform_index],
                attach_to=self._parent)
            # We need to pass the lambda a weak reference to self to avoid
            # circular reference.
            weak_self = weakref.ref(self)
            self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
        if notify:
            self.hud.notification(self.sensors[index][2])
        self.index = index

    def next_sensor(self):
        self.set_sensor(self.index + 1)

    def toggle_recording(self):
        self.recording = not self.recording
        self.hud.notification('Recording %s' % ('On' if self.recording else 'Off'))

    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))

    @staticmethod
    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        if self.sensors[self.index][0].startswith('sensor.lidar'):
            points = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 3), 3))
            lidar_data = np.array(points[:, :2])
            lidar_data *= min(self.hud.dim) / 100.0
            lidar_data += (0.5 * self.hud.dim[0], 0.5 * self.hud.dim[1])
            lidar_data = np.fabs(lidar_data) # pylint: disable=E1111
            lidar_data = lidar_data.astype(np.int32)
            lidar_data = np.reshape(lidar_data, (-1, 2))
            lidar_img_size = (self.hud.dim[0], self.hud.dim[1], 3)
            lidar_img = np.zeros(lidar_img_size)
            lidar_img[tuple(lidar_data.T)] = (255, 255, 255)
            self.surface = pygame.surfarray.make_surface(lidar_img)
        else:
            image.convert(self.sensors[self.index][1])
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        if self.recording:
            image.save_to_disk('_out/%08d' % image.frame_number)


# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================


def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None
    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(2.0)

        _failed = True
        num_of_attempts = 0
        while _failed:
            try:
                client = carla.Client(args.host, int(args.port))
                client.set_timeout(2.0)
                client.get_world()
                _failed = False
            except Exception as err:
                # print(err)
                num_of_attempts+=1
                print("Attempting to connect to carla: Test {}".format(num_of_attempts))
                time.sleep(1)
                continue

        print("Connected to CARLA server!")

        SCREEN_MODE = pygame.HWSURFACE | pygame.DOUBLEBUF
        if(args.fullscreen):
            SCREEN_MODE = pygame.FULLSCREEN

        display = pygame.display.set_mode(
            (args.width, args.height),
            SCREEN_MODE)

        hud = HUD(args.width, args.height)
        world = World(client.get_world(), hud, args.filter,args)
        controller = DualControl(world, args.autopilot)

        clock = pygame.time.Clock()

        while True:
            clock.tick_busy_loop(60)
            ##GameTime.get_time() - self._start_time
            if controller.parse_events(world, clock, args):
                break
            if not world.tick(clock):
                break
            world.render(display)
            pygame.display.flip()
            ego = world.player
            # print("<waypoint  x=\"{}\" y=\"{}\" z=\"{}\" connection=\"RoadOption.LANEFOLLOW\"/>".format(ego.get_location().x, ego.get_location().y, ego.get_location().z))
            # for event in pygame.event.get():
            #     if event.type == pygame.KEYDOWN and event.key == K_KP_ENTER:
            #         ego = world.player
            #         print("<waypoint  x=\"{}\" y=\"{}\" z=\"{}\" connection=\"RoadOption.LANEFOLLOW\"/>".format(ego.get_location().x, ego.get_location().y, ego.get_location().z))


    finally:
        #if world is not None:
            #world.destroy()

        pygame.quit()


# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Manual Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
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
        '-a', '--autopilot',
        action='store_true',
        help='enable autopilot')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='1920x1080',
        help='window resolution (default: 1920x1080)')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.*',
        help='actor filter (default: "vehicle.*")')
    argparser.add_argument(
        '--fullscreen',
        action='store_true',
        help='enable fullscreen mode')
    argparser.add_argument(
        '--follow_vehicle',
        default="TFHRC-MANUAL-1",
        help='Vehicle to be used for the follow cam (default: "TFHRC-MANUAL-1"')
    argparser.add_argument(
        '-s', '--speed_limit',
        metavar='S',
        default=50,
        type=int,
        help='Speed limit for manual vehicle in kph (default: 50 kph)')
    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    print(__doc__)

    try:

        game_loop(args)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':

    main()
