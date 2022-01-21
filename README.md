# monopointcloud
A repository for the paper validating crowdsourced monocular pointcloud generation

## Setup remote server and local python client
To start a remote server for carla and start agent from local computer:
### On the remote machine
1. Install nvidia drivers on the server 
   1. For V100: https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/index.html
2. Set up ssh 
   1. `ssh-keygen -t rsa`
   2. `cd ~/.ssh`
   3. `cat id_rsa.pub`
   4. Copy the public id to the local computer's `authorized keys` file
3. `sudo apt-get install docker`
4. `sudo docker pull carlasim/carla:0.9.13`<br>
(Note: you can replace "0.9.13" with any other version, but make sure that the versions on the remote and local computers match)
5. `sudo docker run --privileged --gpus all --net=host -v /tmp/.X11-unix:/tmp/.X11-unix:rw carlasim/carla:0.9.13 /bin/bash ./CarlaUE4.sh -RenderOffScreen` <br>
(Note: replace 0.9.13 with the installed version)<br>
(Note: -RenderOffScreen starts the carla server in headless version)<br>
For further information see: https://carla.readthedocs.io/en/latest/build_docker/
6. `ssh -R 2000:localhost:2000 -R 2001:localhost:2001 -R 2002:localhost:2002 <user@local>`
### On the local machine
1. To install carla follow the steps described in: https://carla.readthedocs.io/en/latest/start_quickstart/#a-debian-carla-installation 
2. `cd /opt/carla-simulator/PythonAPI/examples/`
3. `python3 manual_control.py`
