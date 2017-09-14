import sys
import rosbag
import matplotlib.pyplot as plt
import numpy as np
#from scipy import signal

filename = sys.argv[1]
bag = rosbag.Bag(filename)

time = []
pos = []
#disp = []
for topic, msg, t in bag.read_messages(topics=["/roboy/middleware/MotorStatus"]):
    pos.append(msg.position)
    #disp.append(msg.displacement)
    time.append(t.to_sec())
time = np.array(time)
time = time-time[0]
pos = np.array(pos)

bag.close()

#blue, red, green, yellow, magenta, orange, yellow, pink, lightGreen, darkRed, blue, red, green , yellow, magenta
color_pallette = ['#2274A5', '#B4656F', '#4E937A', '#F3D34A', '#A11692', '#F75C03', '#F1C40F', '#D90368', '#00CC66', '#540B0E', '#2274A5', '#B4656F', '#4E937A', '#F3D34A']

for motor in range(pos[0,:].size):
	if sum(pos[:,motor]) == 0:
		print "Motor "+str(motor)+" not connected\n"
		continue
	plt.plot(time,pos[:,motor],color=color_pallette[motor], linewidth=2.0)
plt.show()

'''
for motor in range(pos[0,:].size):
	# 4th order butterworth filter with 10 hz cutoff
	b, a = signal.butter(4, 0.2, 'low')
	y_filt = signal.lfilter(b,a,vel[:,motor])
	plt.plot(time,y_filt,color=color_pallette[motor], linewidth=2.0)
plt.show()
'''

'''
# moving average filter
for motor in range(vel[0,:].size):
	y_smooth = []
	buff = []
	for y in vel[:,motor]:
	    buff.append(y)
	    y_smooth.append(np.mean(buff))
	    if len(buff)>10:
	        buff.pop(0)
	plt.plot(time,y_smooth)
plt.show()
'''

'''
# directly filtering requencies above 10 hz
vel1_filt = np.array([])
for motor in range(vel[0,:].size):
	vel1_freq = np.fft.fft(vel[:,motor])
	vel1_freq[vel1_freq.size*10/50:-vel1_freq.size*10/50] = 0
	vel1_filt = np.fft.ifft(vel1_freq)
	plt.plot(time,vel1_filt,color=color_pallette[motor], linewidth=3.0)
plt.show()
'''


'''
# to plot in frequency domain
x = np.linspace(0,50,time.size)
vel1_freq = np.fft.fft(vel[:,1])
plt.plot(x,np.abs(vel1_freq))
'''