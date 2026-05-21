#!/usr/bin/env python3

import math
import sys
import time

import rospy
from actionlib_msgs.msg import GoalStatusArray
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, Quaternion
from tf.transformations import quaternion_from_euler


def make_quaternion(yaw):
    q = quaternion_from_euler(0.0, 0.0, yaw)
    quat = Quaternion()
    quat.x = q[0]
    quat.y = q[1]
    quat.z = q[2]
    quat.w = q[3]
    return quat


def publish_initial_pose(pub, x, y, yaw):
    msg = PoseWithCovarianceStamped()
    msg.header.stamp = rospy.Time.now()
    msg.header.frame_id = "map"
    msg.pose.pose.position.x = x
    msg.pose.pose.position.y = y
    msg.pose.pose.position.z = 0.0
    msg.pose.pose.orientation = make_quaternion(yaw)
    covariance = [0.0] * 36
    covariance[0] = 0.25
    covariance[7] = 0.25
    covariance[35] = 0.06853891945200942
    msg.pose.covariance = covariance
    pub.publish(msg)


def publish_goal(pub, x, y, yaw):
    msg = PoseStamped()
    msg.header.stamp = rospy.Time.now()
    msg.header.frame_id = "map"
    msg.pose.position.x = x
    msg.pose.position.y = y
    msg.pose.position.z = 0.0
    msg.pose.orientation = make_quaternion(yaw)
    pub.publish(msg)


def main():
    if len(sys.argv) != 7:
        print(
            "usage: publish_nav_goal.py init_x init_y init_yaw goal_x goal_y goal_yaw",
            file=sys.stderr,
        )
        return 1

    init_x, init_y, init_yaw, goal_x, goal_y, goal_yaw = map(float, sys.argv[1:])

    rospy.init_node("publish_nav_goal", anonymous=True)
    init_pub = rospy.Publisher("/initialpose", PoseWithCovarianceStamped, queue_size=1, latch=True)
    goal_pub = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=1, latch=True)
    status_msg = {"data": None}

    def status_cb(msg):
        status_msg["data"] = msg

    rospy.Subscriber("/move_base/status", GoalStatusArray, status_cb, queue_size=1)

    deadline = time.time() + 20.0
    while init_pub.get_num_connections() == 0 and time.time() < deadline and not rospy.is_shutdown():
        rospy.sleep(0.2)

    for _ in range(5):
        publish_initial_pose(init_pub, init_x, init_y, init_yaw)
        rospy.sleep(0.2)

    rospy.sleep(2.0)

    deadline = time.time() + 20.0
    while goal_pub.get_num_connections() == 0 and time.time() < deadline and not rospy.is_shutdown():
        rospy.sleep(0.2)

    for _ in range(3):
        publish_goal(goal_pub, goal_x, goal_y, goal_yaw)
        rospy.sleep(0.3)

    wait_deadline = time.time() + 60.0
    while time.time() < wait_deadline and not rospy.is_shutdown():
        data = status_msg["data"]
        if data and data.status_list:
            last_status = data.status_list[-1].status
            if last_status in (3, 4, 5, 9):
                print(last_status)
                return 0
        rospy.sleep(0.5)

    print("timeout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
