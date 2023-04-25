#!/bin/bash

carma exec
source /opt/carma/install_ros2/setup.bash; ros2 topic echo /localization/current_pose
