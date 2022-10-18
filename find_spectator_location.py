#!/usr/bin/env python

# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys
import time
import numpy as np

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
            'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    except IndexError:
        pass

# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================


import carla

_HOST_ = '127.0.0.1'
_PORT_ = 2000
_SLEEP_TIME_ = 1


def get_closest_spawn_point(sps, x, y):

    # search through it by x
    x_candidates = np.ones((10, 2))
    x_candidates[:, 1] = np.Inf

    for i, sp in enumerate(sps):
        sp_x = sp.location.x
        if abs(sp_x - x) < max(x_candidates[:, 1]):
            x_candidates[np.argmax(x_candidates[:, 1])] = np.array([i, abs(sp_x - x)])

    i_closest_spawn_point = 0

    y_diff_min = np.Inf
    for j, i_candidate in enumerate(x_candidates[:, 0]):
        sp_y_diff = abs(sps[int(i_candidate)].location.y - y)
        if sp_y_diff < y_diff_min:
            i_closest_spawn_point = int(x_candidates[j, 0])
            y_diff_min = sp_y_diff

    return i_closest_spawn_point


def main():
    client = carla.Client(_HOST_, _PORT_)
    client.set_timeout(2.0)
    world = client.get_world()
    spawn_points = world.get_map().get_spawn_points()

    # print(help(t))
    # print("(x,y,z) = ({},{},{})".format(t.location.x, t.location.y,t.location.z))

    while True:
        t = world.get_spectator().get_transform()
        # coordinate_str = "(x,y) = ({},{})".format(t.location.x, t.location.y)
        coordinate_str = f"(x,y,z) = ({t.location.x},{t.location.y},{t.location.z})"
        rotation_str = f"(pitch, yaw, roll) = ({t.rotation.pitch}, {t.rotation.yaw}, {t.rotation.roll})"
        # print(coordinate_str)
        # print(rotation_str)
        time.sleep(_SLEEP_TIME_)
        if len(spawn_points) > 0:
            best_sp_index = get_closest_spawn_point(sps=spawn_points, x=t.location.x, y=t.location.y)
            # print(f"Closest spawn point (x,y,z) =  {spawn_points[best_sp_index].location.x},"
            #       f" {spawn_points[best_sp_index].location.y} {spawn_points[best_sp_index].location.z}")
            print(f"Closest spawn point index: {best_sp_index}")


if __name__ == '__main__':
    main()
