#!/usr/bin/env python

"""
Test scenario:
Set up map, weather, sun (Town02, Clear, Noon)
Spawn vehicle (Tesla Model3) in random color
Spawn RGB camera
Activate autopilot
Record images for 5 seconds (runtime) from camera
Destroy actors
"""

import glob
import os
import sys
from datetime import datetime
import queue

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random
import time

class CarlaSyncMode(object):
    """
    Context manager to synchronize output from different sensors. Synchronous
    mode is enabled as long as we are inside this context

        with CarlaSyncMode(world, sensors) as sync_mode:
            while True:
                data = sync_mode.tick(timeout=1.0)

    """

    def __init__(self, world, *sensors, **kwargs):
        self.world = world
        self.sensors = sensors
        self.frame = None
        self.delta_seconds = 1.0 / kwargs.get('fps', 20)
        self.timestamp = datetime.now()
        self._queues = []
        self._settings = None

    def __enter__(self):
        self._settings = self.world.get_settings()
        self.frame = self.world.apply_settings(carla.WorldSettings(
            no_rendering_mode=False,
            synchronous_mode=True,
            fixed_delta_seconds=self.delta_seconds))

        def make_queue(register_event):
            q = queue.Queue()
            register_event(q.put)
            self._queues.append(q)

        make_queue(self.world.on_tick)
        for sensor in self.sensors:
            make_queue(sensor.listen)
        return self

    def tick(self, timeout):
        self.frame = self.world.tick()
        data = [self._retrieve_data(q, timeout) for q in self._queues]
        assert all(x.frame == self.frame for x in data)
        return data

    def __exit__(self, *args, **kwargs):
        self.world.apply_settings(self._settings)

    def _retrieve_data(self, sensor_queue, timeout):
        while True:
            data = sensor_queue.get(timeout=timeout)
            if data.frame == self.frame:
                return data


def main():
    actor_list = []

    try:
        # connect to client
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)

        # retrieve world
        world = client.get_world()

        """
        Setting up map and weather:
        Map: Town02
        Weather: clear
        Sun: noon
        """
        client.load_world('Town02')
        weather = world.get_weather()
        weather.sun_altitude_angle = 45
        weather.sun_azimuth_angle = 0
        clear_weather = [10.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0331]
        weather.cloudiness = clear_weather[0]
        weather.precipitation = clear_weather[1]
        weather.precipitation_deposits = clear_weather[2]
        weather.wind_intensity = clear_weather[3]
        weather.fog_density = clear_weather[4]
        weather.fog_distance = clear_weather[5]
        weather.fog_falloff = clear_weather[6]
        weather.wetness = clear_weather[7]
        weather.scattering_intensity = clear_weather[8]
        weather.mie_scattering_scale = clear_weather[9]
        weather.rayleigh_scattering_scale = clear_weather[10]

        # Setting up and spawning vehicle

        blueprint_library = world.get_blueprint_library()
        bp = world.get_blueprint_library().find('vehicle.tesla.model3')

        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)

        transform = world.get_map().get_spawn_points()[0]
        vehicle = world.spawn_actor(bp, transform)

        actor_list.append(vehicle)
        print('created %s' % vehicle.type_id)

        # Let's put the vehicle to drive around.
        vehicle.set_autopilot(True)

        # Let's add now an RGB camera attached to the vehicle. Note that the
        # transform we give here is now relative to the vehicle.
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        actor_list.append(camera)
        print('created %s' % camera.type_id)

        # create directory for exported images
        current_time = datetime.now().strftime("%H_%M_%S")
        os.makedirs(f"_out/{current_time}")

        # turn lights green
        for actor in world.get_actors():
            if actor.type_id == "traffic.traffic_light":
                actor.set_state(carla.TrafficLightState.Green)

        # instantiate CarlaSyncMode and start exporting images on ticks
        print(f"before instantiation: {world.get_settings().fixed_delta_seconds}")
        with CarlaSyncMode(world, camera, fps=30) as synchronizer:
            tick = 0
            print(f"after instantiation: {world.get_settings().fixed_delta_seconds}")
            while True:
                _, image = synchronizer.tick(timeout=2.0)
                image.save_to_disk(path=f'_out/{current_time}/{tick}.png')
                tick += 1
                if tick > 120:
                    break
                if tick % 20 == 0:
                    print(tick)

    finally:

        print('destroying actors')
        camera.destroy()
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('done.')
        elapsed_time = datetime.now() - synchronizer.timestamp
        print(f"Time elapsed: {elapsed_time}")


if __name__ == '__main__':

    main()
