# i) Calculate quasi-coincident state of two behaviors based on phase which minimizes RMS differences between two behaviors
# ii) Calculate trigger levels for muscles based on intersection of each muscle between two behaviors (if multiple intersections pick one closest to quasi-coincident state)

import sys
import rosbag
import matplotlib.pyplot as plt
import numpy as np
import os
import re

# some constants
global position_to_rads
global displacement_to_N
global motor_to_muscle
motor_to_muscle = [0, 1, 0, 2, 6, 5, 0, 0, 0, 0, 4, 0, 3, 0]
position_to_rads = 2.0*3.14159/(2000.0*53.0);
displacement_to_N = 0.237536

def getData(file,start_time,end_time,transition_stuff=[False,0,0,0]): #transition_stuff = [bool,int motor, float trigger_level, bool rising_edge]
	pos = []
	force = []
	time = []
	bag = rosbag.Bag(file)
	for topic, msg, t in bag.read_messages(topics=["/roboy/middleware/MotorStatus"]):
		pos.append(msg.position)
		force.append(msg.displacement)
		time.append(t.to_sec())
	bag.close()
	time = np.array(time)
	start_time -= time[0]
	end_time -= time[0]
	time -= time[0]
	#print start_time,end_time
	pos = np.array(pos)*position_to_rads
	force = np.array(force)*displacement_to_N
	result = []
	start_time = int(start_time/0.02)+1
	end_time = int(end_time/0.02)+1
	if transition_stuff[0]:
		transition_stuff[2] *= position_to_rads
		done = False
		prev = 0
		curr = 0
		while(not done):
			prev = pos[start_time-3:start_time,transition_stuff[1]].mean()
			curr = pos[start_time:start_time+3,transition_stuff[1]].mean()
			if transition_stuff[3]:
				if curr > transition_stuff[2] and prev < transition_stuff[2]:
					done = True
					break
			else:
				if curr < transition_stuff[2] and prev > transition_stuff[2]:
					done = True
					break
			start_time += 1
			end_time += 1
	result.append(pos[start_time:end_time])
	result.append(force[start_time:end_time])
	result.append(time[start_time:end_time])
	return result

def RMS(base, data):
	return np.sqrt(((base-data)**2).mean())

def allRMS(behv1, behv2):
	# calculate all RMS
	results = []
	low = 1e9
	index = 0
	for i in range(behv1.shape[0]):
		RMS_ = 0
		for j in range(behv1.shape[1]):
			base = np.roll(np.transpose(behv1)[j],i)
			data = np.transpose(behv2)[j]
			RMS_ += RMS(base,data)
		if RMS_ < low:
			low = RMS_
			index = i
		results.append(RMS_)
	return results, low, index

def muscleRMS(behv1, behv2):
	# calculate all muscle RMS'
	results = []
	#iterate over all muscles
	for j in range(behv1.shape[1]):
		results.append(RMS(behv1[:,j],behv2[:,j]))
	return results

def intersections(behv1, behv2):
	while(len(behv1) != len(behv2)):
		if len(behv1) > len(behv2):
			behv1 = behv1[:-1]
		else:
			behv2 = behv2[:-1]        
	a, b, index = allRMS(behv1,behv2)
	color_pallette = ['#2274A5', '#B4656F', '#4E937A', '#F3D34A', '#A11692', '#F75C03', '#F1C40F', '#D90368', '#00CC66', '#540B0E', '#2274A5', '#B4656F', '#4E937A', '#F3D34A']
	#fig = plt.figure(1)
	#plt.plot(behv1)
	behv2 = np.roll(behv2,index,axis=0)
	#fig = plt.figure(2)
	#plt.plot(behv2)
	#plt.show()
	muscle_rms = muscleRMS(behv1,behv2)
	# calculate all RMS
	trigger_motors = []
	trigger_levels = []
	trigger_edges = []
	#distance = []
	time_index = []
	diff = behv1[0,:] - behv2[0,:]
	for i in range(1,behv1.shape[0]):
		prev_diff = diff
		diff = behv1[i,:] - behv2[i,:]
		for j in range(behv1.shape[1]):
			if muscle_rms[j] > 1.0: 
				if prev_diff[j]/diff[j] < 0:
					if diff[j] > 0:
						edge = 1
					else:
						edge = 0
					trigger_motors.append(motor_to_muscle[j])
					trigger_levels.append(behv1[i-1,j]/position_to_rads)
					trigger_edges.append(edge)
					#distance.append(abs(i-index))
					time_index.append(i-1)
	return trigger_motors,trigger_levels,trigger_edges,time_index,index


def main():
	path = '../dep_data/data/'
	base_files = [path+"steps_fb_fs/0_rising/0_rising_2017-09-14-20-22-54.bag",path+"steps_fb_fs/0_rising/0_rising_2017-09-14-20-22-54.bag", path+"steps_fb_sd/0_rising/steps_fb_sd_0_rising_2017-09-14-23-37-30.bag"]
	base_times = [(16.828+1505413374.96, 19.395+1505413374.96),(30.919+1505413374.96,33.516+1505413374.96),(37.353+1505425050.4,39.785+1505425050.4)]

	fb_base = getData(base_files[0],base_times[0][0],base_times[0][1])
	fs_base = getData(base_files[1],base_times[1][0],base_times[1][1])
	sd_base = getData(base_files[2],base_times[2][0],base_times[2][1])
	trigger_motors,trigger_levels,trigger_edges,indices,phase = intersections(fb_base[0],sd_base[0])
	return trigger_motors,trigger_levels,trigger_edges,indices,phase



trigger_motors,trigger_levels,trigger_edges,indices,phase = main()
print trigger_motors,trigger_levels,trigger_edges,indices,phase