### Sourcing

In root folder in Docker Container you should run:

```bash
source ./install/setup.bash
```

### Cameras

Cameras with all their calibration and ids are stored in `cameras.yml`.

Update calibration data for a camera in cameras.yml

```bash
python3 src/get_camera_intrinsics.py --camera <camera_name>
```

Run the camera nodes from cameras.yml

```bash
ros2 launch src/multi_camera_launch.py
```





Useful commands:
```bash

sudo apt update
sudo apt upgrade -y

# If can't find packages, configure sudo
# https://wiki.ros.org/Installation/Ubuntu/Sources

sudo apt install ros-humble-librealsense2*
sudo apt install ros-humble-realsense2-*

ros2 topic list -v

# ros2 launch realsense2_camera rs_launch.py
# sets color resolution to 1280x720 at 15 fps and depth resolution to 1280x720 at 5 fps
ros2 launch realsense2_camera rs_launch.py rgb_camera.color_profile:=1280x720x15 depth_module.depth_profile:=1280x720x5

roslaunch realsense2_camera rs_camera.launch camera:=cam_1 serial_no:=108222250719
roslaunch realsense2_camera rs_camera.launch camera:=cam_2 serial_no:=105322250885

```

## Running detect_and_pick.py
If you encounter errors running detect_and_pick.py or other functions, these commands might help:
```bash
pip install roboticstoolbox-python
pip uninstall numpy
pip install numpy==1.24.3

# then you might need to comment the following line in File "/home/imitlearn/.local/lib/python3.10/site-packages/roboticstoolbox/mobile/EKF.py":

# from scipy import integrate, randn

### To push on this pc:

```bash

# If there is no key added yet
ssh-keygen -t ed25519 -C "borysole@fel.cvut.cz"

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh -T git@gitlab.ciirc.cvut.cz
```

And then to *git push*.

### Commands for panda py server:
```bash
ping 192.168.89.140

crow_robot_server
```