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

import numpy

try:
    sys.path.append(glob.glob('/opt/carla-simulator/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    try:
        sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
            sys.version_info.major,
            sys.version_info.minor,
            'win-amd64' if os.name == 'nt' else 'linux-x86_64'
        ))[0])
    except IndexError:
        pass

import carla
import cv2 as cv
import numpy as np

import random
import time

import image_converter
import depth_treshold


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
        self.frame = self.world.apply_settings(carla.WorldSettings(no_rendering_mode=False,
                                                                   synchronous_mode=True,
                                                                   fixed_delta_seconds=self.delta_seconds,
                                                                   )
                                               )

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
    global client
    actor_list = []

    # set camera parameters
    im_height = 720
    im_width = 1280
    camera_fov = 120

    # set up number of runs per spawn position
    num_runs = 4

    # set up length of single run
    len_run = 110
    tick_to_start_recrding = 10

    # set map "Town03"
    map_string = "Town03"

    # get current time and make new dir
    current_time = datetime.now().strftime("%m_%d_%H_%M_%S")
    os.makedirs(f"_out/sequences/{current_time}")
    print(f"_out/sequences/{current_time}")

    try:
        # connect to client
        client = carla.Client('localhost', 2000)
        client.set_timeout(20.0)

        # retrieve world
        world = client.get_world()

        """
        Setting up map and weather:
        Map: Town03
        Weather: clear
        Sun: noon
        """

        # check if map setting is needed, and set it to Town03
        if str(world.get_map()) != "Map(name=Carla/Maps/Town03)":
            client.load_world(map_string)

        # set weather
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

        # rel_y = [-4, 0, 4]
        spawn_position = []

        # Adding spawn positions
        spawn_indices = [221,
                         220,
                         239,
                         240,
                         ]

        j = 0
        for spawn_position in spawn_indices:
            j += 1
            for i in range(num_runs):

                sensor_list = []

                # Setting up and spawning vehicle
                blueprint_library = world.get_blueprint_library()
                bp = world.get_blueprint_library().find('vehicle.tesla.model3')

                if bp.has_attribute('color'):
                    color = random.choice(bp.get_attribute('color').recommended_values)
                    bp.set_attribute('color', color)

                spawn_points = world.get_map().get_spawn_points()
                vehicle = world.spawn_actor(bp, spawn_points[spawn_position])

                actor_list.append(vehicle)
                print('created %s' % vehicle.type_id)

                time.sleep(1)
                # Let's put the vehicle to drive around.
                vehicle.set_autopilot(True)

                # set up an RGB camera
                camera_bp = blueprint_library.find('sensor.camera.rgb')

                # x-forward, y-right, z-up
                camera_y_rel = random.uniform(a=-2, b=2)
                camera_z_rel = 2.4 + random.uniform(a=-1, b=1)
                camera_transform = carla.Transform(carla.Location(x=1.5, y=camera_y_rel, z=camera_z_rel))

                # set camera resolution
                camera_bp.set_attribute("fov", f"{camera_fov}")
                camera_bp.set_attribute('image_size_x', f'{im_width}')
                camera_bp.set_attribute('image_size_y', f'{im_height}')

                # spawn camera and fix to vehicle
                camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
                actor_list.append(camera)
                sensor_list.append(camera)
                print(f'created {camera.type_id}')

                # create a depth camera at the same location
                depth_camera_bp = blueprint_library.find('sensor.camera.depth')

                depth_camera_bp.set_attribute("fov", f"{camera_fov}")
                depth_camera_bp.set_attribute('image_size_x', f'{im_width}')
                depth_camera_bp.set_attribute('image_size_y', f'{im_height}')

                depth_camera = world.spawn_actor(depth_camera_bp, camera_transform, attach_to=vehicle)
                actor_list.append(depth_camera)
                sensor_list.append(depth_camera)
                print(f'created {depth_camera.type_id}')

                # create a segmentation camera at the same location
                semseg_camera_bp = blueprint_library.find('sensor.camera.semantic_segmentation')

                semseg_camera_bp.set_attribute("fov", f"{camera_fov}")
                semseg_camera_bp.set_attribute('image_size_x', f'{im_width}')
                semseg_camera_bp.set_attribute('image_size_y', f'{im_height}')

                semseg_camera = world.spawn_actor(semseg_camera_bp, camera_transform, attach_to=vehicle)
                actor_list.append(semseg_camera)
                sensor_list.append(semseg_camera)
                print(f'created {semseg_camera.type_id}')

                # create directory for exported images
                export_basepath = f"_out/sequences/{current_time}/{j}_{i+1}"
                os.makedirs(export_basepath)

                # turn all traffic lights green
                for actor in world.get_actors():
                    if actor.type_id == "traffic.traffic_light":
                        actor.set_state(carla.TrafficLightState.Green)

                # create directories for image export
                os.makedirs(f'{export_basepath}/masked_rgb/')
                os.makedirs(f'{export_basepath}/depth')
                os.makedirs(f'{export_basepath}/rgb/')
                os.makedirs(f'{export_basepath}/semseg_masked/')
                os.makedirs(f'{export_basepath}/semseg/')

                camera_positions = []

                # instantiate CarlaSyncMode and start exporting images on ticks
                # print(f"before instantiation: {world.get_settings().fixed_delta_seconds}")
                with CarlaSyncMode(world, *sensor_list, fps=30) as synchronizer:
                    tick = 0
                    # print(f"after instantiation: {world.get_settings().fixed_delta_seconds}")

                    # print focal length to focal.txt
                    focal = im_width / (2 * np.tan(camera_fov * np.pi / 360))
                    np.savetxt(fname=f'{export_basepath}/focal.txt', X=np.array([focal]))

                    while True:
                        _, image, depth_as_rgb, semseg_raw = synchronizer.tick(timeout=2.0)

                        if tick < tick_to_start_recrding:
                            tick += 1
                            continue

                        # mask image with depth
                        depth = image_converter.depth_to_array(depth_as_rgb)
                        depth *= 255
                        depth_mask = depth_treshold.create_mask(depth)

                        depth_mat = image_converter.to_bgra_array(image)
                        masked_rgb = cv.bitwise_and(depth_mat, depth_mat, mask=depth_mask)

                        # export images
                        # depth
                        depth = image_converter.depth_to_logarithmic_grayscale(depth_as_rgb)
                        cv.imwrite(f'{export_basepath}/depth/{tick}_depth.png', depth)

                        # depth masked
                        cv.imwrite(f'{export_basepath}/masked_rgb/{tick}_masked.png', masked_rgb)

                        # rgb
                        image.save_to_disk(path=f'{export_basepath}/rgb/{tick}.png')

                        # semseg
                        semseg_orig = image_converter.labels_to_cityscapes_palette(semseg_raw)
                        semseg_mask = np.copy(semseg_orig)
                        semseg_mask[semseg_mask == 0] = np.Inf
                        semseg_mask[semseg_mask != np.Inf] = 0
                        semseg_mask[semseg_mask == np.Inf] = 1
                        semseg_mask_2 = np.stack((semseg_mask[:, :, 0],
                                                  semseg_mask[:, :, 0],
                                                  semseg_mask[:, :, 0],
                                                  semseg_mask[:, :, 0]),
                                                 axis=2,
                                                 )

                        final_masked_rgb = np.multiply(masked_rgb, semseg_mask_2)

                        cv.imwrite(f'{export_basepath}/semseg_masked/{tick}_semseg_masked.png', final_masked_rgb)
                        cv.imwrite(f'{export_basepath}/semseg/{tick}_semseg.png', semseg_orig)

                        camera_positions.append([camera.get_transform().location.x,
                                                 camera.get_transform().location.y,
                                                 camera.get_transform().location.z,
                                                 camera.get_transform().rotation.roll,
                                                 camera.get_transform().rotation.yaw,
                                                 camera.get_transform().rotation.pitch])

                        tick += 1

                        if tick > len_run - 1:
                            np.savetxt(fname=f'{export_basepath}/camera.txt', X=camera_positions)
                            break

                print('destroying actors')
                camera.destroy()
                depth_camera.destroy()
                client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
                print(f'Run {i+1} images exported to folder')

    except Exception as e:
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print(e)

    finally:
        elapsed_time = datetime.now() - synchronizer.timestamp
        print(f"Done. Total time elapsed: {elapsed_time}")


if __name__ == '__main__':
    main()
