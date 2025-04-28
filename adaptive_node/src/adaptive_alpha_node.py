#!/usr/bin/env python3

import rospy
import sys
import math
from std_msgs.msg import Float64, Float32


class Arbitrator:

    def __init__(self):
        rospy.init_node("adaptive_alpha_node")
        rospy.loginfo("INITIALISING NODE -> /adaptive_alpha_node")
        rospy.loginfo("Arbitrator is ACTIVE")
        # while not rospy.is_shutdown():
            #Initialize node and log
            
        self.prediction_sub = rospy.Subscriber("/predicted_suffering", Float64, self.arbitration_callback)

        self.alpha_pub = rospy.Publisher("/alpha_arb", Float32, queue_size=4)

    def arbitration_callback(self, msg):
        self.alpha = msg.data            #adaptive  #formula

        self.abfunction = 0.2 + self.alpha
        if (self.abfunction >= 1):
            self.abfunction = 1
        # if (self.alpha <= 0.2):
        #     self.alpha = 0.3
        self.alpha_pub.publish(self.abfunction)
        
 
# def shutdown_log():
#   print("TERMINATING NODE -> /adaptive_alpha_node")
#   print("Arbitrator is NOT ACTIVE")
# rospy.on_shutdown(shutdown_log)

if __name__ == '__main__':
    try:
        arb = Arbitrator()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass




