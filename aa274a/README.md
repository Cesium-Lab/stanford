# AA274A

## Layout
`aa274a/` is the colcon workspace root. Packages live in `src/`.
```
aa274a/
    src/
        autonomy_repo/          # my ROS package
            CMakeLists.txt
            package.xml
            launch/
            rviz/
            scripts/            # ROS Python executables
    build/ install/ log/        # made by colcon (gitignored)
    hw1/ hw2/ hw3/ ...          # not ROS, colcon ignores them
```

## One-time setup (new machine)

### 1. Course libraries (asl_tb3_lib, asl_tb3_msgs, asl_tb3_examples, asl_tb3_sim)
Install them to `~/.local/asl_tb3` so you don't need a separate `tb_ws` workspace.
Builds without `--symlink-install` so the clone can be deleted afterwards.
`asl_tb3_sim` is needed for its `rviz.launch.py`, which my launch files include.
```bash
source /opt/ros/humble/setup.bash
git clone https://github.com/StanfordASL/asl-tb3-utils /tmp/asl_ws/src/asl-tb3-utils
cd /tmp/asl_ws
colcon build --packages-up-to asl_tb3_lib asl_tb3_examples asl_tb3_sim \
    --install-base ~/.local/asl_tb3 --merge-install
cd ~ && rm -rf /tmp/asl_ws
```
To update later: run the same commands again.

### 2. `~/.bashrc`
```bash
source /opt/ros/humble/setup.bash
source $HOME/.local/asl_tb3/local_setup.bash
```
Open a new terminal after editing it.

### 3. numpy fix
ROS Humble / Ubuntu's matplotlib are built for numpy 1.x. A pip numpy 2 in `~/.local`
shadows it and breaks `import matplotlib` (`_ARRAY_API not found`).
```bash
pip install --user "numpy<2" "opencv-python<4.11"
python3 -c "import numpy, matplotlib; print(numpy.__version__)"   # should print 1.x
```
Note: `asl_tb3_lib` / `rclpy` are NOT pip packages. Don't put them in `requirements.txt`.

### 4. VS Code / Pylance
`.vscode/settings.json` at the repo root points Pylance at the ROS + asl_tb3 paths
(`python.analysis.extraPaths`). For the Run button / debugger / Jupyter to see ROS,
launch VS Code from a terminal: `code .`

## Creating a package
Run from the **`src/`** folder (running from `aa274a/` nests packages wrong):
```bash
cd aa274a/src
ros2 pkg create --build-type ament_cmake autonomy_repo
```

## Coding
Python executables go in `scripts/`. First line (WITH the pound sign):
```python
#!/usr/bin/env python3
```
```bash
chmod +x scripts/[file]
```

Add every script to `CMakeLists.txt` (including helper modules like `a_star.py`
that other scripts import, or the import fails at runtime):
```cmake
install(PROGRAMS
    scripts/a_star.py
    scripts/navigator.py
    DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch rviz
        DESTINATION share/${PROJECT_NAME})
```
Scripts get installed flat: `scripts/oldish/foo.py` runs as `foo.py`
(so launch files use `executable="foo.py"`, not `"oldish/foo.py"`).

Add dependencies to `package.xml`:
```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
<exec_depend>geometry_msgs</exec_depend>
<exec_depend>asl_tb3_lib</exec_depend>
<exec_depend>asl_tb3_msgs</exec_depend>
```

## Building
From `aa274a/`:
```bash
colcon build --symlink-install
# OR, if CMake acts stale
colcon build --symlink-install --cmake-clean-cache
# full reset
rm -rf build install log
```
With `--symlink-install`, editing an existing script doesn't need a rebuild.
Adding a new script or changing `CMakeLists.txt`/`package.xml` does.

## Running
After every build (in each terminal):
```bash
source install/setup.bash
```
```bash
ros2 run autonomy_repo <script_file>          # e.g. navigator.py
ros2 launch autonomy_repo <launch_file>       # e.g. navigator.launch.py
```
```bash
ros2 launch asl_tb3_sim root.launch.py        # Gazebo sim: also needs ros_gz + asl_tb3_driver (not installed)

ros2 launch autonomy_repo heading_control.launch.py
ros2 launch autonomy_repo perception_controller.launch.py
ros2 launch autonomy_repo navigator.launch.py
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
					scripts/             # ROS Python executables
						camera_node.py     # Camera node code
						detection_node.py  # Detection node code

```
