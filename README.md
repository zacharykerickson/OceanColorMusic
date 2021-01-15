# OceanColorMusic
Code to translate ocean color into music

Contents:

get_oceancolor_data.py: Code to load in ocean color data from NASA internet serves and save it as csv, txt, or json file

convert_data.py: Code to convert data into a MIDI file

Sample usage (after opening Terminal and navigating to folder where files are stored):

  python get_oceancolor_data.py 2000 7 0 -30 -20 EqAtl.json
  
  python convert_data.py EqAtl.json EqAtl.mid
  
Will result in the following files:

  EqAtl.json, containing ocean color data from the SeaWifs satellite at 6 standard wavelengths from July (month #7) of 2000, at 0˚N, -30 to -20 ˚E
  
  EqAtl.mid, a MIDI file with default scale (diatonic) and range (C2 to C7)
  
  
Note:

As of yet, there are few checks, so if you input something wrong the code will likely just fail with an indecipherable warning. Similarly, you need the right Python packes installed on your computer. Standard packages used are numpy, sys, os, and json. Less standard (but still easy to find using standard software) packages are midiutil, datetime, and netCDF4.
