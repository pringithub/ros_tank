
# NOTE: DONT USE THIS! This was made under the assumption that the pose stamp was the odom 

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

ODOM_EST_SUB_TOPIC = ""
ODOM_PUB_TOPIC = "odom"

class PoseStamped2Odom:

    def __init__(self):
        self.ps_sub = rospy.Subscriber(ODOM_EST_SUB_TOPIC, PoseStamped, self.cb, queue_size=1)
        self.odom_pub = rospy.Publisher(ODOM_PUB_TOPIC, Odometry, queue_size=1)

        self.prev_x=None
        self.prev_y=None
        self.prev_yaw=None
	self.prev_ts=None

    def cb(self, data):

	if self.prev_x is not None:

	    pose = data.pose
	    ts = data.header.stamp
	    #https://answers.ros.org/question/69754/quaternion-transformations-in-python/
	    euler = tf.transformations.euler_from_quaternion(pose.orientation)
	    yaw = euler[2]
	    # different method
	    #odom->pose.pose.orientation.z = sin(yaw_/2.0)
	    #odom->pose.pose.orientation.w = cos(yaw_/2.0)

	    dx   = pose.position.x   - self.prev_x
	    dy   = pose.position.y   - self.prev_y
	    dyaw = pose.position.yaw - self.prev_yaw
	    dt   = ts                - self.prev_ts

	    odom = Odometry()
	    #odom.header = 
	    #odom.child_frame_id = 
	    odom.pose.pose = pose
	    odom.pose.covariance[0]  = 0.2 # x, covariances here are likely widely off
	    odom.pose.covariance[7]  = 0.2 # y
	    odom.pose.covariance[35] = 0.4 # yaw
	    odom.twist.twist.linear.x    = dx/dt	
	    odom.twist.twist.linear.y    = dy/dt	
	    odom.twist.twist.angular.yaw = dyaw/dt	
	    
	    self.odom_pub.publish(odom)

	self.prev_x   = data.pose.position.x
	self.prev_y   = data.pose.position.y
	self.prev_yaw = data.pose.position.yaw
	self.prev_ts  = data.header.stamp


if __name__=='__main__':
    rospy.init_node('PoseStamped2Odom')i
    s = PoseStamped2Odom()
    rospy.spin()



