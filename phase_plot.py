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

filename = "/home/roboy/dep_data/data/combination/10FB04FS_04FB10FS_200s_2017-10-18-12-50-31.bag"
weights, times = getWeights(filename)

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

time, pos, force = getData(filename)

# obtain peaks of given muscle data
from scipy.signal import argrelextrema
def getPeaks(position):
    indices = np.array(argrelextrema(position, np.less))
    return indices

##### Obtaining muscle and reference peak indices #####
# For FB to FS
# change muscle = muscle 2 i.e. position[:,3]
muscle = pos[:,3]
muscle_peaks = getPeaks(muscle)[0]
# reference muscle = muscle 5 i.e. position[:,5]
ref = pos[:,5]
ref_peaks = getPeaks(ref)[0]

# target muscle has 3 peaks after end of experiment -> remove these
muscle_peaks = muscle_peaks[:-3]
# reference muscle has 4 peaks after end of experiment -> remove these
ref_peaks = ref_peaks[:-4]


##### Behavior period and reference distance #####

avg_period = (1358.5-717.0)/5
dist = 758.0 - 808.0

##### Phase plot #####
y = ((muscle_peaks-ref_peaks)-dist)/avg_dist*360
x = np.around(times[muscle_peaks]-times[0],2)
plt.figure(1)
plt.plot(x,y)
plt.show()