#!/home/dante/anaconda3/bin/python

import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import joblib
import time

class InferenceNode:
    def __init__(self):
        rospy.init_node('arbitrator_node', anonymous=True)
        rospy.loginfo("Activating Arbitrator Inference Node...")

        # self.model_path = rospy.get_param("~model_path", '/home/dante/robotvitals_ws/src/adaptive-shared-control/shared_control/arbimodel_package/model/rfr86f3.joblib')
        self.model_path = rospy.get_param("~model_path", '/home/dante/robotvitals_ws/src/adaptive-shared-control/shared_control/arbimodel_package/model/rfrH82f3.joblib')

        self.model = joblib.load(self.model_path)
        rospy.loginfo("Model Loaded!")

        # Subscribe to vitals
        self.velOdom_sub = rospy.Subscriber('/odom_posErr_sampled', Float64, self.callback_topic1)
        self.psnrLaserscan_sub = rospy.Subscriber('/psnr_laserScan', Float64, self.callback_topic2)
        self.velocity_from_odom = rospy.Subscriber('/odometry/filtered', Odometry, self.callback_topic3)
        # Inference publisher
        self.prediction_pub = rospy.Publisher('/predicted_suffering', Float64, queue_size=10)
        rospy.Timer(rospy.Duration(5), self.on_timer)

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

    def process_data(self):
        if all(data is not None for data in [self.data_topic1, self.data_topic2, self.data_topic3]):
            # Use the data for model input
            input_data = [self.data_topic1, self.data_topic2, self.data_topic3]
            prediction = self.model.predict([input_data])[0]
            self.prediction_pub.publish(Float64(prediction))
            # rospy.loginfo("Prediction: {}".format(prediction))
            # Reset the data after processing
            self.data_topic1 = None
            self.data_topic2 = None
            self.data_topic3 = None

    def on_timer(self, event):
        # Callback function called by the timer
        self.process_data()

if __name__ == '__main__':
    try:
        inference_node = InferenceNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass