#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <sensor_msgs/Joy.h>
#include "std_msgs/Bool.h"
#include <std_msgs/Int8.h>

class JoyActivate{
	private:
		// void joyCallback(const sensor_msgs::Joy::ConstPtr& joy);
		ros::NodeHandle nh_;

		ros::Publisher event_pub1_;
		ros::Publisher event_pub2_;
		ros::Subscriber joy_sub_; 

	public:
					int count = 0;

		JoyActivate(){

			event_pub1_ = nh_.advertise<std_msgs::Int8>("/pdf_event",1);
			event_pub2_ = nh_.advertise<std_msgs::Int8>("/human_overwrite",1);
			joy_sub_ = nh_.subscribe<sensor_msgs::Joy>("joy", 10, &JoyActivate::joyCallback, this);
		}

		void joyCallback(const sensor_msgs::Joy::ConstPtr& joy)
		{
			std_msgs::Int8 msg1;
			std_msgs::Int8 msg2;

			// Button 1 (assuming index 0)
			if (joy->buttons[1] == 1)
			{
				// ROS_INFO("Button 1 pressed!");
				msg1.data = 1; //count = 1
			}
			else
			{
				// ROS_INFO("Button 1 released.");
				msg1.data = 0;
			}

			// Button 2 (assuming index 1)
			if (joy->buttons[5] == 1)
			{
				// ROS_INFO("Button 2 pressed!");
				msg2.data = 1;
			}
			else
			{
				// ROS_INFO("Button 2 released.");
				msg2.data = 0;
			}

			event_pub1_.publish(msg1);
			event_pub2_.publish(msg2);
		}
};

// class TeleopTurtle
// {
// public:
//   TeleopTurtle();

// private:
//   void joyCallback(const sensor_msgs::Joy::ConstPtr& joy);

//   ros::NodeHandle nh_;

//   int linear_, angular_;
//   double l_scale_, a_scale_;
//   ros::Publisher vel_pub_;
//   ros::Subscriber joy_sub_;

// };


// TeleopTurtle::TeleopTurtle():
//   linear_(1),
//   angular_(2)
// {

//   nh_.param("axis_linear", linear_, linear_);
//   nh_.param("axis_angular", angular_, angular_);
//   nh_.param("scale_angular", a_scale_, a_scale_);
//   nh_.param("scale_linear", l_scale_, l_scale_);


//   vel_pub_ = nh_.advertise<geometry_msgs::Twist>("turtle1/cmd_vel", 1);


//   joy_sub_ = nh_.subscribe<sensor_msgs::Joy>("joy", 10, &TeleopTurtle::joyCallback, this);

// }

// void TeleopTurtle::joyCallback(const sensor_msgs::Joy::ConstPtr& joy)
// {
//   geometry_msgs::Twist twist;
//   twist.angular.z = a_scale_*joy->axes[angular_];
//   twist.linear.x = l_scale_*joy->axes[linear_];
//   vel_pub_.publish(twist);
// }


int main(int argc, char** argv)
{
  ros::init(argc, argv, "activate_noise_joystick");
  JoyActivate joy1;

  ros::spin();
}
