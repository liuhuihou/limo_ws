cmake_minimum_required(VERSION 3.0.2)
project(limo_mapping)

find_package(catkin REQUIRED)

catkin_package()

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(FILES 建图流程说明.md
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
