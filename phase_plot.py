import sys
import rosbag
import matplotlib.pyplot as plt
import numpy as np

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

def movingAvg(data, window_size):
    a = []
    for i in range(len(data)):
        a.append(np.ma.average(data[np.clip(i-int(window_size/2),0,len(data)):np.clip(i+int(window_size/2),0,len(data))]))
    return np.array(a)

# remove indices above/below cutoff times from peaks
def trim(indices,t_start,t_end):
    i_start = int(t_start/0.020)
    i_end = int(t_end/0.020)
    indices[indices < i_start] = 0
    indices[indices > i_end] = 0
    indices = np.trim_zeros(indices)
    return indices


def main(filename, muscle, ref_muscle, t_start, t_end):
	weights, times = getWeights(filename)
	time, pos, force = getData(filename)

	muscle_data = movingAvg(pos[:,muscle],3)
	muscle_peaks = getPeaks(muscle_data)[0]

	muscle_peaks = trim(muscle_peaks,t_start,t_end)

	ref_data = movingAvg(pos[:,ref_muscle],3)
	ref_peaks = getPeaks(ref_data)[0]
	ref_peaks = trim(ref_peaks,t_start,t_end)

	avg_dist = np.ma.average((ref_peaks-np.roll(ref_peaks,1))[1:])
	#std_dist = np.std((ref_peaks-np.roll(ref_peaks,1))[1:])

	##### Phase plot #####
	y = (muscle_peaks-ref_peaks)/avg_dist*360
	x = np.around(times[muscle_peaks]-times[0],2)
	plt.figure(1)
	plt.plot(x,y)
	plt.show()

# recording file
filename = "/home/roboy/dep_data/data/combination/10FB04FS_04FB10FS_200s_2017-10-18-12-50-31.bag"
# start and end time for experiment in recording
t_start = 4.3
t_end = 205.0
# index of muscle of interest and reference muscle
muscle = 3
ref_muscle = 5
# Behavior info: distance of muscle of interest to reference muscle
dist = 758.0 - 808.0

main(filename, muscle, ref_muscle, t_start, t_end)