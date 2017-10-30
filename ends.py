import sys
import rosbag
import matplotlib.pyplot as plt
import numpy as np
import os
import re

#obtaining data from file
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

#obtaining details for all transitions in data
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

def getTransitions(file, cycles):
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
	 	tran.end = tran.start+(base_times[matrix_filename_to_base_index[tran.m]][1]-base_times[matrix_filename_to_base_index[tran.m]][0])*cycles
	 	temp = getData(file,tran.start,tran.end,transition_stuff=[True,tran.trigger_motor,tran.trigger_level,tran.trigger_edge])
	 	if temp != None:
	 		tran.data = temp
	 		trans.append(tran)
	bag.close()
	return trans

#calculate RMS
def RMS(base, data):
	return np.sqrt(((base-data)**2).mean())

def allRMS(data,base):
    # calculate all RMS
    results = []
    for i in range(data.shape[0]):
        low = 1e9
        for k in range(base.shape[0]):
            RMS_ = 0
            for j in range(data.shape[1]):
                RMS_ += RMS(np.roll(base,k,axis=0)[:,j],np.roll(data,i,axis=0)[0:base.shape[0],j])
            if RMS_ < low:
                low = RMS_
        results.append(low)
    return results

def main(file):
	global position_to_rads
	global displacement_to_N
	global base_files
	global base_times
	global matrix_filename_to_base_index

	# obtain baseline
	global fb_base
	global fs_base
	global sd_base
	global baseline

	path = "/home/roboy/dep_data/data/transitions/"
	position_to_rads = 2.0*3.14159/(2000.0*53.0);
	displacement_to_N = 0.237536
	base_files = [path+"steps_fb_fs/0_rising/0_rising_2017-09-14-20-22-54.bag",path+"steps_fb_fs/0_rising/0_rising_2017-09-14-20-22-54.bag", path+"steps_fb_sd/0_rising/steps_fb_sd_0_rising_2017-09-14-23-37-30.bag"]
	base_times = [(16.828+1505413374.96, 19.395+1505413374.96),(30.919+1505413374.96,33.516+1505413374.96),(37.353+1505425050.4,39.785+1505425050.4)]
	matrix_filename_to_base_index = {'front_back.dep':0, 'front_side.dep':1, 'side_down.dep':2}

	fb_base = getData(base_files[0],base_times[0][0],base_times[0][1])
	fs_base = getData(base_files[1],base_times[1][0],base_times[1][1])
	sd_base = getData(base_files[2],base_times[2][0],base_times[2][1])
	baseline = [fb_base,fs_base,sd_base]

	transitions = getTransitions(file, 5)

	for transition in transitions:
		data = transition.data[0]
		base = baseline[matrix_filename_to_base_index[transition.m]][0]
		results = allRMS(data,base)
		#plot the RMS and select minima
		print "Final behavior: ", transition.m, ", Start time: ", transition.start
		plt.figure(1)
		plt.plot(results)
		plt.figure(2)
		plt.plot(data)
		plt.show()

file = sys.argv[1]
main(file)