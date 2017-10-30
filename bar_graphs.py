import matplotlib.pyplot as plt
import numpy as np

#plt.rcParams['axes.facecolor'] = '#87AADE'

a = [3.00,3.55,4.04,2.68,2.29,3.91,3.01,2.01]
b = ['0.0,+','1.5,+','3.0,+','1.5,-','0.0,-','-1.5,-','-3.0,+','-1.5,+']
y_pos = np.arange(len(b))
plt.bar(y_pos, a, align='center', alpha=1.0, color='blue') #color='#162D50', 
plt.xticks(y_pos, b)
plt.ylabel('RMS')
plt.xlabel('Trigger level, trigger edge')
#plt.title('Front back to Front side RMS error')
plt.show()


