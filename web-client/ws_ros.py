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
    pub.append(rospy.Publisher('/ar601/RShoulder1Pitch_position_controller/command', Float64, queue_size=10))
    pub.append(rospy.Publisher('/ar601/RShoulder3Pitch_position_controller/command', Float64, queue_size=10))
    pub.append(rospy.Publisher('/ar601/RArmPitch_position_controller/command', Float64, queue_size=10))
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
T = 1
Interpolated = [[],[],[],[]]

def compute_period(timestamps):
	deltas = []
	for i,_ in enumerate(timestamps[:-1]):
		deltas.append(timestamps[i+1] - timestamps[i])
	return np.mean(deltas)

def publisher():
	T = 0.005
	global tick
	while c_active:
		l = [0]*4
		r = [0]*4
		for i in range(4):
			q = angles_interp["right"][i](tick)
			pub_right[i].publish(q)
			r[i] = float(q)
			Interpolated[i].append(float(q))

			q = angles_interp["left"][i](tick)
			pub_left[i].publish(q)
			l[i] = float(q)
			# print()
		print(l)
		print(r)
		print()
		tick += 0.4
		time.sleep(T)

		# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# sock.sendto(str.encode(str(q)), ('',9090))


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

				filtered = item.filtered

				angles_interp[key][i] = interp1d(range(len(filtered)), filtered)

		T = compute_period(timestamps)

		# if p == 1:
		# 	thread.start_new_thread( publisher, ( ) )

		# T = compute_period(timestamps)
		# print(T, 1/T)
		# print(p)
	print("done")


class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print('new connection')
		self.k = 0
		clients.append(self)
      
	def on_message(self, message):
		for client in clients:
			client.write_message(message)

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
		# print(left)
		# print(right)
		# sys.exit()
		# print(len(angles["left"][0].filtered))
		# print(right[0])
		for i,item in enumerate(right):
			angles["right"][i].push(right[i])
			angles["left"][i].push(left[i])

			if len(angles["right"][i].filtered) > 0:
				pub_right[i].publish(angles["right"][i].filtered[-1])
				pub_left[i].publish(angles["left"][i].filtered[-1])

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

		plt.figure()
		for item in Interpolated:
			plt.plot(range(len(item)), item)


		plt.show()
		print('connection closed')
 
	def check_origin(self, origin):
		return True
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
	rospy.init_node('kinect', anonymous=True)
	# set_publishers(pub_right)

	pub_right.append(rospy.Publisher('/ar601/RShoulder1Pitch_position_controller/command', Float64, queue_size=10))
	pub_right.append(rospy.Publisher('/ar601/RShoulder2Roll_position_controller/command', Float64, queue_size=10))
	pub_right.append(rospy.Publisher('/ar601/RShoulder3Pitch_position_controller/command', Float64, queue_size=10))
	pub_right.append(rospy.Publisher('/ar601/RElbowYaw_position_controller/command', Float64, queue_size=10))

	pub_left.append(rospy.Publisher('/ar601/LShoulder1Pitch_position_controller/command', Float64, queue_size=10))
	pub_left.append(rospy.Publisher('/ar601/LShoulder2Roll_position_controller/command', Float64, queue_size=10))
	pub_left.append(rospy.Publisher('/ar601/LShoulder3Pitch_position_controller/command', Float64, queue_size=10))
	pub_left.append(rospy.Publisher('/ar601/LElbowYaw_position_controller/command', Float64, queue_size=10))

	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	myIP = socket.gethostbyname(socket.gethostname())
	print ('*** Websocket Server Started at {}***'.format(myIP))
	thread.start_new_thread( consumer, ( ) )
	tornado.ioloop.IOLoop.instance().start()
