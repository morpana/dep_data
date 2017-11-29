import sys
import rosbag
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

# obtain percent transition vs. time
def getWeights(filename):
	weights = []
	times = []
	bag = rosbag.Bag(filename)
	for topic, msg, t in bag.read_messages(topics=["/roboy_dep/linear_combination"]):
		weights.append(msg.weights)
		times.append(t.to_sec())
	bag.close()
	return np.array(weights), np.array(times)

# obtain data from file
def getData(filename):
    position_to_rads = 2.0*3.14159/(2000.0*53.0);
    displacement_to_N = 0.237536
    time = []
    pos = []
    force = []
    bag = rosbag.Bag(filename)
    for topic, msg, t in bag.read_messages(topics=["/roboy/middleware/MotorStatus"]):
        pos.append(msg.position)
        force.append(msg.displacement)
        time.append(t.to_sec())
    bag.close()
    time = np.array(time)
    pos = np.array(pos)*position_to_rads
    force = np.array(force)*displacement_to_N
    return time, pos, force

# obtain peaks of given muscle data
from scipy.signal import argrelextrema
def getPeaks(position):
    indices = np.array(argrelextrema(position, np.less))
    return indices

'''
def movingAvg(data, window_size):
    a = []
    for i in range(len(data)):
        a.append(np.ma.average(data[np.clip(i-int(window_size/2),0,len(data)):np.clip(i+int(window_size/2),0,len(data))]))
    return np.array(a)
'''
def movingAvg(data, window_size):
    a = []
    for i in range(len(data)):
        a.append(np.ma.average(data[np.clip(i-window_size,0,len(data)):np.clip(i,0,len(data))]))
    return np.array(a)

# remove indices above/below cutoff times from peaks
def trim(indices,t_start,t_end):
    i_start = int(t_start/0.020)
    i_end = int(t_end/0.020)
    indices[indices < i_start] = 0
    indices[indices > i_end] = 0
    indices = np.trim_zeros(indices)
    return indices

def getEndIndex(weights):
    a = weights[1:-1,1]-weights[2:,1]
    for i in range(len(a)):
        if a[i] > 0:
            return i

def main(filename, motors, ref_motor, t_start=0, t_end=0):
	weights, times = getWeights(filename)
	time, pos, force = getData(filename)

	offset = 0
	while((time[offset]-times[0])<0):
	    offset += 1

	if t_start == 0 and t_end == 0:
		t_start = time[offset]-time[0]+2.0
		t_end = time[offset+getEndIndex(weights)]-time[0]-1.0

	ref_data = movingAvg(pos[:,ref_motor],4)
	ref_peaks = getPeaks(ref_data)[0]
	ref_peaks = trim(ref_peaks,t_start,t_end)

	for motor in motors:
		motor_data = movingAvg(pos[:,motor],4)
		motor_peaks = getPeaks(motor_data)[0]
		motor_peaks = trim(motor_peaks,t_start,t_end)

		avg_dist = np.ma.average((ref_peaks-np.roll(ref_peaks,1))[1:])
		#std_dist = np.std((ref_peaks-np.roll(ref_peaks,1))[1:])

		##### Phase plot #####
		print(motor_peaks, )
		y = (motor_peaks-ref_peaks)/avg_dist*360
		# calculate offset between weight indices and position indices
		offset = 0
		while((time[offset]-times[0])<0):
		    offset += 1
		# use transition percentage as x-axis
		x = (weights[motor_peaks-offset][:,1]-0.4)/0.6*100
		plt.figure(1)
		plt.plot(x,y,color=color_pallette[motor],linewidth=2.0, label="Muscle "+str(motor_to_muscle[motor]))
		
		fontP = FontProperties()
		fontP.set_size('small')
		plt.figure(1)
		plt.ylabel("Relative phase (deg)")
		plt.xlabel("Transition percentage (%)")
		plt.legend(loc="lower center", mode="expand", ncol=6, prop=fontP)
		plt.show()

motor_to_muscle = [0, 1, 0, 2, 6, 5, 0, 0, 0, 0, 4, 0, 3, 0]
muscle_to_motor = [0, 1, 3, 12, 10, 5, 4, 0, 0, 0, 0, 0, 0, 0]
color_pallette = ['#2274A5', '#B4656F', '#4E937A', '#F3D34A', '#A11692', '#F75C03', '#F1C40F', '#D90368', '#00CC66', '#540B0E', '#2274A5', '#B4656F', '#4E937A', '#F3D34A']

'''
# FB to FS phase plot
# recording file
filename = "/home/roboy/dep_data/data/combination/10FB04FS_04FB10FS_200s_2017-10-18-12-50-31.bag"
# start and end time for experiment in recording
#t_start = 4.3
#t_end = 200.8
# index of motor of interest and reference motor
motor = [3]
ref_motor = 5
# Behavior info: distance of motor of interest to reference motor
#dist = 758.0 - 808.0
'''
# FB to FS phase plot
# recording file
filename = "/home/roboy/dep_data/data/combination/10FB04SD_04FB10SD_200s_2017-10-18-12-55-03.bag"
motor = [muscle_to_motor[3],muscle_to_motor[4],muscle_to_motor[6]]
ref_motor = 5



main(filename, motor, ref_motor)