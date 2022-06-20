# Importing individual maps
This readme contains information on how externally defined opendrive maps can be imported into Carla simulator.

## Requirements
1. Ubuntu 18.04 (_probably works on 20.04 as well, but not tested_)
2. Carla version must be ≥0.9.12
3. ~500GB free disk space
4. ≥12GB RAM
   1. Use swapping if available memory is not enough <br>
      (A great tutorial: https://www.youtube.com/watch?v=Tteiw6MY4QI)
   2. _Don't forget to undo any changes after you're done with docker generation (see below)_

## Steps
Follow the instructions given in https://carla.readthedocs.io/en/latest/tuto_M_add_map_package/ <br>
For the installation to work fine, you'll need to:
1. Register to Unreal at:<br>
https://www.unrealengine.com/en-US/
2. Connect Unreal to your GitHub account as described in:
https://www.epicgames.com/help/en-US/epic-accounts-c74/connect-accounts-c110/how-do-i-link-my-unreal-engine-account-with-my-github-account-a3618
3. Replace the downloaded Carla.dockerfile with the one in the docker_files directory.<br>Source:
https://github.com/carla-simulator/carla/issues/4862