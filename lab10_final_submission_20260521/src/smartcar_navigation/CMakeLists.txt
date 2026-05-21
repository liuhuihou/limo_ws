cmake_minimum_required(VERSION 3.0.2)
project(smartcar_navigation)

find_package(catkin REQUIRED)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/publish_nav_goal.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch param rviz
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(FILES 寻路流程说明.md 实车导航运行说明.md
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
