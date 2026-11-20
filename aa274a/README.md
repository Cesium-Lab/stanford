# AA274A

## Layout
```
aa274a/                 # workspace root
    src/
        autonomy_repo/  # package
            launch/ rviz/ scripts/
```

## One-time setup
```bash
source /opt/ros/humble/setup.bash
git clone https://github.com/StanfordASL/asl-tb3-utils /tmp/asl_ws/src/asl-tb3-utils
cd /tmp/asl_ws
colcon build --packages-up-to asl_tb3_lib asl_tb3_examples asl_tb3_sim \
    --install-base ~/.local/asl_tb3 --merge-install
cd ~ && rm -rf /tmp/asl_ws
```
Add to `~/.bashrc`:
```bash
source /opt/ros/humble/setup.bash
source $HOME/.local/asl_tb3/local_setup.bash
```
If matplotlib crashes: `pip install --user "numpy<2" "opencv-python<4.11"`

For Pylance/Run button to see ROS, open VS Code from a terminal: `code .`

## Creating a package
```bash
cd aa274a/src
ros2 pkg create --build-type ament_cmake autonomy_repo
```

## Coding
```python
#!/usr/bin/env python3
```
```bash
chmod +x scripts/[file]
```
`CMakeLists.txt` (list every script, including imported helpers like `a_star.py`):
```cmake
install(PROGRAMS
    scripts/a_star.py
    scripts/navigator.py
    DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch rviz
        DESTINATION share/${PROJECT_NAME})
```
`package.xml`:
```xml
<exec_depend>asl_tb3_lib</exec_depend>
<exec_depend>asl_tb3_msgs</exec_depend>
<exec_depend>rclpy</exec_depend>
```

## Building
From `aa274a/`:
```bash
colcon build --symlink-install
rm -rf build install log   # full reset
```

## Running
```bash
source install/setup.bash

ros2 launch asl_tb3_sim root.launch.py

ros2 run autonomy_repo navigator.py
ros2 launch autonomy_repo navigator.launch.py

ros2 launch <name of package> <name of launch file>  # GENERICALLY WITH RVIZ2

ros2 launch autonomy_repo navigator.launch.py use_sim_time:=false  # no sim time


```

```bash
rviz2
rviz2 -d <path-to-rviz-config-file>

```

## Other commands from section

### Topics and Params
```bash
ros2 topic list
ros2 topic echo <topic_name>
ros2 topic pub /kill std_msgs/msg/Bool data:\ true -1
ros2 topic pub /detector_bool std_msgs/msg/Bool "{data: true}"

ros2 param list
ros2 param get <node_name> <parameter_name>
ros2 param set <node_name> <parameter_name> <value>
```

### Robot
```bash
# ssh into robot
echo $ROS_DOMAIN_ID
ssh aa274@<robot_name>.local

pkill -f "gz sim" 
pgrep -af "gz sim" # should print nothing 
ros2 launch asl_tb3_driver bringup.launch.py camera:=true
ros2 launch asl_tb3_driver test_detector.launch.py
```

### Special robot
```bash
# robot
ros2 run image_transport republish raw compressed \
  --ros-args --remap in:=/detector_image --remap out/compressed:=/detector_image_compressed

# laptop
ros2 run image_transport republish compressed raw \
  --ros-args --remap in/compressed:=/detector_image_compressed --remap out:=/detector_image_decompressed

ros2 topic hz /detector_image_decompressed
```


## Useful info from sheets
```bash
# Directory organization for a ROS Development Workspace

~/tb_ws/ 	# My group's workspace root directory
	 build/ 		# Compiled libraries
	 install/setup.bash # Source workspace packages  
	 src/ 			# Top-level package directory
			external_pkg1/  # Some external package that I am using
			external_pkg2/   # Another external package
			group4_repo/     # My group's autonomy repository
				navigation_pkg/    # My group's Navigation ROS Package
				perception_pkg/    # My group's Perception ROS Package
					CMakeLists.txt  # Build instructions
					package.xml     # ROS package details
					src/            # C++ Code lives here!
					my_pytorch_py_lib/   # My custom python module
					scripts/             # ROS Python executables
						camera_node.py     # Camera node code
						detection_node.py  # Detection node code

```
