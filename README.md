# ALTrainSeismo
Code for our Loyola PHYS 338 SP 2026 (Advanced Lab) semester long project. We hope to characterize the seismic noice induced by Chicago light rail using Arduino to construct a PSD. There may be other READMEs in the subdirs here, will certainly not be consistent.
## Structure
Datalogger scripts are to be flashed to Arduinos, with weak not requiring true location lock to start recording.\
ALProjNotes *should* contain working notes for the project, but is deprecated.\
SDCardOut contains three directories for each detector CSV output.\
analysisPipe contains the Jupyter notebooks and helper scripts to compute the PSD estimates for a given observational run.\
circuitDiagrams contains different files describing the configuration of the amplifier circuit.\
clickerFiles is for the output of manually produced CSV files with the times (in UTC) of events.\
paperThings is figures and other things useful for writing the paper.\
testsAndSuch is self explanatory.\
## Operation
Flash each Arduino with the Data logger (strong preferred, but for indoors weak may be required).\
Connect SD card and GPS antenna to detector, ensure all amplifier connections are strong.\
Give her power.\
4 single beeps to set up and attempt GPS fix.\
1 double beep after to confirm GPS fix and recording start.\
Let it ride.

## Locations
So we need to make sure that we have dedicated locations for each of the detectors:\
UNO goes under the train, DOS goes on the monolith, and TRES will go into the dome.

## Caveats
Note that the datalogger scripts require the year to be between 2025-2027 or else nothing will be recorded. To fix, change the condition for creating the file.