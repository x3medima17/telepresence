import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import json
import math

import sys
import numpy as np
from pprint import pprint
import kinematics

"""
import ros
import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64
"""

import time

import matplotlib.pyplot as plt


class ContinuousFilter:
    class KalmanFilter(object):

        def __init__(self, process_variance, estimated_measurement_variance):
            self.process_variance = process_variance
            self.estimated_measurement_variance = estimated_measurement_variance
            self.posteri_estimate = 0.0
            self.posteri_error_estimate = 1.0

        def input_latest_noisy_measurement(self, measurement):
            priori_estimate = self.posteri_estimate
            priori_error_estimate = self.posteri_error_estimate + self.process_variance

            blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
            self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
            self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

        def get_latest_estimated_measurement(self):
            return self.posteri_estimate

    def __init__(self):
        self.data = []
        self.filtered = []


    @staticmethod
    def filter(noise):
        Y = noise
        measurement_standard_deviation = np.std(Y)

        # The smaller this number, the fewer fluctuations, but can also venture off
        # course..
        process_variance = 1e-2
        estimated_measurement_variance = measurement_standard_deviation ** 2  # 0.05 ** 2
        kalman_filter = ContinuousFilter.KalmanFilter(process_variance, estimated_measurement_variance)
        posteri_estimate_graph = []

        for iteration in Y:
            kalman_filter.input_latest_noisy_measurement(iteration)
            posteri_estimate_graph.append(kalman_filter.get_latest_estimated_measurement())
        return posteri_estimate_graph

    def push(self,val):
        self.data.append(val)
        if len(self.data) > 50:
            curr = self.filter(self.data[-50:])[-1]
            self.filtered.append(curr)


def set_publishers(pub):
    pub.append(rospy.Publisher('/control/joint_20/command', Float64, queue_size=10))
    pub.append(rospy.Publisher('/control/joint_19/command', Float64, queue_size=10))
    pub.append(rospy.Publisher('/control/joint_18/command', Float64, queue_size=10))
    pub.append(rospy.Publisher('/control/joint_17/command', Float64, queue_size=10))
    pub.append(rospy.Publisher('/control/joint_21/command', Float64, queue_size=10))


'''
This is a simple Websocket Echo server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
This program will echo back the reverse of whatever it recieves.
Messages are output to the terminal for debuggin purposes. 
''' 


pub_left = []
pub_right = []


angles = {
		"left" : [ContinuousFilter(), ContinuousFilter(), ContinuousFilter(), ContinuousFilter()],
		"right" : [ContinuousFilter(), ContinuousFilter(), ContinuousFilter(), ContinuousFilter()],
	}
k = 0

kinect = None
clients = []

class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print('new connection')
		self.k = 0
		clients.append(self)
      
	def on_message(self, message):
		self.k += 1
		print(self.k)
		data = json.loads(message)
		left = data["left"]
		right = data["right"]

		points_left = [left["shoulder"], left["elbow"], left["wrist"]]
		angles_left = kinematics.inverse_kinematics(points_left, "left")

		points_right = [right["shoulder"], right["elbow"], right["wrist"]]
		angles_right = kinematics.inverse_kinematics(points_right, "right")

		left = angles_left
		right = angles_right

		for i,item in enumerate(right):
			angles["right"][i].push(right[i])
			print(len(angles["right"][i].filtered), len(angles["right"][i].data))
			if len(angles["right"][i].filtered) > 0:
                #item.publish(angles[i].filtered[-1] *180 / math.pi)
				print("{} ".format(angles["right"][i].filtered[-1] *180 / math.pi))
               
	def on_close(self):
		plt.figure()
		for item in angles["right"]:
			plt.plot(range(len(item.filtered)), item.filtered)

		plt.figure()
		for item in angles["right"]:
			plt.plot(range(len(item.data)), item.data)


		plt.show()
		print('connection closed')
 
	def check_origin(self, origin):
		return True
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
	"""
    	rospy.init_node('kinect', anonymous=True)
    	pub_left.append(rospy.Publisher('/control/joint_36/command', Float64, queue_size=10))
    	pub_left.append(rospy.Publisher('/control/joint_35/command', Float64, queue_size=10))
    	pub_left.append(rospy.Publisher('/control/joint_34/command', Float64, queue_size=10))
    	pub_left.append(rospy.Publisher('/control/joint_33/command', Float64, queue_size=10))

    	pub_right.append(rospy.Publisher('/control/joint_20/command', Float64, queue_size=10))
    	pub_right.append(rospy.Publisher('/control/joint_19/command', Float64, queue_size=10))
    	pub_right.append(rospy.Publisher('/control/joint_18/command', Float64, queue_size=10))
    	pub_right.append(rospy.Publisher('/control/joint_17/command', Float64, queue_size=10))
    	"""
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	myIP = socket.gethostbyname(socket.gethostname())
	print ('*** Websocket Server Started at {}***'.format(myIP))
	tornado.ioloop.IOLoop.instance().start()
