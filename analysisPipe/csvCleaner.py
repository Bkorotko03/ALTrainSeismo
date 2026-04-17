# helper script from work in csvCleaner.ipynb
import pandas as pd
import numpy as np
import csv

# set up windowing params globally, these can and will be overwritten in interactive
sampFreq = 100
window_half_width = 5 # enforce that this is seconds somehow
halfWIndex = window_half_width * sampFreq
defVoltCon = 5/16383

# extract big numpy arrays from csv files
def arrayExtract(fpath,voltCon=defVoltCon,endCut=120,fs=100):# this cuts 2 minutes off of the end of each run, need to be long now
    # import csv and prep colums
    DF = pd.read_csv(fpath)
    DF['seconds'] = pd.to_numeric(DF['seconds'],errors='coerce')
    DF['sensor'] = pd.to_numeric(DF['sensor'],errors='coerce')
    DF = DF.dropna(subset=['seconds']).reset_index(drop=True) # kill rows with nans

    # now want to make chops off ends
    endIdx = endCut*fs # endCut in seconds, fs in Hz
    DFSecs = DF['seconds'].to_numpy(dtype=float)
    DFSecs = DFSecs[endIdx:-endIdx]
    DFSens = DF['sensor'].to_numpy(dtype=float)
    DFSens = DFSens[endIdx:-endIdx]
    DFVolt = DFSens * voltCon

    return DFSecs,DFSens,DFVolt

# copilot generated function to convert csv from clicker into seconds elapsed

def utcSecondsConv(csv_path, sort_ascending=True):
    """
    Parse lines like: HH:MM:SS.s,UTC
    Return NumPy array of seconds elapsed since 00:00:00 UTC.
    """
    seconds = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            # Keep only rows that look like: time,UTC
            if len(row) < 2 or row[1].strip().upper() != "UTC":
                continue

            t = row[0].strip()
            parts = t.split(":")
            if len(parts) != 3:
                continue

            hh = int(parts[0])
            mm = int(parts[1])
            ss = float(parts[2])   # supports fractional seconds

            seconds.append(hh * 3600 + mm * 60 + ss)

    arr = np.array(seconds, dtype=float)
    if sort_ascending:
        arr = np.sort(arr)
    return arr

# want to pull indexes from the UTC event times
def eventIdx(secs,clicker):
    idxArr = []
    for event in clicker:
        eventIdx = np.searchsorted(secs,event)
        idxArr.append(eventIdx)
    return np.array(idxArr)

# pull windows from inputted array into noise and signal
def windowMaker(arr,idxarr,halfWIndex=halfWIndex):
    # kind of a big function but it should output lists of arrays with event and background segregated
    # first need to make some cutoff indices
    noiseWIndex = []
    eventWIndex = []
    n = len(arr)

    # now we construct prelim event windows
    for idx in idxarr:
        low = max(0,int(idx-halfWIndex))
        high = min(n-1,int(idx+halfWIndex))
        eventWIndex.append([low,high])
    
    # then here we merge if any overlap
    eventWIndex.sort(key=lambda w: w[0])
    merged = []
    for low, high in eventWIndex:
        if not merged or low > merged[-1][1] + 1:
            merged.append([low,high])
        else:
            merged[-1][1] = max(merged[-1][1],high)
    
    eventWIndex = merged

    # now the remaining values are all background noise
    cursor = 0
    for low,high in eventWIndex:
        if cursor < low:
            noiseWIndex.append([cursor,low-1])
        cursor = high + 1 
    
    if cursor <= n-1:
        noiseWIndex.append([cursor,n-1])
    
    # enforce these windows upon the voltage and seconds arrs
    noiseArrs = []
    for low,high in noiseWIndex:
        noiseArrs.append(arr[low:high])
    eventArrs = []
    for low,high in eventWIndex:
        eventArrs.append(arr[low:high])

    return eventArrs,noiseArrs