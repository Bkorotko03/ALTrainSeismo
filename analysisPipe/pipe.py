# interactive script to process data from an experimental run and output figures
# will essentially be a command line version of pipe.ipynb
# this is being made so we can run analysis on the RasPi

# imports
import pandas as pd
import numpy as np
from scipy.signal import welch
import matplotlib.pyplot as plt
import PSDProd as prod
import csvCleaner as cleaner
import interaction as inter
import os
import sys
import datetime

# plot params
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.minor.visible'] = True
plt.rcParams['ytick.minor.visible'] = True
plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'DejaVu Sans'

# for saving figures
plt.rcParams['figure.figsize'] = (6,4)
plt.rcParams["figure.dpi"] = 300

# set up initial globals, these will shortly be replaced by interaction
sampFreq = 100 #Hz
nper = 200
winHalfWidth = 5 # seconds
voltCon = 5/16383

sampFreq = inter._get_int(f"Sampling frequency? (press return for default = {sampFreq} Hz):", sampFreq)
nper = inter._get_int(f"Number of points per PSD segment? (press return for default = {nper}): ", nper)
winHalfWidth = inter._get_float(f"Half width of event window? (press return for default = {winHalfWidth} seconds): ",5)
voltCon = inter._get_float(f"Voltage conversion? (press return for default value = {voltCon}): ", voltCon)

halfWIndex = winHalfWidth*sampFreq

# set globals for each helper
prod.defFreq = sampFreq
prod.defNper = nper
cleaner.sampFreq = sampFreq
cleaner.window_half_width = winHalfWidth
cleaner.halfWIndex = halfWIndex
cleaner.defVoltCon = voltCon

# get file names for this run
unoFName = inter._get_str(f"Enter file *name* for UNO in UNO output path: ",'unoTest.CSV')
dosFName = inter._get_str(f"Enter file *name* for DOS in DOS output path: ",'dosTest.CSV')
tresFName = inter._get_str(f"Enter file *name* for TRES in TRES output path: ",'tresTest.CSV')

unoPath = f'../SDCardOut/uno/{unoFName}'
dosPath = f'../SDCardOut/dos/{dosFName}'
tresPath = f'../SDCardOut/tres/{tresFName}'

# the no mag names should always be the same
unoNoMagPath = '../SDCardOut/uno/noMagFullUNO.CSV'
dosNoMagPath = '../SDCardOut/dos/noMagFullDOS.CSV'
tresNoMagPath = '../SDCardOut/tres/noMagFullTRES.CSV'

# get clicker path
clickFName = inter._get_str('Enter file *name* for clicker csv: ','clickTest.CSV')
clickerPath = f'../clickerFiles/{clickFName}'

# figure output path handling
fnow = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
outputDirName = fnow
outputDirName = inter._get_str(f'Enter output directory name in /figureOut (press return for default = {outputDirName}): ',outputDirName)
figOut = f'../figureOut/{outputDirName}'
os.makedirs(figOut,exist_ok=True)

print('Extracting arrays from CSVs...')

# now lets extract arrays from data CSVs
unoSecs,unoSens,unoVolt = cleaner.arrayExtract(unoPath)
dosSecs,dosSens,dosVolt = cleaner.arrayExtract(dosPath)
tresSecs,tresSens,tresVolt = cleaner.arrayExtract(tresPath)

print('Plotting raw voltages...')

# save raw voltage curves
plt.plot(unoSecs,unoVolt,label='uno')
plt.plot(dosSecs,dosVolt,label='dos')
plt.plot(tresSecs,tresVolt,label='tres')
plt.legend()
plt.xlabel('seconds')
plt.ylabel('Volts')
plt.title('Raw Voltage Curves')
# plt.tight_layout()
plt.savefig(f'{figOut}/rawSignal.png')
plt.close()

print('Starting windowing...')
# convert clicker csv to array of seconds
eventSecs = cleaner.utcSecondsConv(clickerPath)

# create indexes from these times
unoEventIdx = cleaner.eventIdx(unoSecs,eventSecs)
dosEventIdx = cleaner.eventIdx(dosSecs,eventSecs)
tresEventIdx = cleaner.eventIdx(tresSecs,eventSecs)

# apply event and noise windows, make lists of arrays
unoEventVolt,unoNoiseVolt = cleaner.windowMaker(unoVolt,unoEventIdx,halfWIndex)
unoEventSecs,unoNoiseSecs = cleaner.windowMaker(unoSecs,unoEventIdx,halfWIndex)

dosEventVolt,dosNoiseVolt = cleaner.windowMaker(dosVolt,dosEventIdx,halfWIndex)
dosEventSecs,dosNoiseSecs = cleaner.windowMaker(dosSecs,dosEventIdx,halfWIndex)

tresEventVolt,tresNoiseVolt = cleaner.windowMaker(tresVolt,tresEventIdx,halfWIndex)
tresEventSecs,tresNoiseSecs = cleaner.windowMaker(tresSecs,tresEventIdx,halfWIndex)

print('Plotting windows...')
# make event and noise window curves for each detector
for i in range(len(unoEventVolt)):
    plt.plot(unoEventSecs[i],unoEventVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.xlim(unoSecs.min(),unoSecs.max())
plt.title('Uno Event Voltage Curves')
plt.savefig(f'{figOut}/unoEventVolt.png')
plt.close()

for i in range(len(dosEventVolt)):
    plt.plot(dosEventSecs[i],dosEventVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.xlim(dosSecs.min(),dosSecs.max())
plt.title('Dos Event Voltage Curves')
plt.savefig(f'{figOut}/dosEventVolt.png')
plt.close()

for i in range(len(tresEventVolt)):
    plt.plot(tresEventSecs[i],tresEventVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.xlim(tresSecs.min(),tresSecs.max())
plt.title('Tres Event Voltage Curves')
plt.savefig(f'{figOut}/tresEventVolt.png')
plt.close()

for i in range(len(unoNoiseVolt)):
    plt.plot(unoNoiseSecs[i],unoNoiseVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.xlim(unoSecs.min(),unoSecs.max())
plt.title('Uno Noise Voltage Curves')
plt.savefig(f'{figOut}/unoNoiseVolt.png')
plt.close()

for i in range(len(dosNoiseVolt)):
    plt.plot(dosNoiseSecs[i],dosNoiseVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.xlim(dosSecs.min(),dosSecs.max())
plt.title('Dos Noise Voltage Curves')
plt.savefig(f'{figOut}/dosNoiseVolt.png')
plt.close()

for i in range(len(tresNoiseVolt)):
    plt.plot(tresNoiseSecs[i],tresNoiseVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.xlim(tresSecs.min(),tresSecs.max())
plt.title('Tres Noise Voltage Curves')
plt.savefig(f'{figOut}/tresNoiseVolt.png')
plt.close()

print('Downsampling...')
# apply downsampling for PSD prod
unoEventVoltDown = prod.downSamp(unoEventVolt)
unoNoiseVoltDown = prod.downSamp(unoNoiseVolt)

dosEventVoltDown = prod.downSamp(dosEventVolt)
dosNoiseVoltDown = prod.downSamp(dosNoiseVolt)

tresEventVoltDown = prod.downSamp(tresEventVolt)
tresNoiseVoltDown = prod.downSamp(tresNoiseVolt)

print('Making PSDs...')
# make dicts of PSDs
unoEventPSDs,unoEventF = prod.makePSD(unoEventVoltDown)
unoNoisePSDs,unoNoiseF = prod.makePSD(unoNoiseVoltDown)

dosEventPSDs,dosEventF = prod.makePSD(dosEventVoltDown)
dosNoisePSDs,dosNoiseF = prod.makePSD(dosNoiseVoltDown)

tresEventPSDs,tresEventF = prod.makePSD(tresEventVoltDown)
tresNoisePSDs,tresNoiseF = prod.makePSD(tresNoiseVoltDown)

# average PSDs
unoEventAvgPSD,unoEventAvgF = prod.PSDAverage(unoEventPSDs,unoEventF)
unoNoiseAvgPSD,unoNoiseAvgF = prod.PSDAverage(unoNoisePSDs,unoNoiseF)

dosEventAvgPSD,dosEventAvgF = prod.PSDAverage(dosEventPSDs,dosEventF)
dosNoiseAvgPSD,dosNoiseAvgF = prod.PSDAverage(dosNoisePSDs,dosNoiseF)

tresEventAvgPSD,tresEventAvgF = prod.PSDAverage(tresEventPSDs,tresEventF)
tresNoiseAvgPSD,tresNoiseAvgF = prod.PSDAverage(tresNoisePSDs,tresNoiseF)

print('Plotting PSDs...')
# now to plot these for each frequency band
# in the future might just let the dictionary have one entry, but I wanted to allow for downsampling in the code
for label in prod.freqDict.keys():
    plt.plot(unoEventAvgF[label],unoEventAvgPSD[label],label='uno')
    plt.plot(dosEventAvgF[label],dosEventAvgPSD[label],label='dos')
    plt.plot(tresEventAvgF[label],tresEventAvgPSD[label],label='tres')

    plt.semilogy()
    plt.legend()
    plt.xlabel('Hz')
    plt.ylabel('V$^2$/Hz')
    plt.title(f'Average Event PSDs ($f_s = ${prod.freqDict[label]} Hz)')
    plt.savefig(f'{figOut}/avgEventPSDfs{int(prod.freqDict[label])}.png')
    plt.close()

for label in prod.freqDict.keys():
    plt.plot(unoNoiseAvgF[label],unoNoiseAvgPSD[label],label='uno')
    plt.plot(dosNoiseAvgF[label],dosNoiseAvgPSD[label],label='dos')
    plt.plot(tresNoiseAvgF[label],tresNoiseAvgPSD[label],label='tres')

    plt.semilogy()
    plt.legend()
    plt.xlabel('Hz')
    plt.ylabel('V$^2$/Hz')
    plt.title(f'Average Noise PSDs ($f_s = ${prod.freqDict[label]} Hz)')
    plt.savefig(f'{figOut}/avgNoisePSDfs{int(prod.freqDict[label])}.png')
    plt.close()

print('Converting amp noise to baseline PSDs...')
# now make the baseline PSD for amp noise
unoNoMagSecs,unoNoMagSens,unoNoMagVolt = cleaner.arrayExtract(unoNoMagPath)
dosNoMagSecs,dosNoMagSens,dosNoMagVolt = cleaner.arrayExtract(dosNoMagPath)
tresNoMagSecs,tresNoMagSens,tresNoMagVolt = cleaner.arrayExtract(tresNoMagPath)

# yeah these guys are only gonna exist at 100 Hz idk why i did the downsampling thing tbh
unoNoMagF,unoNoMagPSD = welch(unoNoMagVolt,fs=sampFreq,nperseg=nper)

dosNoMagF,dosNoMagPSD = welch(dosNoMagVolt,fs=sampFreq,nperseg=nper)

tresNoMagF,tresNoMagPSD = welch(tresNoMagVolt,fs=sampFreq,nperseg=nper)

print('Plotting amp noise...')
plt.plot(unoNoMagF,unoNoMagPSD,label='uno')
plt.plot(dosNoMagF,dosNoMagPSD,label='dos')
plt.plot(tresNoMagF,tresNoMagPSD,label='tres')

plt.semilogy()
plt.legend()
plt.xlabel('Hz')
plt.ylabel('V$^2$/Hz')
plt.title('Amp Noise PSDs')
plt.savefig(f'{figOut}/ampNoise.png')
plt.close()

print('Creating decibel PSDs...')
# make PSDs in dB
# i know hardcoding the freq100 is bad, can always downsample and deal with that but thats such a pain rn
unoNoisedB = prod.decibel(unoNoiseAvgPSD['freq100'],unoNoMagPSD)
dosNoisedB = prod.decibel(dosNoiseAvgPSD['freq100'],dosNoMagPSD)
tresNoisedB = prod.decibel(tresNoiseAvgPSD['freq100'],tresNoMagPSD)

unoTraindB = prod.decibel(unoEventAvgPSD['freq100'],unoNoiseAvgPSD['freq100'])
dosTraindB = prod.decibel(dosEventAvgPSD['freq100'],dosNoiseAvgPSD['freq100'])
tresTraindB = prod.decibel(tresEventAvgPSD['freq100'],tresNoiseAvgPSD['freq100'])

# plot background in dB
plt.plot(unoNoMagF,unoNoisedB,label='uno')
plt.plot(dosNoMagF,dosNoisedB,label='dos')
plt.plot(tresNoMagF,tresNoisedB,label='tres')

plt.xlabel('Hz')
plt.ylabel('dB')
plt.legend()
plt.title('Avg. Background Noise over Amp Noise')
plt.savefig(f'{figOut}/bkgdOverAmp.png')
plt.close()

# plot train signal
plt.plot(unoNoMagF,unoTraindB,label='uno')
plt.plot(dosNoMagF,dosTraindB,label='dos')
plt.plot(tresNoMagF,tresTraindB,label='tres')

plt.xlabel('Hz')
plt.ylabel('dB')
plt.legend()
plt.title('Avg. Train Signal over Avg. Background Noise')
plt.savefig(f'{figOut}/trainOverBkgd.png')
plt.close()

# now want to compare total signal jumps between events and noise per detector
with open(f'{figOut}/eventSignificance.txt','w') as file:
    for label in prod.freqDict.keys():
        print(f'Computing event signal increase in dB over noise for sampling frequency {prod.freqDict[label]}...')
        unoEventAvgInt = np.trapezoid(unoEventAvgPSD[label],unoEventAvgF[label])
        unoNoiseAvgInt = np.trapezoid(unoNoiseAvgPSD[label],unoNoiseAvgF[label])
        dosEventAvgInt = np.trapezoid(dosEventAvgPSD[label],dosEventAvgF[label])
        dosNoiseAvgInt = np.trapezoid(dosNoiseAvgPSD[label],dosNoiseAvgF[label])
        tresEventAvgInt = np.trapezoid(tresEventAvgPSD[label],tresEventAvgF[label])
        tresNoiseAvgInt = np.trapezoid(tresNoiseAvgPSD[label],tresNoiseAvgF[label])

        unoAvgIntdB = prod.decibel(unoEventAvgInt,unoNoiseAvgInt)
        dosAvgIntdB = prod.decibel(dosEventAvgInt,dosNoiseAvgInt)
        tresAvgIntdB = prod.decibel(tresEventAvgInt,tresNoiseAvgInt)

        file.write(f'Total signal to noise ratio in decibels for 0 - {sampFreq/2} Hz band:\n Uno: {unoAvgIntdB} dB\n Dos: {dosAvgIntdB} dB\n Tres: {tresAvgIntdB} dB')

print(f'All files saved under {figOut}.\n Goodbye :3')