```bash
rm -rf build install log
colcon build --symlink-install
# OR 
colcon build --symlink-install --cmake-clean-cache

source ./install/setup.bash
ros2 launch asl_tb3_sim root.launch.py


source ./install/setup.bash
ros2 launch autonomy_repo heading_control.launch.py

source ./install/setup.bash
ros2 run autonomy_repo p3_plot.py

```