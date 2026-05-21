# LAB10 实验报告

## 1. 实验名称

ROS 导航栈与路径规划实验（LAB10）

## 2. 实验目的

1. 学习 ROS 导航技术栈的基本组成与使用方法。
2. 理解静态地图、定位、全局规划、局部规划之间的关系。
3. 掌握 A*/Dijkstra 全局规划算法与 DWA、TEB 局部规划算法的基本思想。
4. 在 LIMO 仿真平台上完成建图、定位与导航功能联调。
5. 通过参数调整提高机器人对规划轨迹的跟踪效果。

## 3. 实验环境

- 操作系统：Ubuntu 20.04
- ROS 版本：ROS Noetic
- 仿真平台：Gazebo 11
- 机器人平台：LIMO 四轮差速仿真模型
- 工作区路径：`~/myfile/robote_project/limo_ws`

## 4. 实验原理

### 4.1 ROS 导航栈组成

本实验使用的导航流程主要由以下部分组成：

1. `map_server`
   
   负责加载保存好的静态地图，并发布 `/map`。

2. `amcl`
   
   负责在已知地图中进行粒子滤波定位，输出机器人在 `map` 坐标系中的位姿。

3. `move_base`
   
   导航核心节点，负责调用全局规划器与局部规划器生成机器人运动命令。

4. `global_costmap` 与 `local_costmap`
   
   负责构建全局代价地图和局部代价地图，用于障碍物建模与路径搜索。

5. 全局规划器
   
   根据起点和终点在静态地图上搜索一条可行路径。

6. 局部规划器
   
   在局部范围内结合机器人运动学约束和动态障碍信息，实时生成控制指令 `/cmd_vel`。

### 4.2 A* / Dijkstra 全局规划

全局规划的目标是在静态地图中找到从起点到目标点的最优路径。

- Dijkstra 算法从起点向外扩展，能够找到全局最短路径，但没有目标方向启发，搜索范围通常较大。
- A* 算法在 Dijkstra 的基础上加入启发函数，能更快地朝目标点搜索，因此通常效率更高。

在本实验中，`GlobalPlanner` 作为全局规划器使用。当参数 `use_dijkstra: false` 时，更接近 A* 搜索方式。

### 4.3 DWA 局部规划

DWA（Dynamic Window Approach）是一种基于速度采样的局部规划算法。其核心思想是：

1. 在当前速度和加速度约束下采样若干组速度；
2. 预测每组速度在短时间内对应的轨迹；
3. 对轨迹进行打分；
4. 选择综合得分最优的一组速度作为控制输出。

DWA 的优点是实现稳定、实时性较好，但在狭窄环境或大曲率转弯时可能表现得较保守。

### 4.4 TEB 局部规划

TEB（Timed Elastic Band）将局部路径表示为带有时间信息的轨迹点序列，通过优化方法同时考虑：

- 轨迹平滑性
- 时间最优性
- 障碍物距离
- 速度与加速度约束
- 运动学约束

与 DWA 相比，TEB 在狭窄通道、连续转弯和复杂路径跟踪场景中通常能生成更平滑的轨迹。

## 5. 实验实现内容

本实验在当前 LIMO 工作区中完成了导航功能落地，主要实现内容如下：

### 5.1 建图流程

在 `limo_mapping` 包中整理了建图入口，保留以下方式：

- `gmapping.launch`
- `hector.launch`
- `cartographer.launch`

其中：

- `gmapping` 为当前工作区默认建图方案；
- `hector` 可作为另一种 SLAM 方案；
- `cartographer.launch` 在当前环境中作为兼容入口，实际回退到 `gmapping`。

保存地图后可生成：

- `~/myfile/robote_project/limo_ws/map/map.yaml`
- `~/myfile/robote_project/limo_ws/map/map.pgm`

### 5.2 寻路流程

在 `smartcar_navigation` 包中实现了基于静态地图的导航流程，提供三种入口：

1. `smartcar_navigation_teb.launch`
2. `smartcar_navigation_dwa.launch`
3. `smartcar_navigation_teb_astar.launch`

这三个入口均包含：

- 地图加载
- AMCL 定位
- `move_base` 导航
- RViz 可视化

### 5.3 针对 LIMO 的适配

由于参考实验原始配置更偏向 TurtleBot 风格，因此本实验对 LIMO 仿真平台进行了适配，主要包括：

1. 激光话题改为 `/limo/scan`
2. 控制话题改为 `/cmd_vel`
3. 机器人底盘坐标系改为 `base_footprint`
4. 里程计坐标系设为 `odom`
5. 地图默认路径改为当前工作区：
   `~/myfile/robote_project/limo_ws/map/map.yaml`
6. 调整机器人足迹、障碍膨胀半径、速度上限、角速度上限和加速度参数，使 LIMO 更适合轨迹跟踪

## 6. 实验步骤

### 6.1 编译工作区

```bash
cd ~/myfile/robote_project/limo_ws
catkin_make
source devel/setup.bash
```

### 6.2 启动 Gazebo 仿真

```bash
roslaunch limo_gazebo_sim limo_four_diff.launch
```

### 6.3 建图

任选一种建图方式：

#### 方法一：Gmapping

```bash
roslaunch limo_mapping gmapping.launch
```

#### 方法二：Hector

```bash
roslaunch limo_mapping hector.launch
```

控制机器人移动：

```bash
rosrun limo_gazebo_sim keyboard_teleop.py
```

建图完成后保存地图：

```bash
mkdir -p ~/myfile/robote_project/limo_ws/map
rosrun map_server map_saver -f ~/myfile/robote_project/limo_ws/map/map
```

### 6.4 导航

#### 1. TEB 局部规划

```bash
roslaunch smartcar_navigation smartcar_navigation_teb.launch
```

#### 2. DWA 局部规划

```bash
roslaunch smartcar_navigation smartcar_navigation_dwa.launch
```

#### 3. A* 全局规划 + TEB 局部规划

```bash
roslaunch smartcar_navigation smartcar_navigation_teb_astar.launch
```

### 6.5 RViz 中设置导航目标

启动导航后，在 RViz 中：

1. 使用 `2D Pose Estimate` 设置机器人初始位姿；
2. 使用 `2D Nav Goal` 设置目标点；
3. 观察机器人在全局路径和局部路径引导下移动到目标位置。

## 7. 关键文件与作用

### 7.1 建图部分

`limo_mapping/launch/gmapping.launch`

- 启动 `slam_gmapping`
- 负责订阅激光数据并生成地图

`limo_mapping/launch/hector.launch`

- 启动 `hector_mapping`
- 利用激光匹配进行建图

`limo_mapping/launch/cartographer.launch`

- 兼容原实验流程
- 当前环境中实际调用 `gmapping.launch`

### 7.2 导航部分

`smartcar_navigation/launch/amcl.launch`

- 启动 AMCL 定位
- 设置粒子数、里程计噪声、激光模型与 TF 坐标系

`smartcar_navigation/launch/move_base_dwa.launch`

- 启动 `move_base`
- 使用 `DWAPlannerROS` 作为局部规划器

`smartcar_navigation/launch/move_base_teb.launch`

- 启动 `move_base`
- 使用 `TebLocalPlannerROS` 作为局部规划器

`smartcar_navigation/launch/move_base_teb_astar.launch`

- 启动 `move_base`
- 使用 `GlobalPlanner` 做全局规划
- 使用 `TEB` 做局部规划

`smartcar_navigation/param/costmap_common_params.yaml`

- 设置机器人足迹、传感器来源、障碍膨胀半径等公共参数

`smartcar_navigation/param/local_costmap_params.yaml`

- 设置局部代价地图尺寸、更新频率和滚动窗口

`smartcar_navigation/param/global_costmap_params.yaml`

- 设置全局代价地图使用静态地图模式

`smartcar_navigation/param/dwa_local_planner_params.yaml`

- 设置 DWA 的速度采样、代价权重和目标容差

`smartcar_navigation/param/teb_local_planner_params.yaml`

- 设置 TEB 的优化权重、速度约束、障碍物距离和机器人模型

`smartcar_navigation/param/global_planner_params.yaml`

- 设置全局规划算法参数

## 8. 关键参数说明

### 8.1 顶层 launch 参数

`map_file`

- 指定导航时加载的地图文件路径

`use_rviz`

- 控制是否同时启动 RViz

`cmd_vel_topic`

- 指定 `move_base` 输出的速度控制话题

`odom_topic`

- 指定里程计话题

### 8.2 AMCL 参数

`min_particles` / `max_particles`

- 决定粒子滤波中粒子数量范围
- 粒子越多，定位通常更稳定，但计算量更大

`update_min_d`

- 机器人平移超过该距离后才更新粒子滤波

`update_min_a`

- 机器人旋转超过该角度后才更新粒子滤波

`laser_model_type`

- 激光模型类型
- 本实验使用 `likelihood_field`

### 8.3 代价地图参数

`footprint`

- 机器人二维外形
- 会直接影响障碍物膨胀与可通行区域判断

`inflation_radius`

- 障碍物周围膨胀半径
- 半径越大，机器人会离障碍物更远

`obstacle_range`

- 识别障碍物的最大距离

`rolling_window`

- 局部代价地图是否跟随机器人移动

### 8.4 DWA 参数

`max_vel_x`

- 最大线速度

`max_vel_theta`

- 最大角速度

`acc_lim_x`

- 最大线加速度

`path_distance_bias`

- 轨迹接近全局路径的权重

`goal_distance_bias`

- 轨迹接近目标点的权重

`occdist_scale`

- 轨迹远离障碍物的权重

### 8.5 TEB 参数

`max_vel_x`

- 最大前进速度

`max_vel_theta`

- 最大角速度

`weight_obstacle`

- 障碍物约束权重

`weight_optimaltime`

- 时间最优权重

`weight_kinematics_nh`

- 非完整运动学约束权重

`min_obstacle_dist`

- 轨迹与障碍物的最小安全距离

## 9. 实验结果分析

在当前工作区中，建图和导航流程已经可以完整串联，系统具备以下能力：

1. 可使用激光雷达在仿真环境中构建二维地图；
2. 可将生成的地图保存为导航使用的静态地图；
3. 可通过 AMCL 在已有地图上完成定位；
4. 可通过 RViz 设置目标点并调用 `move_base` 导航；
5. 可在 DWA、TEB、A* + TEB 三种模式之间进行切换。

从算法特性上看：

- DWA 方案结构简单、运行稳定，适合一般场景；
- TEB 方案在轨迹平滑性和转弯连续性方面表现更好；
- A* + TEB 方案同时具备较明确的全局路径和较好的局部轨迹优化效果。

本实验中，通过对 LIMO 的速度约束、足迹和障碍物距离参数进行调整，机器人对规划路径的跟踪更加稳定，避免了原始参考参数直接迁移后可能出现的速度过大、转向过急或贴障过近的问题。

## 10. 实验中遇到的问题与解决方法

### 问题 1：原参考实验中的地图路径是写死的本地目录

原始实验配置中地图路径不是当前工作区路径，导致 `map_server` 无法正常加载地图。

解决方法：

- 将地图路径统一改为当前工作区的
  `~/myfile/robote_project/limo_ws/map/map.yaml`

### 问题 2：参考实验配置更适合 TurtleBot，而不是 LIMO

直接使用原始参数会导致传感器话题、机器人尺寸和运动特性不匹配。

解决方法：

- 将 `/scan` 改为 `/limo/scan`
- 将机器人坐标系改为 `base_footprint`
- 重新设置机器人足迹、局部规划速度和障碍物参数

### 问题 3：参考实验中存在冗余或未实际使用的配置文件

原实验包中包含多份针对其他机器人平台的参数。

解决方法：

- 清理未使用的参数文件
- 仅保留当前 LIMO 导航实际使用的配置

## 11. 实验总结

通过本次 LAB10 实验，我完成了从建图到导航的完整 ROS 流程联调，进一步理解了导航栈的工作机制。实验中我掌握了：

1. 如何使用 `gmapping` 或 `hector_mapping` 构建二维地图；
2. 如何使用 `map_server` 和 `amcl` 在静态地图中实现定位；
3. 如何使用 `move_base` 完成路径规划与运动控制；
4. DWA、TEB 和 A* 等算法在导航系统中的角色与区别；
5. 如何根据具体机器人平台调整参数，提高路径跟踪效果。

总体而言，本实验实现了 LIMO 在 Gazebo 仿真环境中的自主导航功能，为后续更复杂的移动机器人路径规划与控制实验打下了基础。
