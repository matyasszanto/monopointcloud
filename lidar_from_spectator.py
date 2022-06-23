import copy
import time
import carla
import numpy as np
import open3d as o3d

from im_seq_roundabout import CarlaSyncMode as syncer

_HOST_ = '127.0.0.1'
_PORT_ = 2000
_SLEEP_TIME_ = 1


def main():
    client = carla.Client(_HOST_, _PORT_)
    client.set_timeout(2.0)
    world = client.get_world()

    spectator = world.get_spectator()

    spectator.set_transform(carla.Transform(carla.Location(20, 0, 5), carla.Rotation(0, 180, 0)))

    blueprint_library = world.get_blueprint_library()

    # create lidar sensor higher up and with raycasting
    lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')

    # set attributes
    lidar_bp.set_attribute('range', f'{float(50)}')
    lidar_bp.set_attribute('upper_fov', f'{float(20)}')
    lidar_bp.set_attribute('lower_fov', f'{float(-30)}')
    lidar_bp.set_attribute('rotation_frequency', '30')
    lidar_bp.set_attribute('channels', '64')
    lidar_bp.set_attribute('points_per_second', '1000000')

    lidar_transform = carla.Transform(carla.Location(x=0,
                                                     y=0,
                                                     z=0,
                                                     ),
                                      carla.Rotation(0,
                                                     0,
                                                     0,
                                                     ),
                                      )

    lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=spectator)

    sensor_list = [lidar]

    print("lidar created!")

    number_of_records = 170

    full_pointcloud = o3d.geometry.PointCloud()

    with syncer(world, *sensor_list, fps=30) as sync:
        for i in range(number_of_records):
            try:
                time.sleep(0.1)
                if True:
                    lidar_output = sync.tick(timeout=2.0)[1]

                    locations = np.array([-spectator.get_location().x,
                                          -spectator.get_location().y,
                                          -spectator.get_location().z])

                    lidar_output.save_to_disk(f'_out/{i}.ply')

                    current_ply = o3d.io.read_point_cloud(f'_out/{i}.ply')
                    point_cloud_in_numpy = np.asarray(current_ply.points)
                    point_cloud_in_numpy += locations

                    current_ply.points = o3d.utility.Vector3dVector(point_cloud_in_numpy)

                    export_ply = copy.deepcopy(current_ply)

                    o3d.io.write_point_cloud(f'_out/{i}.ply', current_ply)

                    full_pointcloud += export_ply
            except:
                continue

        lidar.destroy()

        full_pointcloud_np = np.asarray(full_pointcloud.points)
        full_pointcloud_np[:, 1] *= -1
        full_pointcloud.points = o3d.utility.Vector3dVector(full_pointcloud_np)

        o3d.io.write_point_cloud("_out/pointcloud.pcd", full_pointcloud)
        o3d.visualization.draw_geometries([full_pointcloud])


if __name__ == '__main__':
    main()
