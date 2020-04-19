#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
import tf
#from tf.transformations import euler_from_quaternion
from math import sin, cos

TF_TOPIC   = "/tf"
TARGET_FRAME = "odom"
SOURCE_FRAME = "base_link" # TODO change
ODOM_TOPIC = "/odom"
LOOKUP_RATE = 10.0 #Hz


class TF2Odom:

    def __init__(self):
        self.odom_pub = rospy.Publisher(ODOM_TOPIC, Odometry, queue_size=1)

        self.prev_x=None
        self.prev_y=None
        self.prev_yaw=None
	self.prev_ts=None

	self.tf_listener = tf.TransformListener()

	rate = rospy.Rate(LOOKUP_RATE)

	while not rospy.is_shutdown():
            try:
		ts           = self.tf_listener.getLatestCommonTime(SOURCE_FRAME, TARGET_FRAME)
                (trans,quat) = self.tf_listener.lookupTransform(TARGET_FRAME, SOURCE_FRAME, rospy.Time(0))
		#trans = { "x":trans[0], "y":trans[1], "z":trans[2] }
		#quat  = { "x":quat[0], "y":quat[1], "z":quat[2], "w":quat[3] }
		# would be nice to use, apparently people have gotten errors  
		#twist       = tf_listener.lookupTwist(TARGET_FRAME, SOURCE_FRAME, rospy.Time(0), rospy.Duration(1/LOOKUP_RATE))
 
		x = trans[0]
		y = trans[1]

		#https://answers.ros.org/question/69754/quaternion-transformations-in-python/
		euler = tf.transformations.euler_from_quaternion(quat)
		yaw = euler[2]
		# different method
		#odom->pose.pose.orientation.z = sin(yaw_/2.0)
		#odom->pose.pose.orientation.w = cos(yaw_/2.0)
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                continue


	    if self.prev_x is not None:

		dx   = x   - self.prev_x
		dy   = y   - self.prev_y
		dyaw = yaw - self.prev_yaw
		dt_ros   = ts  - self.prev_ts
		dt = dt_ros.secs + dt_ros.nsecs/1000000000.0

		odom = Odometry()
		odom.header.seq      += 1
		odom.header.stamp    = rospy.Time.now()
		odom.header.frame_id = "odom" 
		odom.child_frame_id  = "base_footprint" 
		odom.pose.pose.position.x    = x 
		odom.pose.pose.position.y    = y 
		odom.pose.pose.orientation.z = sin(yaw/2.0) 
		odom.pose.pose.orientation.w = cos(yaw/2.0) 
		odom.pose.covariance[0]  = 0.2 # x, covariances here are guesses, likely widely off
		odom.pose.covariance[7]  = 0.2 # y
		odom.pose.covariance[35] = 0.4 # yaw
		odom.twist.twist.linear.x    = dx/dt	
		odom.twist.twist.linear.y    = dy/dt	
		odom.twist.twist.angular.yaw = dyaw/dt	

		self.odom_pub.publish(odom)

	    self.prev_x   = x 
	    self.prev_y   = y
	    self.prev_yaw = yaw 
	    self.prev_ts  = ts 

	    # enforce the rate
	    rate.sleep()


if __name__=='__main__':
    rospy.init_node('TF2Odom')
    s = TF2Odom()
    rospy.spin()



