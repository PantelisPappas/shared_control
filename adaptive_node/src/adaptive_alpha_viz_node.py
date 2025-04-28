#!/usr/bin/env python3

import os
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
from std_msgs.msg import Float32, Int8
import numpy as np

class AdaptiveAlphaVizNode:

    def __init__(self):
        rospy.init_node('adaptive_alpha_viz_node', anonymous=True)
        self.prediction_sub = rospy.Subscriber("/alpha_arb", Float32, self.viz_callback)
        self.ow_sub = rospy.Subscriber("/human_overwrite", Int8, self.human_overwrite_callback)
        self.image_publisher = rospy.Publisher('/image_case', Image, queue_size=1)
        
        script_directory = os.path.dirname(os.path.realpath(__file__))
        # Relative paths to the images directory
        self.image_paths = [
            os.path.join(script_directory, 'images', 'robot.png'),
            os.path.join(script_directory, 'images', 'equal.png'),
            os.path.join(script_directory, 'images', 'human.png'),
        ]

        self.images = []
        self.bridge = CvBridge()
        self.over = 0

        # Load images into the list
        for path in self.image_paths:
            img = cv2.imread(path)
            img = self.bridge.cv2_to_imgmsg(img, encoding="rgb8")
            self.images.append(img)

    def human_overwrite_callback(self, msg):
        self.over = msg.data

    def viz_callback(self, msg):
        self.alpha = msg.data

        if self.alpha < 0.30:
            case = 1
        elif self.alpha < 0.65:
            case = 2
        else:
            case = 3

        if self.over:
            case = 3

        img = self.images[case-1]

        self.image_publisher.publish(img)

if __name__ == '__main__':
    try:
        node = AdaptiveAlphaVizNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
