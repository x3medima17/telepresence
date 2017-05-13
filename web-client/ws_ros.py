import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import json
import math
import thread

import sys
import numpy as np
from pprint import pprint
import kinematics
import threading


# import ros
import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

import time

import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


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
    pub.append(rospy.Publisher('/ar601/RShoulder2Roll_position_controller/command', Float64, queue_size=10))
    pub.append(rospy.Publisher('/ar601/RShoulder1Pitch_position_controller/command', Float64, queue_size=10))
    pub.append(rospy.Publisher('/ar601/RShoulder3Pitch_position_controller/command', Float64, queue_size=10))
    pub.append(rospy.Publisher('/ar601/RElbowYaw_position_controller/command', Float64, queue_size=10))
    # pub.append(rospy.Publisher('/control/joint_21/command', Float64, queue_size=10))

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t



pub_left = []
pub_right = []


angles = {
		"left" : [ContinuousFilter(), ContinuousFilter(), ContinuousFilter(), ContinuousFilter()],
		"right" : [ContinuousFilter(), ContinuousFilter(), ContinuousFilter(), ContinuousFilter()],
	}

angles_interp = {
		"left" : [None]*4,
		"right" : [None]*4,
}

k = 0
tick = 0
kinect = None
clients = []
timestamps = []

c_active = True
T = 0

def compute_period(timestamps):
	deltas = []
	for i,_ in enumerate(timestamps[:-1]):
		deltas.append(timestamps[i+1] - timestamps[i])
	return np.mean(deltas)

def move():
	global tick
	for i in range(3):
		q = angles_interp["right"][0](tick)
		pub_right[i].publish(q *180 / math.pi)

	tick += 0.005
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(str.encode(str(q)), ('',9090))


def consumer():
	p = -1
	global c_active
	global T
	while c_active:
		while len(angles["left"][0].filtered) == p+1 and c_active:
			# print(len(angles["left"][0].filtered), p+1)
			time.sleep(0)
		p+=1

		for key in angles.keys():
			for i, item in enumerate(angles[key]):
				# if key == "right":
				# 	pub_right[i].publish(item.filtered[-1] *180 / math.pi)
				N = len(item.filtered)
				if(N<2):
					break
				angles_interp[key][i] = interp1d(range(N), item.filtered)

		T = compute_period(timestamps)

		if p == 1:
			set_interval(move,0.0047)

		T = compute_period(timestamps)
		# print(T, 1/T)
		# print(p)
	print("done")


class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print('new connection')
		self.k = 0
		clients.append(self)
      
	def on_message(self, message):
		global timestamps
		timestamps.append(time.time())
		self.k += 1
		data = json.loads(message)
		left = data["left"]
		right = data["right"]

		points_left = [left["shoulder"], left["elbow"], left["wrist"]]
		angles_left = kinematics.inverse_kinematics(points_left, "left")

		points_right = [right["shoulder"], right["elbow"], right["wrist"]]
		angles_right = kinematics.inverse_kinematics(points_right, "right")

		left = angles_left
		right = angles_right

		print(len(angles["left"][0].filtered))
		for i,item in enumerate(right):
			angles["right"][i].push(right[i])
			angles["left"][i].push(left[i])

			if len(angles["right"][i].filtered) > 0:
                #item.publish(angles[i].filtered[-1] *180 / math.pi)
				# print("{} ".format(angles["right"][i].filtered[-1] *180 / math.pi))
				pass
               
	def on_close(self):
		global c_active
		c_active = False
		plt.figure()
		for item in angles["right"]:
			plt.plot(range(len(item.filtered)), item.filtered)

		plt.figure()
		for item in angles["right"]:
			plt.plot(range(len(item.data)), item.data)


		# plt.show()
		print('connection closed')
 
	def check_origin(self, origin):
		return True
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
	rospy.init_node('kinect', anonymous=True)
	set_publishers(pub_right)
	"""
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
	thread.start_new_thread( consumer, ( ) )
	tornado.ioloop.IOLoop.instance().start()
