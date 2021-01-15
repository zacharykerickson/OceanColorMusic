import numpy as np
from midiutil import MIDIFile
import sys
import os

version = '0.0'
contact = 'zachary.k.erickson@nasa.gov'
usage   = 'Enter input file, output file, scale (opt), lowest pitch (MIDI-format; opt), and highest pitch (MIDI_format opt)'
example = ['Example: python convert_data.py in.json out.mid diatonic 36 96','Same as: python convert_data.py in.json out.mid']
restrictions = ['Input file must be .csv, .txt, or .json.','scale types recognized: diatonic, todi, hungarian, istrian, chromatic, pentatonic']

if len(sys.argv)==1:
    print('')
    print('Version: %s, Contact: %s'%(version,contact))
    print(usage)
    for ex in example:
        print(ex)
    print('Restrictions:')
    for r in restrictions:
        print(r)
    print('')
    sys.exit()

input_file = sys.argv[1]
output_file = sys.argv[2]
if len(sys.argv)>3:
    use_scale = sys.argv[3]
else:
    print('No scale specified, using diatonic')
    use_scale = 'diatonic'
if len(sys.argv)>4:
    lowest_pitch = int(sys.argv[4])
else:
    print('No lowest pitch specified, using C2')
    lowest_pitch = 36
if len(sys.argv)>5:
    highest_pitch = int(sys.argv[5])
else:
    print('No highest pitch specified, using C7')
    highest_pitch = 96

# describe valid notes
diatonic = np.array([0,2,4,5,7,9,11])
todi = np.array([0,1,3,6,7,8,10])
hungarian = np.array([0,2,3,6,7,8,11])
istrian = np.array([0,1,3,4,6,7])
chromatic = np.arange(12)
pentatonic = np.array([0,2,5,7,9])

ext = os.path.splitext(input_file)
if ext=='.csv' or '.txt':
    Rrs = np.loadtxt(input_file,delimiter=',')
elif ext=='.json':
    import json
    json_data = json.load(open(input_file,'r'))
    Rrs = np.array([json_data[key] for key in json_data.keys()]) 
else:
    sys.exit('Do not recognize file type: %s'%ext)

# set available pitches and discretize Rrs data
if use_scale=='chromatic':
    scale=chromatic
elif use_scale=='diatonic':
    scale=diatonic
elif use_scale=='pentatonic':
    scale=pentatonic
elif use_scale=='todi':
    scale=todi
elif use_scale=='hungarian':
    scale=hungarian
elif use_scale=='istrian':
    scale=istrian
else:
    print('scale type "%s" not understood (valid types: "diatonic", "todi", "hungarian", "istrian", "chromatic", and "pentatonic"); using a diatonic scale')
    scale=diatonic
pitches = np.concatenate([scale+lowest_pitch+12*i for i in range(int((highest_pitch-lowest_pitch)/12))])

Rrs_int = (np.array(Rrs)/np.nanmax(np.array(Rrs))*len(pitches)-1).astype('int')

# make midi file
tempo = 120 # bpm
MyMIDI = MIDIFile(len(Rrs_int))
MyMIDI.addTempo(0,0,tempo)
instruments = [72,68,69,71,60,70] # flute, oboe, english horn, clarinet, french horn, bassoon

for i in range(len(Rrs_int)):
    MyMIDI.addProgramChange(i, 0, 0, instruments[i])

for i in range(len(Rrs_int)):
    times = np.concatenate([[0],np.where(np.diff(Rrs_int[i]))[0]+1])
    unique_pitches = pitches[Rrs_int[i]][times]
    durations = np.diff(np.concatenate([times,[len(Rrs_int[i])]]))
    for pitch,time,duration in zip(unique_pitches,times,durations):
        MyMIDI.addNote(i,0,pitch,time,duration,100)

# save midi file
with open(output_file,"wb") as o:
    MyMIDI.writeFile(o)
