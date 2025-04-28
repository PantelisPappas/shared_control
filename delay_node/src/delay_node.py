#!/usr/bin/env python3

import functools
import rospy
import sys
import time

from experiments_package.msg import exp_keys

from geometry_msgs.msg import Twist

from std_msgs.msg import String


class delayer:

    def __init__(self):
        self.sub = rospy.Subscriber("/teleop/cmd_vel", Twist, self.callback)
        ###
        self.sub = rospy.Subscriber("/experiment", exp_keys, self.experiment_callback)
        ####
        self.pub = rospy.Publisher("/delayed_teleop/cmd_vel", Twist, queue_size=4)

        self.lag = 1e-9 # in seconds

    def experiment_callback(self, msg):
        flag = msg.data
        if flag == 'lag':
            time.sleep(10)
            self.lag = 0.50


    def delayed_callback(self, msg, event):
        self.pub.publish(msg)

    def callback(self, msg):
        timer = rospy.Timer(rospy.Duration(self.lag), functools.partial(
            self.delayed_callback, msg), oneshot=True)


if __name__ == '__main__':
    rospy.init_node("delay_node")
    dela = delayer()
    rospy.spin()

