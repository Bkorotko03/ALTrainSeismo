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

freqDict = {
    f'freq{sampFreq}':sampFreq,
    # f'freq{int(sampFreq/2)}':sampFreq/2,
    # f'freq{int(sampFreq/4)}':sampFreq/4,
    # f'freq{int(sampFreq/10)}':sampFreq/10,
    }

prod.freqDict = freqDict

# initialize detectors
detectors = {}
for name, default in [('uno','concurrentUNO2.CSV'),('dos','concurrentDOS2.CSV'),('tres','concurrentTRES2.CSV')]:
    active = inter._get_bool(f'Is {name} running? (y/n, press return for y): ',True)
    if active:
        fname = inter._get_str(f'Enter file *name* for {name} in {name} output path: ',default)
        clickBool = inter._get_bool(f'Valid clicker for {name}? (y/n, press return for default = y): ',True)
        detectors[name] = {
            'path': f'../SDCardOut/{name}/{fname}',
            'noMagPath': f'../SDCardOut/{name}/noMagFull{name.upper()}.CSV',
            'clickBool': clickBool,
        }

if not detectors:
    print('No detectors initialized. Goodbye :3')
    sys.exit(1)

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

for name,d in detectors.items():
    d['secs'],d['sens'],d['volt'] = cleaner.arrayExtract(d['path'])
    print(f'{name} arrays extracted')

print('Plotting raw voltages...')

# save raw voltage curves
for name,d in detectors.items():
    plt.plot(d['secs'],d['volt'],label=name)
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
for name,d in detectors.items():
    d['eventIdx'] = cleaner.eventIdx(d['secs'],eventSecs)

# apply event and noise windows, make lists of arrays
for name,d in detectors.items():
    # this is for if the clicker times are valid (ie the detector is near the clicker)
    if d['clickBool'] == True:
        d['eventVolt'],d['noiseVolt'] = cleaner.windowMaker(d['volt'],d['eventIdx'],halfWIndex)
        d['eventSecs'],d['noiseSecs'] = cleaner.windowMaker(d['secs'],d['eventIdx'],halfWIndex)
    # this is for dos/tres, which are far away from where clicks are happening
    elif d['clickBool'] == False:
        d['statEventIdx'] = []
        for i in range(len(d['volt'])):
            if (d['volt'][i] <= np.percentile(d['volt'],0.1)) or (d['volt'][i] >= np.percentile(d['volt'],99.9)):
                d['statEventIdx'].append(i)
        
        d['eventVolt'],d['noiseVolt'] = cleaner.windowMaker(d['volt'],d['statEventIdx'],halfWIndex)
        d['eventSecs'],d['noiseSecs'] = cleaner.windowMaker(d['secs'],d['statEventIdx'],halfWIndex)

    # this is if something breaks
    else:
        print(f'Clicker bool not set for detector {name}, goodbye :3')
        sys.exit(1)


print('Plotting windows...')
# make event and noise window curves for each detector
for name,d in detectors.items():
    for i in range(len(d['eventVolt'])):
        plt.plot(d['eventSecs'][i],d['eventVolt'][i])

    plt.ylabel('Volts')
    plt.xlabel('Seconds')
    plt.xlim(d['secs'].min(),d['secs'].max())
    plt.ylim(d['volt'].min()-0.1,d['volt'].max()+0.1)
    plt.title(f'{name.capitalize()} Event Voltage Curves')
    plt.savefig(f'{figOut}/{name}EventVolt.png')
    plt.close()

    for i in range(len(d['noiseVolt'])):
        plt.plot(d['noiseSecs'][i],d['noiseVolt'][i])

    plt.ylabel('Volts')
    plt.xlabel('Seconds')
    plt.xlim(d['secs'].min(),d['secs'].max())
    plt.ylim(d['volt'].min()-0.1,d['volt'].max()+0.1)
    plt.title(f'{name.capitalize()} Noise Voltage Curves')
    plt.savefig(f'{figOut}/{name}NoiseVolt.png')
    plt.close()

print('Downsampling...')
# apply downsampling for PSD prod
for name,d in detectors.items():
    d['eventVoltDown'] = prod.downSamp(d['eventVolt'])
    d['noiseVoltDown'] = prod.downSamp(d['noiseVolt'])

print('Making PSDs...')
# make dicts of PSDs
for name,d in detectors.items():
    d['eventPSDs'],d['eventF'] = prod.makePSD(d['eventVoltDown'])
    d['noisePSDs'],d['noiseF'] = prod.makePSD(d['noiseVoltDown'])

    d['eventAvgPSD'],d['eventAvgF'] = prod.PSDAverage(d['eventPSDs'],d['eventF'])
    d['noiseAvgPSD'],d['noiseAvgF'] = prod.PSDAverage(d['noisePSDs'],d['noiseF'])

print('Plotting PSDs...')
# now to plot these for each frequency band
# in the future might just let the dictionary have one entry, but I wanted to allow for downsampling in the code
for label in prod.freqDict.keys():
    for name,d in detectors.items():
        plt.plot(d['eventAvgF'][label],d['eventAvgPSD'][label],label=name)

    plt.semilogy()
    plt.legend()
    plt.xlabel('Hz')
    plt.ylabel('V$^2$/Hz')
    plt.title(f'Average Event PSDs ($f_s = ${prod.freqDict[label]} Hz)')
    plt.savefig(f'{figOut}/avgEventPSDfs{int(prod.freqDict[label])}.png')
    plt.close()

for label in prod.freqDict.keys():
    for name,d in detectors.items():
        plt.plot(d['noiseAvgF'][label],d['noiseAvgPSD'][label],label=name)

    plt.semilogy()
    plt.legend()
    plt.xlabel('Hz')
    plt.ylabel('V$^2$/Hz')
    plt.title(f'Average Noise PSDs ($f_s = ${prod.freqDict[label]} Hz)')
    plt.savefig(f'{figOut}/avgNoisePSDfs{int(prod.freqDict[label])}.png')
    plt.close()

print('Converting amp noise to baseline PSDs...')
# now make the baseline PSD for amp noise
for name,d in detectors.items():
    d['noMagSecs'],d['noMagSens'],d['noMagVolt'] = cleaner.arrayExtract(d['noMagPath'])

for name,d in detectors.items():
    d['noMagVoltDown'] = prod.downSamp([d['noMagVolt']])


for name,d in detectors.items():
    d['noMagF'] = {}
    d['noMagPSD'] = {}
    for label in prod.freqDict.keys():
        d['noMagF'][label],d['noMagPSD'][label] = welch(d['noMagVoltDown'][label][0],fs=prod.freqDict[label],nperseg=nper)

print('Plotting amp noise...')

for label in prod.freqDict.keys():
    for name,d in detectors.items():
        plt.plot(d['noMagF'][label],d['noMagPSD'][label],label=name)
    
    plt.semilogy()
    plt.legend()
    plt.xlabel('Hz')
    plt.ylabel('V$^2$/Hz')
    plt.title(f'Amp Noise PSDs ($f_s = ${prod.freqDict[label]} Hz)')
    plt.savefig(f'{figOut}/ampNoisefs{int(prod.freqDict[label])}.png')
    plt.close()

print('Creating decibel PSDs...')
# make PSDs in dB
for name,d in detectors.items():
    d['noisedB'] = {}
    d['eventdB'] = {}
    for label in prod.freqDict.keys():
        d['noisedB'][label] = prod.decibel(d['noiseAvgPSD'][label],d['noMagPSD'][label])
        d['eventdB'][label] = prod.decibel(d['eventAvgPSD'][label],d['noiseAvgPSD'][label])

print('Plotting decibel PSDs...')

for label in prod.freqDict.keys():
    # plot background in dB
    for name,d in detectors.items():
        plt.plot(d['noMagF'][label],d['noisedB'][label],label=name)

    plt.xlabel('Hz')
    plt.ylabel('dB')
    plt.legend()
    plt.title(f'Avg. Background over Amp Noise ($f_s = ${prod.freqDict[label]} Hz)')
    plt.savefig(f'{figOut}/bkgdOverAmpfs{int(prod.freqDict[label])}.png')
    plt.close()

    # plot train signal
    for name,d in detectors.items():
        plt.plot(d['noMagF'][label],d['eventdB'][label],label=name)

    plt.xlabel('Hz')
    plt.ylabel('dB')
    plt.legend()
    plt.title(f'Avg. Train Signal over Avg. Background ($f_s = ${prod.freqDict[label]} Hz)')
    plt.savefig(f'{figOut}/trainOverBkgdfs{int(prod.freqDict[label])}.png')
    plt.close()

# # now want to compare total signal jumps between events and noise per detector
# with open(f'{figOut}/eventSignificance.txt','w') as file:
#     for label in prod.freqDict.keys():
#         print(f'Computing event signal increase in dB over noise for sampling frequency {prod.freqDict[label]}...')
#         unoEventAvgInt = np.trapezoid(unoEventAvgPSD[label],unoEventAvgF[label])
#         unoNoiseAvgInt = np.trapezoid(unoNoiseAvgPSD[label],unoNoiseAvgF[label])
#         dosEventAvgInt = np.trapezoid(dosEventAvgPSD[label],dosEventAvgF[label])
#         dosNoiseAvgInt = np.trapezoid(dosNoiseAvgPSD[label],dosNoiseAvgF[label])
#         tresEventAvgInt = np.trapezoid(tresEventAvgPSD[label],tresEventAvgF[label])
#         tresNoiseAvgInt = np.trapezoid(tresNoiseAvgPSD[label],tresNoiseAvgF[label])

#         unoAvgIntdB = prod.decibel(unoEventAvgInt,unoNoiseAvgInt)
#         dosAvgIntdB = prod.decibel(dosEventAvgInt,dosNoiseAvgInt)
#         tresAvgIntdB = prod.decibel(tresEventAvgInt,tresNoiseAvgInt)

#         file.write(f'Total signal to noise ratio in decibels for 0 - {sampFreq/2} Hz band:\n Uno: {unoAvgIntdB} dB\n Dos: {dosAvgIntdB} dB\n Tres: {tresAvgIntdB} dB')

# SNR vs window width sweep per detector, thank you copilot :)
print('Computing SNR vs window width...')

# get snr band
bandMin = 10
bandMax = sampFreq/2

bandMin = inter._get_float(f'SNR analysis band minimum? (press return for default = {bandMin} Hz): ',bandMin,0,bandMax)
bandMax = inter._get_float(f'SNR analysis band maximum? (press return for default = {bandMax} Hz): ',bandMax,bandMin,sampFreq)


snr_band = (bandMin,bandMax)
candidate_widths = np.arange(1, 15, 0.25)  # seconds
freqLabel = f'freq{int(sampFreq)}'

for name, d in detectors.items():
    snr_curve = []
    for cand in candidate_widths:
        cand_half = int(cand * sampFreq)
        if d['clickBool'] == True:
            eVolt, nVolt = cleaner.windowMaker(d['volt'], d['eventIdx'], cand_half)
        elif d['clickBool'] == False:
            eVolt, nVolt = cleaner.windowMaker(d['volt'], d['statEventIdx'], cand_half)
        else:
            print(f'Clicker bool not set for detector {name}, goodbye :3')
            sys.exit(1)

        eDown = prod.downSamp(eVolt)
        nDown = prod.downSamp(nVolt)
        ePSDs, eFs = prod.makePSD(eDown)
        nPSDs, nFs = prod.makePSD(nDown)
        if not ePSDs[freqLabel] or not nPSDs[freqLabel]:
            snr_curve.append(np.nan)
            continue
        eAvg, eF = prod.PSDAverage(ePSDs, eFs)
        nAvg, nF = prod.PSDAverage(nPSDs, nFs)
        fArr = eF[freqLabel]
        mask = (fArr >= snr_band[0]) & (fArr <= snr_band[1])
        ePow = np.trapezoid(eAvg[freqLabel][mask], fArr[mask])
        nPow = np.trapezoid(nAvg[freqLabel][mask], fArr[mask])
        snr_curve.append(10 * np.log10(ePow / nPow) if nPow > 0 else np.nan)

    snr_arr = np.array(snr_curve)
    valid = ~np.isnan(snr_arr)
    if valid.any():
        best_width = candidate_widths[np.nanargmax(snr_arr)]
        best_snr = np.nanmax(snr_arr)
        print(f'{name}: max SNR {best_snr:.2f} dB at window half-width {best_width} s')
        d['bestWinHalfWidth'] = float(best_width)
        d['bestSNRdB'] = float(best_snr)
    else:
        d['bestWinHalfWidth'] = None
        d['bestSNRdB'] = None

    plt.plot(candidate_widths, snr_curve)
    plt.axvline(winHalfWidth, color='r', linestyle='--', label=f'chosen = {winHalfWidth} s')
    if valid.any():
        plt.axvline(best_width, color='g', linestyle='--', label=f'optimal = {best_width} s')
    plt.xlabel('Window half-width (s)')
    plt.ylabel('SNR (dB)')
    plt.title(f'{name.capitalize()} SNR vs Window Width ({snr_band[0]}-{snr_band[1]} Hz)')
    plt.legend()
    plt.savefig(f'{figOut}/{name}SNRvsWindow.png')
    plt.close()

# output detectors dict as json (strip numpy arrays, keep scalar metadata)
import json

def _json_safe(v):
    if isinstance(v, (np.ndarray, list, dict)):
        return None  # skip arrays and nested dicts of arrays
    if isinstance(v, (np.integer, np.floating)):
        return v.item()
    return v

detectors_out = {
    name: {k: _json_safe(v) for k, v in d.items() if _json_safe(v) is not None}
    for name, d in detectors.items()
}

with open(f'{figOut}/detectors.json', 'w') as f:
    json.dump(detectors_out, f, indent=2)

print(f'All files saved under {figOut}.\n Goodbye :3')