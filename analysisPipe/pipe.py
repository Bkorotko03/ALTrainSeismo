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
plt.rcParams['figure.figsize'] = (3,2)
plt.rcParams["figure.dpi"] = 300

# set up initial globals, these will shortly be replaced by interaction
sampFreq = 100 #Hz
nper = 200
winHalfWidth = 5 # seconds
voltCon = 5/16383

sampFreq = inter._get_int(f"Sampling frequency? (press return for default = {sampFreq} Hz):", sampFreq)
nper = inter._get_int(f"Number of points per PSD segment? (press return for default = {nper}): ", nper)
winHalfWidth = inter._get_float(f"Half width of event window? (press return for default = {winHalfWidth} seconds): ")
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
unoFName = inter._get_str(f"Enter file *name* for UNO in UNO output path: ")
dosFName = inter._get_str(f"Enter file *name* for DOS in DOS output path: ")
tresFName = inter._get_str(f"Enter file *name* for TRES in TRES output path: ")

unoPath = f'../SDCardOut/uno/{unoFName}'
dosPath = f'../SDCardOut/dos/{dosFName}'
tresPath = f'../SDCardOut/tres/{tresFName}'

# the no mag names should always be the same
unoNoMagPath = '../SDCardOut/uno/noMagFullUNO.CSV'
dosNoMagPath = '../SDCardOut/dos/noMagFullDOS.CSV'
tresNoMagPath = '../SDCardOut/tres/noMagFullTRES.CSV'

# get clicker path
clickFName = inter._get_str('Enter file *name* for clicker csv: ')
clickerPath = f'../clickerFiles/{clickFName}'

# figure output path handling
fnow = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
outputDirName = fnow
outputDirName = inter._get_str(f'Enter output directory name in /figureOut (press return for default = {outputDirName}): ',outputDirName)
figOut = f'../figureOut/{outputDirName}'
os.makedirs(figOut,exist_ok=True)

# now lets extract arrays from data CSVs
unoSecs,unoSens,unoVolt = cleaner.arrayExtract(unoPath)
dosSecs,dosSens,dosVolt = cleaner.arrayExtract(dosPath)
tresSecs,tresSens,tresVolt = cleaner.arrayExtract(tresPath)

# save raw voltage curves
plt.plot(unoSecs,unoVolt,label='uno')
plt.plot(dosSecs,dosVolt,label='dos')
plt.plot(tresSecs,tresVolt,label='tres')
plt.legend()
plt.xlabel('seconds')
plt.ylabel('Volts')
# plt.tight_layout()
plt.savefig(f'{figOut}/rawSignal.png')
plt.close()

# convert clicker csv to array of seconds
eventSecs = cleaner.utcSecondsConv(clickerPath)

# create indexes from these times
unoEventIdx = cleaner.eventIdx(unoSecs,eventSecs)
dosEventIdx = cleaner.eventIdx(dosSecs,eventSecs)
tresEventIdx = cleaner.eventIdx(tresSecs,eventSecs)

# apply event and noise windows, make lists of arrays
unoEventVolt,unoNoiseVolt = cleaner.windowMaker(unoVolt,unoEventIdx)
unoEventSecs,unoNoiseSecs = cleaner.windowMaker(unoSecs,unoEventIdx)

dosEventVolt,dosNoiseVolt = cleaner.windowMaker(dosVolt,dosEventIdx)
dosEventSecs,dosNoiseSecs = cleaner.windowMaker(dosSecs,dosEventIdx)

tresEventVolt,tresNoiseVolt = cleaner.windowMaker(tresVolt,tresEventIdx)
tresEventSecs,tresNoiseSecs = cleaner.windowMaker(tresSecs,tresEventIdx)

# make event and noise window curves for each detector
for i in range(len(unoEventVolt)):
    plt.plot(unoEventSecs[i],unoEventVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.title('Uno Event Voltage Curves')
plt.savefig(f'{figOut}/unoEventVolt.png')
plt.close()

for i in range(len(dosEventVolt)):
    plt.plot(dosEventSecs[i],dosEventVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.title('Dos Event Voltage Curves')
plt.savefig(f'{figOut}/dosEventVolt.png')
plt.close()

for i in range(len(tresEventVolt)):
    plt.plot(tresEventSecs[i],tresEventVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.title('Tres Event Voltage Curves')
plt.savefig(f'{figOut}/tresEventVolt.png')
plt.close()

for i in range(len(unoNoiseVolt)):
    plt.plot(unoNoiseSecs[i],unoNoiseVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.title('Uno Noise Voltage Curves')
plt.savefig(f'{figOut}/unoNoiseVolt.png')
plt.close()

for i in range(len(dosNoiseVolt)):
    plt.plot(dosNoiseSecs[i],dosNoiseVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.title('Dos Noise Voltage Curves')
plt.savefig(f'{figOut}/dosNoiseVolt.png')
plt.close()

for i in range(len(tresNoiseVolt)):
    plt.plot(tresNoiseSecs[i],tresNoiseVolt[i])

plt.ylabel('Volts')
plt.xlabel('Seconds')
plt.title('Tres Noise Voltage Curves')
plt.savefig(f'{figOut}/tresNoiseVolt.png')
plt.close()

# apply downsampling for PSD prod
unoEventVoltDown = prod.downSamp(unoEventVolt)
unoNoiseVoltDown = prod.downSamp(unoNoiseVolt)

dosEventVoltDown = prod.downSamp(dosEventVolt)
dosNoiseVoltDown = prod.downSamp(dosNoiseVolt)

tresEventVoltDown = prod.downSamp(tresEventVolt)
tresNoiseVoltDown = prod.downSamp(tresNoiseVolt)

# make dicts of PSDs
unoEventPSDs,unoEventF = prod.makePSD(unoEventVoltDown)
unoNoisePSDs,unoNoiseF = prod.makePSD(unoNoiseVoltDown)

dosEventPSDs,dosEventF = prod.makePSD(dosEventVoltDown)
dosNoisePSDs,dosNoiseF = prod.makePSD(dosNoiseVoltDown)

tresEventPSDs,tresEventF = prod.makePSD(tresEventVoltDown)
tresNoisePSDs,tresNoiseF = prod.makePSD(tresNoiseVoltDown)

# average PSDs
unoEventAvgPSD,unoEventAvgF = prod.PSDAverage(unoEventPSDs,unoEventF)
unoNoiseAvgPSD,unoNoiseAvgF = prod.PSDAverage(unoEventPSDs,unoEventF)

dosEventAvgPSD,dosEventAvgF = prod.PSDAverage(dosEventPSDs,dosEventF)
dosNoiseAvgPSD,dosNoiseAvgF = prod.PSDAverage(dosEventPSDs,dosEventF)

tresEventAvgPSD,tresEventAvgF = prod.PSDAverage(tresEventPSDs,tresEventF)
tresNoiseAvgPSD,tresNoiseAvgF = prod.PSDAverage(tresEventPSDs,tresEventF)