# this code is to produce PSDs, analysis, and the plots from lists of arrays of separated noise and event signals
# combined with csvCleaner into one larger script to run the analysis for the total outputs and inputs this should all work together

import pandas as pd
import numpy as np
from scipy.signal import welch
import json
import os

# lets set some default globals
# interaction in the larger script will allow us to override these
defFreq = 100
defNper = 300

# now initialize dictionary of sampling frequencies for downsampling
# remember PSD can only probe up to sampFreq/2
freqDict = {
    f'freq{defFreq}':defFreq,
    # f'freq{int(defFreq/2)}':defFreq/2,
    # f'freq{int(defFreq/4)}':defFreq/4,
    # f'freq{int(defFreq/10)}':defFreq/10,
    }

# now define a quick downsample function
# gives a dictionary with labels matching freqDict and values equal to downsampled versions of the input list of arrays
def downSamp(nArr,fd=freqDict):
    noiseDict = {}
    for label in fd.keys():
        f = fd[label]
        skipNum = int(defFreq / f) # force integer for indexing
        noiseDict[label] = []
        for i in range(len(nArr)):
            downArr = nArr[i][::skipNum]
            noiseDict[label].append(downArr)
    return noiseDict

# now to actually make the PSDs
# take in dict of all our signals, output PSD and frequency grid dicts with same labelling convention
# def makePSD(dict,fDict = freqDict):
#     PSDDict = {}
#     fGridDict = {}
#     for label in fDict.keys():
#         list = dict[label]
#         PSDDict[label] = []
#         fGridDict[label] = []
#         for i in range(len(list)):
#             fGrid,psd = welch(list[i],fs=freqDict[label],nperseg=defNper)
#             PSDDict[label].append(psd)
#             fGridDict[label].append(fGrid)
    
#     return PSDDict,fGridDict

# new func i guess?
def makePSD(dict, fDict=freqDict):
    PSDDict = {}
    fGridDict = {}
    for label in fDict.keys():
        arrList = dict[label]
        PSDDict[label] = []
        fGridDict[label] = []

        long_arrs = [a for a in arrList if len(a) >= defNper]
        short_arrs = [a for a in arrList if len(a) < defNper]

        # pool short arrays together; if combined they're long enough, keep them
        if short_arrs:
            combined = np.concatenate(short_arrs)
            if len(combined) >= defNper:
                long_arrs.append(combined)

        for arr in long_arrs:
            fGrid, psd = welch(arr, fs=freqDict[label], nperseg=defNper)
            PSDDict[label].append(psd)
            fGridDict[label].append(fGrid)

    return PSDDict, fGridDict

# now we want to average across arrays per frequency sample
# gives average across each dict label of above dictionaries
def PSDAverage(dict,fdict):
    PSDAvgDict = {}
    fAvgDict = {} # fGrid should be same across all list indices, but we condense so i can stop writing them
    for label in dict.keys():
        PSDSum = np.sum(np.array(dict[label]),axis=0)
        fSum = np.sum(np.array(fdict[label]),axis=0)
        # print(PSDSum)
        PSDAvgDict[label] = PSDSum / len(dict[label])
        fAvgDict[label] = fSum / len(fdict[label])
    return PSDAvgDict,fAvgDict

def decibel(signal,ref):
    return 10 * np.log10(signal/ref)