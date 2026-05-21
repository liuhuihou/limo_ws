cmake_minimum_required(VERSION 3.0.2)
project(smartcar_navigation)

find_package(catkin REQUIRED)

catkin_package()

install(DIRECTORY launch param rviz
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(FILES 寻路流程说明.md
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
