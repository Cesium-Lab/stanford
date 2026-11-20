## Useful commands
### Initing
Run this in the aa274a folder:
```bash
rm -rf build install log
# OR
rm -rf autonomy_repo

ros2 pkg create --build-type ament_cmake autonomy_repo # or whatever else
ros2 pkg create --build-type ament_cmake autonomy_repo --destination-directory .
```

Should already have `install/setup.bash` in `~/.bashrc`, but if not, run
```bash
source ./install/setup.bash
```

### Coding
```bash
# shebang (put WITH the pound sign)

#!/usr/bin/env python3

chmod +x [file]
```

Add to CMakeLists.txt (as an example with constant_control.py):
```bash
install(PROGRAMS
    scripts/constant_control.py
    DESTINATION lib/${PROJECT_NAME}
)
```

Add to package.xml

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
```

### Building
```bash
colcon build --symlink-install
# OR 
colcon build --symlink-install --cmake-clean-cache
```
### Running

```bash
source ./install/setup.bash # if not already
ros2 run <package_name> <script_file>
```

```bash
ros2 launch asl_tb3_sim root.launch.py


source ./install/setup.bash
ros2 launch autonomy_repo heading_control.launch.py

source ./install/setup.bash
ros2 run autonomy_repo p3_plot.py

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
					scripts/             # ROS Python Executables
						camera_node.py     # Camera node code
						detection_node.py  # Detection node code

```