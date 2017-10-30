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

def getPeriods(sequence):
    zeros = []
    for i in range(1,len(sequence)):
        if sequence[i-1] < 0 and sequence[i] > 0:
            zeros.append(i)
    periods = []
    for i in range(1,len(zeros)):
        periods.append((zeros[i-1],zeros[i]))
    return periods

def getMaxima(sequence,periods):
    maxima = []
    for period in periods:
        maxima.append(np.argmax(sequence[period[0]:period[1]])+period[0])
    return np.array(maxima)

def getEndIndex(weights):
    a = weights[1:-1,1]-weights[2:,1]
    for i in range(len(a)):
        if a[i] > 0:
            return i

def main(filename, motors, ref_motor):
	weights, times = getWeights(filename)
	time, pos, force = getData(filename)

	offset = 0
	while((time[offset]-times[0])<0):
	    offset += 1
	i_start = offset
	i_end = offset + getEndIndex(weights)

	for motor in motors:
		ref = pos[:,ref_motor][i_start:i_end]
		muscle = pos[:,motor][i_start:i_end]

		if swap[0] == 0:
			periods = getPeriods(ref)
		else:
			periods = getPeriods(muscle)
		swap.pop(0)
		ref_peaks = getMaxima(ref,periods) #indices of maxima
		muscle_peaks = getMaxima(muscle,periods) #indices of maxima

		avg_dist = np.ma.average((ref_peaks-np.roll(ref_peaks,1))[1:])

		y = (muscle_peaks-ref_peaks)/avg_dist*360
		x = (weights[muscle_peaks-offset][:,1]-0.4)/0.6*100

		plt.figure(1)
		plt.plot(x,y,color=color_pallette[motor],linewidth=2,label="Muscle "+str(motor_to_muscle[motor]))

	fontP = FontProperties()
	fontP.set_size('small')
	plt.figure(1)
	plt.ylabel("Relative phase (deg)")
	plt.xlabel("Transition percentage (%)")
	plt.legend(loc="lower center", mode="expand", ncol=6, prop=fontP)
	plt.show()


'''
# FB to FS
filename = "/home/roboy/dep_data/data/combination/10FB04FS_04FB10FS_200s_2017-10-18-12-50-31.bag"
ref_motor = 5
muscles = [1,2,3,4,5,6]
swap = [0,0,0,0,0,0]
'''

'''
# FB to SD
filename = "/home/roboy/dep_data/data/combination/10FB04SD_04FB10SD_200s_2017-10-18-12-55-03.bag"
ref_motor = 5
muscles = [1,2,3,4,5,6]
swap = [1,0,0,0,0,0]
'''


# FS to SD
filename = "/home/roboy/dep_data/data/combination/10FS04SD_04FS10SD_200s_2017-10-18-12-59-53.bag"
ref_motor = 1 
muscles = [1,2,3,4,5,6]
swap = [0,1,1,0,1,0]


'''
# SD to FB
filename = "/home/roboy/dep_data/data/combination/10SD04FB_04SD10FB_200s_2017-10-18-13-04-33.bag"
ref_motor = 5 
muscles = [1,2,3,4,5,6]
swap = [1,0,0,0,0,0]
'''

motor_to_muscle = [0, 1, 0, 2, 6, 5, 0, 0, 0, 0, 4, 0, 3, 0]
muscle_to_motor = [0, 1, 3, 12, 10, 5, 4, 0, 0, 0, 0, 0, 0, 0]
color_pallette = ['#2274A5', '#B4656F', '#4E937A', '#F3D34A', '#A11692', '#F75C03', '#F1C40F', '#D90368', '#00CC66', '#540B0E', '#2274A5', '#B4656F', '#4E937A', '#F3D34A']

motors = []
for muscle in muscles:
	motors.append(muscle_to_motor[muscle])

main(filename,motors,ref_motor)

