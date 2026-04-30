[TOC]

# Limo Simulation Operation Process

## 1.	Introduction of Function Package

```
├── image
├── limo_description
├── limo_gazebo_sim
```

​	limo_description: The file is the function package of model file

​	limo_gazebo_sim: The folder is gazebo simulation function package

## 2.	Environment

### Development Environment

​	ubuntu 18.04 + [ROS Melodic desktop full](http://wiki.ros.org/melodic/Installation/Ubuntu)

### Download and install required function package

​	Download and install ros-control function package, ros-control is the robot control middleware provided by ROS

```
sudo apt-get install ros-melodic-ros-control
```

​	Download and install ros-controllers function package, ros-controllers are the kinematics plug-in of common models provided by ROS

```
sudo apt-get install ros-melodic-ros-controllers
```

​	Download and install gazebo-ros function package, gazebo-ros is the communication interface between gazebo and ROS, and connect the ROS and Gazebo

```
sudo apt-get install ros-melodic-gazebo-ros
```

​	Download and install gazebo-ros-control function package, gazebo-ros-control is the communication standard controller between ROS and Gazebo

```
sudo apt-get install ros-melodic-gazebo-ros-control
```

​	Download and install joint-state-publisher-gui package.This package is used to visualize the joint control.

```
sudo apt-get install ros-melodic-joint-state-publisher-gui 
```

​	Download and install rqt-robot-steering plug-in, rqt_robot_steering is a ROS tool closely related to robot motion control, it can send the control command of robot linear motion and steering motion, and the robot motion can be easily controlled through the sliding bar

```
sudo apt-get install ros-melodic-rqt-robot-steering 
```

## 3.	About Usage

### 1. Build

```bash
cd ~/myfile/robote_project/limo_ws
rosdep install --from-paths src --ignore-src -r -y
catkin_make
source devel/setup.bash
```

### 2. Start Gazebo

```bash
roslaunch limo_gazebo_sim limo_four_diff.launch
```

### 3. Run SLAM

Run one method at a time in a new terminal after sourcing `devel/setup.bash`.
Start Gazebo only once. Do not launch `gmapping`, `hector`, or `cartographer` with another world.
When one method is finished, stop it with `Ctrl+C`, then start the next method.
The mapping launch entry points are grouped in the new `limo_mapping` package.

On ROS Noetic, install the Hector backend first:

```bash
sudo apt-get install ros-noetic-hector-mapping
```

Gmapping:

```bash
roslaunch limo_mapping gmapping.launch
```

Hector SLAM:

```bash
roslaunch limo_mapping hector.launch
```

Cartographer:

On this workspace, the `cartographer.launch` entry falls back to the working `gmapping` backend because `cartographer_ros` is not installed for ROS Noetic.

```bash
roslaunch limo_mapping cartographer.launch
```

### 4. Drive the robot

Open a new terminal, source the workspace, keep the cursor in that terminal, then run:

```bash
rosrun limo_gazebo_sim keyboard_teleop.py
```

Keyboard control keys:

```text
u    move forward-left
i    move forward
o    move forward-right
j    turn left
k    stop
l    turn right
m    move backward-left
,    move backward
.    move backward-right
w    increase linear speed
s    decrease linear speed
a    increase angular speed
d    decrease angular speed
```

This keyboard controller is provided by `limo_gazebo_sim`, so you do not need a separate `teleop_twist_keyboard` terminal.

### 5. Save the result

Save generated map files into the workspace `map/` directory.

Gmapping or Hector:

```bash
mkdir -p ~/myfile/robote_project/limo_ws/map
rosrun map_server map_saver -f ~/myfile/robote_project/limo_ws/map/map
```

Cartographer:

```bash
rosservice call /write_state "{filename: '${HOME}/myfile/robote_project/limo_ws/map/map.pbstream'}"
rosrun cartographer_ros cartographer_pbstream_to_ros_map -map_filestem=${HOME}/myfile/robote_project/limo_ws/map/map -pbstream_filename=${HOME}/myfile/robote_project/limo_ws/map/map.pbstream -resolution=0.05
```

 

 
