from numpy import linalg as LA
import numpy as np

def angle(v1, v2):
	""" Returns the angle in radians between vectors 'v1' and 'v2'    """
	cosang = np.dot(v1, v2)
	sinang = LA.norm(np.cross(v1, v2))
	return np.arctan2(sinang, cosang)

def switch_coords_arr(arr):
	return [-arr[2], -arr[0], arr[1]]

def inverse_kinematics(points, arm):
	if arm != "left" and  arm != "right":
		raise Exception("Wrong arm")
	
	#points = [shoulder:(x,y,z) elbow:(x,y,z) wrist(x,y,z)]
	v1 = switch_coords_arr(points[0])	
	v2 = switch_coords_arr(points[1])
	v3 = switch_coords_arr(points[2])

	
	a1 = np.subtract(np.array(v2), np.array(v1))
	a2 = np.subtract(np.array(v3), np.array(v2))
	a3 = np.subtract(np.array(v3), np.array(v1))

	x1 = a1[0]
	y1 = a1[1]
	z1 = a1[2]

	y2 = a3[1]

	l1 = LA.norm(a1)
	l2 = LA.norm(a2)

	if arm == "left":
		q1 = np.arctan2(x1,z1) + np.pi
		q2 = -np.arccos(y1/l1)
		q4 = -angle(a1,a2)
		a = np.cos(q2) * np.cos(q4)
		b = np.sin(q2) * np.sin(q4)
		c = l1 * np.cos(q2)
		tmp = (a-(y2-c)/l2)/b
		q3 = np.arcsin(tmp)
	else:
		q1 = np.arctan2(-x1, -z1)
		q2 = np.arccos(-y1/l1)
		q4 = angle(a1,a2)
		a = np.cos(q2) * np.cos(q4)
		b = np.sin(q2) * np.sin(q4)
		c = -l1 * np.cos(q2)
		tmp = (a-(y2-c)/(-l2))/b
		q3 = np.arcsin(tmp)
	return [q1,q2,q3,q4]
	



