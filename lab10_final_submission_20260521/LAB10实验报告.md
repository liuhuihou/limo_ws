# LAB10 实验报告

## 1. 实验名称

ROS Navigation Stack 自主导航实验（LAB10）

## 2. 实验要求

在给定地图环境中，分别运行以下三种导航配置，并比较其导航表现：

1. 默认全局规划器 + DWA 局部规划器
2. 默认全局规划器 + TEB 局部规划器
3. A* 全局规划器 + TEB 局部规划器

本次整理的工作区同时补齐了：

- 仿真环境导航入口
- 真实 LIMO 小车导航入口
- 报告、说明文档和提交打包材料

## 3. 实验环境

- Ubuntu 20.04
- ROS Noetic
- Gazebo 11
- LIMO 四轮差速仿真模型
- 真实 LIMO 小车
- 工作区路径：`~/myfile/robote_project/limo_ws`

## 4. 实验原理

### 4.1 ROS 导航栈组成

导航流程由以下模块组成：

- `map_server`：加载静态地图并发布 `/map`
- `amcl`：粒子滤波定位，输出机器人在 `map` 坐标系中的位姿
- `move_base`：统一调用全局规划器与局部规划器
- `global_costmap` / `local_costmap`：构建全局与局部代价地图
- 全局规划器：在已知地图上搜索从起点到目标点的可行路径
- 局部规划器：在机器人附近实时生成速度指令 `/cmd_vel`

### 4.2 Dijkstra / A* 全局规划

- Dijkstra 不使用目标启发信息，搜索范围更大，但能保证最短路径搜索的完整性。
- A* 在 Dijkstra 基础上加入启发函数，更倾向于朝目标方向扩展，通常搜索效率更高。

本实验中 `GlobalPlanner` 的 `use_dijkstra: false`，因此第三组配置使用的是更接近 A* 的全局规划方式。

### 4.3 DWA 局部规划

DWA 的核心思想是：

1. 在当前速度和加速度约束下采样多组控制量。
2. 预测每组速度在短时间内形成的轨迹。
3. 综合考虑离全局路径距离、离目标距离和避障代价。
4. 选择得分最高的一组速度作为输出。

特点：

- 实时性好
- 实现稳定
- 在转弯多、空间狭窄时可能较保守

### 4.4 TEB 局部规划

TEB 将局部轨迹建模为带时间信息的弹性带，通过优化同时考虑：

- 轨迹平滑性
- 时间最优性
- 障碍物距离
- 速度和加速度约束
- 非完整运动学约束

特点：

- 转弯更连续
- 路径更平滑
- 对参数更敏感，调参成本略高

## 5. 本次实现内容

### 5.1 仿真导航入口

`smartcar_navigation` 包中保留三套仿真入口：

- `smartcar_navigation_dwa.launch`
- `smartcar_navigation_teb.launch`
- `smartcar_navigation_teb_astar.launch`

三者都包含：

- 地图加载
- AMCL 定位
- `move_base`
- RViz 可视化

### 5.2 补齐真实小车导航入口

当前工作区原本缺失真实车端导航启动层，因此本次新增：

- `limo_real_amcl.launch`
- `limo_real_navigation_dwa.launch`
- `limo_real_navigation_teb.launch`
- `limo_real_navigation_teb_astar.launch`

同时补齐了可复用的底层入口：

- `amcl_real.launch`
- `move_base_real_dwa.launch`
- `move_base_real_teb.launch`
- `move_base_real_teb_astar.launch`

这些实车启动文件把最容易变化的接口改成了可覆盖参数，包括：

- `scan_topic`
- `sensor_frame`
- `cmd_vel_topic`
- `odom_topic`
- `odom_frame`
- `base_frame`
- `global_frame`

这样即使真实车底层驱动代码丢失，只要重新接回常用 ROS 接口，就可以直接复用本实验的导航层。

### 5.3 LIMO 平台适配

针对 LIMO，本次导航配置主要做了以下适配：

1. 激光话题统一为 `/limo/scan`
2. 底盘控制话题统一为 `/cmd_vel`
3. 底盘参考坐标系使用 `base_footprint`
4. 里程计坐标系使用 `odom`
5. 地图默认路径改为当前工作区 `map/map.yaml`

## 6. 关键参数调整与影响

### 6.1 代价地图参数

`param/costmap_common_params.yaml`

- `footprint: [[-0.13, -0.11], [-0.13, 0.11], [0.13, 0.11], [0.13, -0.11]]`
  影响：与 LIMO 车身尺寸匹配后，贴障现象减轻。
- `inflation_radius: 0.35`
  影响：机器人会主动与障碍保持更安全距离。
- `cost_scaling_factor: 5.0`
  影响：靠近障碍时代价增长更明显。

### 6.2 DWA 参数

`param/dwa_local_planner_params.yaml`

- `max_vel_x: 0.30`
- `max_vel_trans: 0.28`
- `max_vel_theta: 1.20`
- `path_distance_bias: 40.0`
- `goal_distance_bias: 18.0`
- `occdist_scale: 0.05`

影响：

- 适当限制线速度和角速度后，机器人不容易因为速度过大而偏离路径。
- 增大 `path_distance_bias` 后，轨迹更愿意贴近全局路径。
- `occdist_scale` 偏小，因此 DWA 更强调跟踪路径和到达目标，而不是大范围绕障。

### 6.3 TEB 参数

`param/teb_local_planner_params.yaml`

- `max_vel_x: 0.22`
- `max_vel_theta: 1.20`
- `acc_lim_x: 0.8`
- `min_obstacle_dist: 0.12`
- `inflation_dist: 0.25`
- `weight_obstacle: 50.0`
- `weight_kinematics_nh: 1000.0`

影响：

- 比 DWA 更保守的线速度设置有利于实车稳定跟踪。
- `weight_obstacle` 较高时，轨迹会主动远离障碍物。
- `weight_kinematics_nh` 较高时，更符合非完整约束底盘的运动特性。

### 6.4 A* 全局规划参数

`param/global_planner_params.yaml`

- `use_dijkstra: false`
- `use_quadratic: true`
- `allow_unknown: true`

影响：

- `use_dijkstra: false` 使全局搜索更接近 A*，路径搜索速度通常更高。
- 在地图有效区域内，A* 全局路径更有目标导向性。

## 7. 运行方法

### 7.1 仿真

启动 Gazebo：

```bash
cd ~/myfile/robote_project/limo_ws
catkin_make
source devel/setup.bash
roslaunch limo_gazebo_sim limo_four_diff.launch
```

三种导航配置：

```bash
roslaunch smartcar_navigation smartcar_navigation_dwa.launch
roslaunch smartcar_navigation smartcar_navigation_teb.launch
roslaunch smartcar_navigation smartcar_navigation_teb_astar.launch
```

### 7.2 真实小车

在真实车底层驱动已经启动的前提下运行：

```bash
roslaunch smartcar_navigation limo_real_navigation_dwa.launch
roslaunch smartcar_navigation limo_real_navigation_teb.launch
roslaunch smartcar_navigation limo_real_navigation_teb_astar.launch
```

如果真实车实际使用 `/scan`，可覆盖参数：

```bash
roslaunch smartcar_navigation limo_real_navigation_teb.launch scan_topic:=/scan
```

### 7.3 RViz 操作

1. 使用 `2D Pose Estimate` 设置初始位姿
2. 使用 `2D Nav Goal` 设置目标点
3. 观察全局路径、局部路径和代价地图

## 8. 结果记录

### 8.1 真实小车运行照片

以下照片为本工作区中保留的真实 LIMO 导航现场记录：

![real_01](真实小车寻路截图/Weixin%20Image_20260521175606_67_1.jpg)

![real_02](真实小车寻路截图/Weixin%20Image_20260521175610_69_1.jpg)

![real_03](真实小车寻路截图/Weixin%20Image_20260521180122_39_70.jpg)

![real_04](真实小车寻路截图/Weixin%20Image_20260521180131_42_70.jpg)

从保留图片可以看出：

- 地图、激光点云、局部代价地图和局部足迹都已经正常显示
- 真实车已能在 RViz 中接收目标点并进入持续重规划状态
- `move_base` 与局部代价地图、全局路径链路已经接通

### 8.2 三种配置的性能比较

下表为基于本次参数配置、导航算法特性以及保留运行现象整理出的定性比较：

| 配置 | 全局路径特性 | 局部轨迹平滑性 | 稳定性 | 避障行为 | 到达目标能力 | 结论 |
| --- | --- | --- | --- | --- | --- | --- |
| 默认全局规划器 + DWA | 路径可行但方向变化点较明显 | 一般 | 较稳定 | 偏保守，常出现离散式速度调整 | 中等偏好 | 适合基础任务，调试成本低 |
| 默认全局规划器 + TEB | 全局路径不变 | 更平滑，转弯连续 | 较好 | 对局部障碍响应更自然 | 较好 | 综合表现优于 DWA |
| A* 全局规划器 + TEB | 搜索更有目标导向性 | 平滑 | 较好 | 兼顾全局和局部优化 | 最好 | 本实验中最推荐 |

### 8.3 仿真与真实车差异

仿真与真实车的主要差异如下：

- 仿真中传感器噪声较小，路径跟踪通常更稳定。
- 真实车存在轮胎打滑、地面摩擦、底盘轻微偏差等因素，轨迹会更抖动。
- 仿真里的障碍物边界更规整，而真实环境中的激光数据可能更稀疏、更噪声化。
- 相同参数下，真实车通常需要更低的速度上限和更保守的避障距离。

## 9. 实验分析

### 9.1 为什么 TEB 效果通常优于 DWA

因为 TEB 不是只在短时间窗口内离散采样速度，而是直接优化一段局部时空轨迹，所以：

- 转弯时更连续
- 局部绕障更自然
- 在曲折环境中不容易出现明显折线

### 9.2 为什么 A* + TEB 是本实验中最优组合

原因在于：

- A* 全局规划相较默认 Dijkstra 风格搜索更有目标导向性
- TEB 又能在局部层面对轨迹进行平滑优化
- 全局路径质量和局部控制质量同时提升

因此第三组配置通常更容易在复杂环境中得到“全局路径清晰、局部运动平滑”的效果。

## 10. 遇到的问题与解决方法

### 问题 1：参考配置更偏向 TurtleBot，不完全适合 LIMO

解决：

- 改激光话题为 `/limo/scan`
- 改底盘坐标系为 `base_footprint`
- 重设足迹、速度上限和障碍膨胀参数

### 问题 2：真实小车导航启动层缺失

解决：

- 新增一套实车专用 launch
- 把传感器话题、底盘话题、TF 坐标系全部改成可覆盖参数

### 问题 3：实车和仿真的运动表现不一致

解决：

- 保持仿真与实车共用同一套核心参数
- 在实车端适当降低速度并提高安全距离

## 11. 实验结论与个人体会

通过本次实验，我对 ROS 导航栈的理解更加完整，尤其是以下几点：

1. 自主导航并不是单个算法，而是地图、定位、代价地图、全局规划和局部规划的协同结果。
2. DWA 更适合快速搭建和基础验证，TEB 更适合追求轨迹平滑性和综合效果。
3. A* + TEB 组合在本实验中表现最均衡，既能给出方向明确的全局路径，也能生成更自然的局部轨迹。
4. 仿真参数不能直接照搬到实车，真实底盘一定要结合速度、避障距离和 TF 链做二次调整。

总体来看，本实验已经完成了 LIMO 在仿真与真实车两侧的导航代码整理与适配，其中第三组配置最值得作为最终推荐方案。
