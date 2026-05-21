# LAB10 提交说明

本提交版材料已经包含：

- `smartcar_navigation` 仿真导航代码
- 新增的真实 LIMO 小车导航启动文件
- 地图文件 `map/map.yaml` 和 `map/map.pgm`
- 真实小车运行照片
- 最终版实验报告 `LAB10实验报告.md`

## 新增的真实车入口

- `limo_real_amcl.launch`
- `limo_real_navigation_dwa.launch`
- `limo_real_navigation_teb.launch`
- `limo_real_navigation_teb_astar.launch`

## 本次已完成的验证

- 新增 launch 文件通过 `xmllint` 语法检查
- `catkin_make --pkg smartcar_navigation limo_gazebo_sim` 编译通过

## 关于仿真截图

当前打包环境可以完成代码补齐和编译验证，但无法稳定完成 Gazebo + RViz 图形化截图采集，因此提交包中保留了：

- 仿真运行入口
- 真实车运行证据
- 详细运行命令和参数说明

如果需要在本机补录仿真截图，直接执行：

```bash
roslaunch limo_gazebo_sim limo_four_diff.launch
roslaunch smartcar_navigation smartcar_navigation_dwa.launch
roslaunch smartcar_navigation smartcar_navigation_teb.launch
roslaunch smartcar_navigation smartcar_navigation_teb_astar.launch
```

然后在 RViz 中使用 `2D Pose Estimate` 和 `2D Nav Goal` 进行截图即可。
