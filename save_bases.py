import rosbag
import numpy as np
import pickle

def getData(file, start_time, end_time):
	pos = []
	force = []
	velocity = []
	time = []
	result = []

	bag = rosbag.Bag(file)
	for topic, msg, t in bag.read_messages(topics=["/roboy/middleware/MotorStatus"]):
		pos.append(msg.position)
		force.append(msg.displacement)
		velocity.append(msg.velocity)
		time.append(t.to_sec())
	bag.close()

	pos = np.array(pos)
	force = np.array(force)
	velocity = np.array(velocity)
	time = np.array(time)
	
	start_time -= time[0]
	end_time -= time[0]
	time -= time[0]
	start_time = int(start_time/0.02)+1
	end_time = int(end_time/0.02)+1

	result.append(pos[start_time:end_time])
	result.append(velocity[start_time:end_time])
	result.append(force[start_time:end_time])
	result.append(time[start_time:end_time])
	return result

base_files = ["/home/markus/dep/data/transition/steps_fb_fs/0_rising/0_rising_2017-09-14-20-22-54.bag","/home/markus/dep/data/transition/steps_fb_fs/0_rising/0_rising_2017-09-14-20-22-54.bag", "/home/markus/dep/data/transition/steps_fb_sd/0_rising/steps_fb_sd_0_rising_2017-09-14-23-37-30.bag"]
base_times = [(16.828+1505413374.96, 19.395+1505413374.96),(30.919+1505413374.96,33.516+1505413374.96),(37.353+1505425050.4,39.785+1505425050.4)]
fb = getData(base_files[0],base_times[0][0],base_times[0][1])
fs = getData(base_files[1],base_times[1][0],base_times[1][1])
sd = getData(base_files[2],base_times[2][0],base_times[2][1])

import matplotlib.pyplot as plt

position_to_rads = 2.0*3.14159/(2000.0*53.0)

plt.figure(1)
plt.plot(fb[1][:])
plt.show()
plt.figure(2)
plt.plot(fs[1][:])
plt.show()
plt.figure(3)
plt.plot(sd[1][:])
plt.show()

pickle_fb = open("bases/fb.pickle","wb")
pickle.dump(fb, pickle_fb)
pickle_fb.close()

pickle_fs = open("bases/fs.pickle","wb")
pickle.dump(fs, pickle_fs)
pickle_fs.close()

pickle_sd = open("bases/sd.pickle","wb")
pickle.dump(sd, pickle_sd)
pickle_sd.close()