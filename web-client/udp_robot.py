from socket import *
import time
import numpy as np

def compute_period(timestamps):
	deltas = []
	for i,_ in enumerate(timestamps[:-1]):
		deltas.append(timestamps[i+1] - timestamps[i])
	return np.mean(deltas)

s = socket(AF_INET, SOCK_DGRAM)

s.bind(('',9090))

t0 = time.time()
stamps = []
while True:
	data, addr = s.recvfrom(100)
	td = time.time() - t0
	t0 = time.time()
	stamps.append(t0)
	print(1/compute_period(stamps[-min(len(stamps), 200):]), 1/td)

