#!/usr/bin/env python


import glob
import os
import sys

try:
    sys.path.append(glob.glob('/opt/carla-simulator/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


def main():

    # connect to client
    client = carla.Client('localhost', 2000)
    client.set_timeout(20.0)

    # restart map
    world = client.get_world()
    current_map = str(world.get_map())
    current_map = current_map[current_map.find("=")+1:-1]
    client.load_world(current_map)

    """# retrieve world
    world = client.get_world()

    # setup counter
    actors_destroyed = 0

    # cleanup tesla model 3's and cameras
    for actor in world.get_actors():
        if actor.type_id == "vehicle.tesla.model3" or actor.type_id == "sensor.camera.rgb" or \
                actor.type_id == "sensor.camera.depth":
            actor.destroy()
            actors_destroyed += 1
            print(f"actors destroyed: {actors_destroyed}")

    print(f"Done! Total number of actors destroyed: {actors_destroyed}")
    """

if __name__ == '__main__':
    main()
