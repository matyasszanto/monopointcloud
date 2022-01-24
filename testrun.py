#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

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


def main():
    actor_list = []

    # create directory for exported images
    current_time = datetime.now().strftime("%H_%M_%S")
    os.makedirs(f"_out/{current_time}")

    try:
        # First of all, we need to create the client that will send the requests
        # to the simulator. Here we'll assume the simulator is accepting
        # requests in the localhost at port 2000.
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        # Once we have a client we can retrieve the world that is currently
        # running.
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

        # The world contains the list blueprints that we can use for adding new
        # actors into the simulation.
        blueprint_library = world.get_blueprint_library()

        # Now let's filter all the blueprints of type 'vehicle' and choose one
        # at random.
        bp = world.get_blueprint_library().find('vehicle.tesla.model3')

        # A blueprint contains the list of attributes that define a vehicle's
        # instance, we can read them and modify some of them. For instance,
        # let's randomize its color.
        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)

        # Now we need to give an initial transform to the vehicle. We choose a
        # random transform from the list of recommended spawn points of the map.
        transform = world.get_map().get_spawn_points()[0]

        # So let's tell the world to spawn the vehicle.
        vehicle = world.spawn_actor(bp, transform)

        # It is important to note that the actors we create won't be destroyed
        # unless we call their "destroy" function. If we fail to call "destroy"
        # they will stay in the simulation even after we quit the Python script.
        # For that reason, we are storing all the actors we create so we can
        # destroy them afterwards.
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

        # Now we register the function that will be called each time the sensor
        # receives an image. In this example we are saving the image to disk
        # converting the pixels to gray-scale.

        # cc = carla.ColorConverter.LogarithmicDepth
        # camera.listen(lambda image: image.save_to_disk(f'_out/{current_time}/%06d.png' % image.frame))
        #
        # print("let's wait 5 seconds")
        # time.sleep(5)


    finally:

        print('destroying actors')
        camera.destroy()
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('done.')


if __name__ == '__main__':

    main()
