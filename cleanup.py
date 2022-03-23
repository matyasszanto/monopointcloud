#!/usr/bin/env python


import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
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

    # retrieve world
    world = client.get_world()

    for actor in world.get_actors():
        if actor.type_id == "vehicle.tesla.model3":
            actor.destroy()


if __name__ == '__main__':
    main()
