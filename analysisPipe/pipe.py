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
halfWIndex = winHalfWidth*sampFreq
voltCon = 5/16383

sampFreq = inter._get_int(f"Sampling frequency? (press return for default = {sampFreq} Hz):", sampFreq)
nper = inter._get_int(f"Number of points per PSD segment? (press return for default = {nper}): ", nper)
winHalfWidth = inter._get_float(f"Half width of event window? (press return for default = {winHalfWidth} seconds): ")