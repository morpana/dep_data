# We want to calculate the RMS error between the first cycle of a transition relative to the final pattern--"baseline".
# The transition is assumed to be able to "begin" from any point considering the baseline,
# therefore the calculation should be performed along all starting points on the baseline.
# The result which produces the lowest value is taken as the final value, and the timing is noted.
import sys
import rosbag
import matplotlib.pyplot as plt
import numpy as np
#from matplotlib.font_manager import FontProperties

# some constants
position_to_rads = 2.0*3.14159/(2000.0*53.0);
displacement_to_N = 0.237536
base_files = ["/media/markus/OS/Users/Sefi/Dropbox/data/steps_fb_fs/0_rising/0_rising_2017-09-14-20-22-54.bag","/media/markus/OS/Users/Sefi/Dropbox/data/steps_fb_fs/0_rising/0_rising_2017-09-14-20-22-54.bag", "/media/markus/OS/Users/Sefi/Dropbox/data/steps_fb_sd/0_rising/steps_fb_sd_0_rising_2017-09-14-23-37-30.bag"]
base_times = [(16.828+1505413374.96, 19.395+1505413374.96),(30.919+1505413374.96,33.516+1505413374.96),(37.353+1505425050.4,39.785+1505425050.4)]
matrix_filename_to_base_index = {'front_back.dep':0, 'front_side.dep':1, 'side_down.dep':2}

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

# obtain baseline
fb_base = getData(base_files[0],base_times[0][0],base_times[0][1])
fs_base = getData(base_files[1],base_times[1][0],base_times[1][1])
sd_base = getData(base_files[2],base_times[2][0],base_times[2][1])
baseline = [fb_base,fs_base,sd_base]

class transition:
	file = ''
	prev_m = ''
	m = ''
	baseline = []
	time = 0
	f_type = 0
	trigger = 0
	trigger_motor = 0
	trigger_level = 0
	trigger_edge = 0
	duration = 0
	start = 0
	end = 0
	data = []
	rms = 0

def getTransitions(file):
	bag = rosbag.Bag(file)
	trans = []
	for topic, msg, t in bag.read_messages(topics=["/roboy_dep/transition"]):
		tran = transition()
		tran.file = file
		tran.prev_m = msg.prev_filename
		tran.m = msg.matrix_filename
		if tran.m not in matrix_filename_to_base_index.keys():
			continue
		#print baseline[matrix_filename_to_base_index[tran.m]][0][:5,1]
		tran.base = baseline[matrix_filename_to_base_index[tran.m]]
	 	tran.f_type = msg.transition_type
	 	tran.trigger = msg.trigger_on
	 	tran.trigger_motor = msg.trigger_motor
	 	tran.trigger_level = msg.trigger_level
	 	tran.trigger_edge = msg.trigger_edge 		#rising (1) or falling (0)
	 	tran.duration = msg.duration
	 	tran.start = t.to_sec() #Note: this is not actual start of transition, rather the time when the command to transition was given (once trigger condition is met)
	 	tran.end = tran.start+(base_times[matrix_filename_to_base_index[tran.m]][1]-base_times[matrix_filename_to_base_index[tran.m]][0])
	 	temp = getData(file,tran.start,tran.end,transition_stuff=[True,tran.trigger_motor,tran.trigger_level,tran.trigger_edge])
	 	if temp != None:
	 		tran.data = temp
	 		trans.append(tran)
	bag.close()
	return trans

def RMS(base, data):
	return np.sqrt(((base-data)**2).mean())

def allRMS(transition):
	# calculate all RMS
	results = []
	low = 1e9
	index = 0
	for i in range(transition.base[0].shape[0]):
		RMS_ = 0
		for j in range(transition.base[0].shape[1]):
			base = np.roll(np.transpose(transition.base[0])[j],i)
			data = np.transpose(transition.data[0])[j]
			while(len(base) != len(data)):
				if len(base) > len(data):
					base = base[:-1]
				else:
					data = data[:-1]
			RMS_ += RMS(base,data)
		if RMS_ < low:
			low = RMS_
			index = i
		results.append(RMS_)
	return results, low, index

def plot(figure,x,y):
	color_pallette = ['#2274A5', '#B4656F', '#4E937A', '#F3D34A', '#A11692', '#F75C03', '#F1C40F', '#D90368', '#00CC66', '#540B0E', '#2274A5', '#B4656F', '#4E937A', '#F3D34A']
	motor_to_muscle = [0, 1, 0, 2, 6, 5, 0, 0, 0, 0, 4, 0, 3, 0]
	for motor in range(y.shape[0]):
		if sum(y[motor]) == 0:
			continue
		plt.plot(x,y[motor],color=color_pallette[motor], linewidth=2.0, label="Muscle "+str(motor_to_muscle[motor]))
	# configure plots
	plt.ylabel("Motor position (rad)")
	plt.xlabel("Time (s)")
	plt.legend(loc="lower center", mode="expand", ncol=6)

def getRMSvals(transition_file):
	transitions = getTransitions(transition_file)
	# for each transition calculate RMS values for each starting point
	ret = []
	for transition in transitions:
		if transition.prev_m == transition.m or transition.prev_m == "zero.dep" or transition.prev_m[:-4] in transition.m or transition.m[:-4] in transition.prev_m :
			continue
		results, low, index  = allRMS(transition)
		transition.rms = low
		ret.append(transition)
		print low, transition.prev_m, transition.m
		'''
		x = transition.data[2]
		y = np.transpose(transition.data[0])
		plt.figure(1)
		plot(1,x,y)
		x = transition.base[2]
		y = np.transpose(transition.base[0])
		y = np.roll(y,index,axis = 1)
		plt.figure(2)
		plot(2,x,y)
		plt.show()
		#plt.plot(range(128),results)
		#plt.show()
		'''
	return ret

import os
import re

def getFiles(dir_name,regex):
	results = []
	for root, dirs, files in os.walk(dir_name):
		for file in files:
			if regex.match(file):
				results.append(os.path.join(root,file))
				#print os.path.join(root,file)
	return results

def allData():
	folder = "/media/markus/OS/Users/Sefi/Dropbox/data/steps_fb_fs/" #sys.argv[1]
	regex = re.compile(".*?\.bag")
	files = getFiles(folder,regex)
	transitions = []
	for file in files:
		print file
		transitions.append(getRMSvals(file))
		#print transitions[0]
	return transitions
'''
to do:
done - perform calculation for all transitions in a file
done - plot lowest RMS baseline position on top of transition
'''

#allData()