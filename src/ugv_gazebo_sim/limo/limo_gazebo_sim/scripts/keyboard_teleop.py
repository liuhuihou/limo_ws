#!/usr/bin/env python

from __future__ import print_function

import select
import sys
import termios
import tty

import rospy
from geometry_msgs.msg import Twist


MOVE_BINDINGS = {
	'i': (1.0, 0.0),
	'o': (1.0, -1.0),
	'u': (1.0, 1.0),
	',': (-1.0, 0.0),
	'.': (-1.0, -1.0),
	'm': (-1.0, 1.0),
	'j': (0.0, 1.0),
	'l': (0.0, -1.0),
	'k': (0.0, 0.0),
	' ': (0.0, 0.0),
}

SPEED_BINDINGS = {
	'w': (1.1, 1.0),
	's': (0.9, 1.0),
	'a': (1.0, 1.1),
	'd': (1.0, 0.9),
}

HELP_TEXT = """
Limo keyboard teleop
---------------------
u    i    o
j    k    l
m    ,    .

w/s: increase/decrease linear speed
a/d: increase/decrease angular speed
space or k: stop
CTRL-C to quit
"""


def get_key(timeout):
	tty.setraw(sys.stdin.fileno())
	readable, _, _ = select.select([sys.stdin], [], [], timeout)
	key = sys.stdin.read(1) if readable else ''
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
	return key


def make_twist(linear_x, angular_z):
	twist = Twist()
	twist.linear.x = linear_x
	twist.angular.z = angular_z
	return twist


def print_status(linear_speed, angular_speed, topic):
	print(HELP_TEXT)
	print('Publishing to %s' % topic)
	print('current linear speed: %.3f, angular speed: %.3f' % (linear_speed, angular_speed))


if __name__ == '__main__':
	settings = termios.tcgetattr(sys.stdin)

	rospy.init_node('limo_keyboard_teleop')
	cmd_vel_topic = rospy.get_param('~cmd_vel_topic', 'cmd_vel')
	linear_speed = rospy.get_param('~linear_speed', 0.3)
	angular_speed = rospy.get_param('~angular_speed', 1.0)
	key_timeout = rospy.get_param('~key_timeout', 0.15)

	publisher = rospy.Publisher(cmd_vel_topic, Twist, queue_size=1)
	print_status(linear_speed, angular_speed, cmd_vel_topic)

	last_twist = make_twist(0.0, 0.0)
	last_command_time = rospy.Time.now()

	try:
		while not rospy.is_shutdown():
			key = get_key(key_timeout)

			if key == '\x03':
				break

			if key in MOVE_BINDINGS:
				linear_factor, angular_factor = MOVE_BINDINGS[key]
				last_twist = make_twist(linear_factor * linear_speed,
										 angular_factor * angular_speed)
				publisher.publish(last_twist)
				last_command_time = rospy.Time.now()
				continue

			if key in SPEED_BINDINGS:
				linear_multiplier, angular_multiplier = SPEED_BINDINGS[key]
				linear_speed *= linear_multiplier
				angular_speed *= angular_multiplier
				print_status(linear_speed, angular_speed, cmd_vel_topic)
				continue

			if key == '' and (rospy.Time.now() - last_command_time).to_sec() >= key_timeout:
				if last_twist.linear.x != 0.0 or last_twist.angular.z != 0.0:
					last_twist = make_twist(0.0, 0.0)
					publisher.publish(last_twist)
				continue

			if key not in MOVE_BINDINGS and key not in SPEED_BINDINGS:
				last_twist = make_twist(0.0, 0.0)
				publisher.publish(last_twist)

	finally:
		publisher.publish(make_twist(0.0, 0.0))
		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
