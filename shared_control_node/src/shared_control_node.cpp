/*
This node combines the controller's inputs with the outputs of the VFH+ alghorithm.
While it still consists of a simple operation of addtion, it can and should be further modifies
for a more optimized input blending. For simple testing though, it should work just fine.
*/
#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <std_msgs/Float32.h>
#include <std_msgs/Int8.h>
#include "geometry_msgs/PoseStamped.h"


class Shared_Control
{
private:
    ros::NodeHandle nh_;
    ros::Subscriber teleop_sub_;
    ros::Subscriber vfh_sub_;
    ros::Subscriber navi_sub_;
    ros::Subscriber alpha_sub_;

    ros::Subscriber iscurrent_goal_sub;
    ros::Subscriber overwrite_sub_;
    ros::Publisher shared_cmd_;
    ros::Timer timer;


    geometry_msgs::Twist tele;
    geometry_msgs::Twist vfh;
    geometry_msgs::Twist navi;
    geometry_msgs::Twist cmd_vel;

    float alpha;
    int is_cg = false;
    int over_flag;



public:
    Shared_Control();
    void teleCallback(const geometry_msgs::Twist::ConstPtr& tele);
    void vfhCallback(const geometry_msgs::Twist::ConstPtr& vfh);
    void naviCallback(const geometry_msgs::Twist::ConstPtr& navi);

    void operationCallback(const ros::TimerEvent&);
    void overwriteCallback(const std_msgs::Int8::ConstPtr& msg);
    void cgCallback(const geometry_msgs::PoseStamped::ConstPtr& msg);
    void alphaCallback(const std_msgs::Float32::ConstPtr& msg);

};

Shared_Control::Shared_Control()
{
  teleop_sub_ = nh_.subscribe("/delayed_teleop/cmd_vel", 5, &Shared_Control::teleCallback,this); //subscriber to controller commands
  vfh_sub_ = nh_.subscribe("/vfh/cmd_vel", 5, &Shared_Control::vfhCallback, this); //subscriber to VFH+ output
  navi_sub_ = nh_.subscribe("/navigation/cmd_vel", 5, &Shared_Control::naviCallback, this); //subscriber to /move_base/navigation/ output
  alpha_sub_ = nh_.subscribe("/alpha_arb", 5, &Shared_Control::alphaCallback, this); //subscriber to arbitrator alpha
  iscurrent_goal_sub = nh_.subscribe("/move_base/current_goal", 5, &Shared_Control::cgCallback, this);

  overwrite_sub_ = nh_.subscribe("/human_overwrite", 5, &Shared_Control::overwriteCallback, this);
  shared_cmd_ = nh_.advertise<geometry_msgs::Twist>("/shared_control/cmd_vel", 5);
  timer = nh_.createTimer(ros::Duration(0.1), &Shared_Control::operationCallback, this);
}

void Shared_Control::overwriteCallback(const std_msgs::Int8::ConstPtr& msg){
  over_flag = msg->data;
}

void Shared_Control::alphaCallback(const std_msgs::Float32::ConstPtr& msg){
  alpha = msg->data;
}

void Shared_Control::teleCallback(const geometry_msgs::Twist::ConstPtr& msg)
{
//  Teleoperation callback. We store the values of the controler
//  input to class variables.
  tele.linear.x = msg->linear.x;
  tele.linear.y = msg->linear.y;
  tele.linear.z = msg->linear.z;
  tele.angular.x = msg->angular.x;
  tele.angular.y = msg->angular.y;
  tele.angular.z = msg->angular.z;
  }
void Shared_Control::vfhCallback(const geometry_msgs::Twist::ConstPtr& msg)
{
  //  Same as teleCallback.
  vfh.linear.x = msg->linear.x;
  vfh.linear.y = msg->linear.y;
  vfh.linear.z = msg->linear.z;
  vfh.angular.x = msg->angular.x;
  vfh.angular.y = msg->angular.y;
  vfh.angular.z = msg->angular.z;
}

void Shared_Control::naviCallback(const geometry_msgs::Twist::ConstPtr& msg)
{
  navi.linear.x = msg->linear.x;
  navi.linear.y = msg->linear.y;
  navi.linear.z = msg->linear.z;
  navi.angular.x = msg->angular.x;
  navi.angular.y = msg->angular.y;
  navi.angular.z = msg->angular.z;
}

void Shared_Control::cgCallback(const geometry_msgs::PoseStamped::ConstPtr& msg)
{
  is_cg = true;
}

void Shared_Control::operationCallback(const ros::TimerEvent&)
/* We combine the controller and VFH+ inputs.
 We care about the angural x input mostly and ignore the linear x at the moment
This CallBack can be modified freely for more optimized input blending.*/
{
  if(over_flag){
    alpha = 1;
    is_cg = false;
    ROS_WARN("Overwritting Input...");
  }

  switch (is_cg)
  {
    case 0:
    // VFH mode
          if (tele.linear.x == 0 & tele.angular.z == 0)
          {
          /*
          * This is just so VFH+ doesn't move the robot, if the operator is not touching the stick at all
            */
          cmd_vel.linear.x = 0;
          cmd_vel.linear.y = 0;
          cmd_vel.linear.z = 0;

          cmd_vel.angular.x = 0;
          cmd_vel.angular.y = 0;
          cmd_vel.angular.z = 0;
          }
        
          cmd_vel.linear.x = tele.linear.x;
          cmd_vel.linear.y = tele.linear.y + vfh.linear.y;
          cmd_vel.linear.z = tele.linear.z + vfh.linear.z;

          cmd_vel.angular.x = tele.angular.x + vfh.angular.x;
          cmd_vel.angular.y = tele.angular.y + vfh.angular.y;
          cmd_vel.angular.z = alpha * tele.angular.z - (1- alpha)*vfh.angular.z;
          /*
          * The reason there is a '-' here is because VFH+ outputs
            negative values for the -->(right) direction
            possitive values for the <--(left) direction
            whereas teleop outputs
            possitive values for the -->(right) direction
            negative values for the <--(left) direction

            this is honestly a quick fix and works fine at the moment
            */
        break;

    case 1:
    // Navigation mode
          cmd_vel.linear.x = tele.linear.x + navi.linear.x;
          cmd_vel.linear.y = tele.linear.y + navi.linear.y;
          cmd_vel.linear.z = tele.linear.z + navi.linear.z;

          cmd_vel.angular.x = tele.angular.x + navi.angular.x;
          cmd_vel.angular.y = tele.angular.y + navi.angular.y;
          cmd_vel.angular.z = alpha * tele.angular.z + (1- alpha)*navi.angular.z;
        break;

    default:
        ROS_WARN("Unhandled case. Add appropriate handling.");
        break;
  }

  ROS_INFO("Confidence ALPHA %lf", alpha);
  shared_cmd_.publish(cmd_vel);
}

int main(int argc, char **argv)
{
  ros::init(argc, argv, "shared_control_node");
  Shared_Control shared_control_node;
  ros::spin();

  return 0;
}
