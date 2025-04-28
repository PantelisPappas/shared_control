#!/home/dante/anaconda3/bin/python

import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import torch
import time
from ArbiN2 import ArbiN2
from ArbiN3 import ArbiN3

class InferenceNodeNetwork:
    def __init__(self):
        rospy.init_node('arbitrator_node_network', anonymous=True)
        rospy.loginfo("Activating Arbitrator Inference Node Network...")

        # Subscribe to vitals
        self.velOdom_sub = rospy.Subscriber('/odom_posErr_sampled', Float64, self.callback_topic1)
        self.psnrLaserscan_sub = rospy.Subscriber('/psnr_laserScan', Float64, self.callback_topic2)
        self.velocity_from_odom = rospy.Subscriber('/odometry/filtered', Odometry, self.callback_topic3)

        # Load the pre-trained model
        # self.model = torch.load('/home/dante/robotvitals_ws/src/adaptive-shared-control/shared_control/arbimodel_package/model/ARBIN2_72/ARBIN2_72.pth',
        #                         map_location='cpu')
        self.model = torch.load('/home/dante/robotvitals_ws/src/adaptive-shared-control/shared_control/arbimodel_package/model/ARBI3/ARBIN3_72.pth',
                                map_location='cpu')
        self.model.eval()
        self.model.to('cpu')
        rospy.loginfo("Model Loaded!")

        
        # Inference publisher
        self.prediction_pub = rospy.Publisher('/predicted_suffering', Float64, queue_size=10)
        self.timer = rospy.Timer(rospy.Duration(5), self.process_data)

        self.data_topic1 = None
        self.data_topic2 = None
        self.data_topic3 = None
        rospy.loginfo("Arbitrator Inference ONLINE")

    def callback_topic1(self, msg):
        self.data_topic1 = msg.data
        self.process_data()

    def callback_topic2(self, msg):
        self.data_topic2 = msg.data
        self.process_data()

    def callback_topic3(self, msg):
        self.data_topic3 = msg.twist.twist.linear.x
        self.process_data()

    def process_data(self, event=None):
        if any(data is None for data in [self.data_topic1, self.data_topic2, self.data_topic3]):
            return

        # Use the data for model input
        input_data = torch.tensor([self.data_topic1, self.data_topic2, self.data_topic3], dtype=torch.float32).to('cpu')
        # rospy.loginfo("Input Data: %s", input_data)

        prediction = self.model(input_data.unsqueeze(0))
        # rospy.loginfo("Prediction: %s", prediction)

        self.prediction_pub.publish(Float64(prediction.item()))

        # Reset data
        self.data_topic1 = None
        self.data_topic2 = None
        self.data_topic3 = None

if __name__ == '__main__':
    try:
        inference_node = InferenceNodeNetwork()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass