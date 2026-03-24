# Now we want to make sure we can run the PSD calculation on the Raspi
# This version will also tell us how long it takes to run
# Our two signals we'll be looking for are a sin at 400 Hz and a cos at 100 Hz
# Sampling frequency is 1000 Hz

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import time
import os

fpath = f'./signalTest_out'
os.makedirs(fpath,exist_ok=True)

starttime = time.perf_counter()

# First test case: Noise only in y direction
tgrid1 = np.linspace(0,100,100000)
ygrid1 = np.sin(tgrid1*800*np.pi)
ygrid2 = 3*np.cos(tgrid1*200*np.pi)

# Add y noise
for i in range(len(tgrid1)):
    ygrid1[i] = ygrid1[i]*np.random.normal(1,0.5)
    ygrid2[i] = ygrid2[i]*np.random.normal(1,0.5)

signal1 = ygrid1+ygrid2

plt.plot(tgrid1,signal1)
plt.title('signal1')
plt.xlabel('time (seconds)')
plt.ylabel('signal')
plt.savefig(f'{fpath}/signal1wave.png')
plt.close()

# Now calculate and plot PSD

tpsd1,ypsd1 = sp.signal.welch(signal1,fs=1000)

plt.plot(tpsd1,ypsd1)
plt.semilogy()
plt.title('signal1 PSD estimate')
plt.ylabel('signal power')
plt.xlabel('frequency (Hz)')
plt.savefig(f'{fpath}/signal1PSD.png')
plt.close()

# Now we want to add t series noise ~1/2 sampling frequency. at 0.001 we lose the second peak at 400 Hz
tgrid2 = np.linspace(0,100,100000)

for i in range(len(tgrid2)):
    tgrid2[i] = tgrid2[i] + np.random.normal(0,0.0005)

ygrid3 = np.sin(tgrid2*800*np.pi)
ygrid4 = 3*np.cos(tgrid2*200*np.pi)

for i in range(len(ygrid3)):
    ygrid3[i] = ygrid3[i]*np.random.normal(1,0.5)
    ygrid4[i] = ygrid4[i]*np.random.normal(1,0.5)

signal2 = ygrid3+ygrid4

# now plot signal waveform

plt.plot(tgrid2,signal2)
plt.title('signal2')
plt.ylabel('signal')
plt.xlabel('time (seconds)')
plt.savefig(f"{fpath}/signal2wave.png")
plt.close()

# calculate psd and plot

tpsd2,ypsd2 = sp.signal.welch(signal2,fs=1000)

plt.plot(tpsd2,ypsd2)
plt.semilogy()
plt.title('signal2 psd estimate')
plt.xlabel('frequency (Hz)')
plt.ylabel('signal power')
plt.savefig(f"{fpath}/signal2PSD.png")
plt.close()

endtime = time.perf_counter()

print(f"All analyis and plots done in {(endtime-starttime):.3f} seconds. \npeace :3")