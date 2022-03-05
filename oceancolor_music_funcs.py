import datetime as dt
import numpy as np
from netCDF4 import Dataset
from midiutil import MIDIFile

def get_oceancolor_data(year,month,lat,lons):
    beginday = (dt.datetime(year,month,1)-dt.datetime(year,1,1)).days + 1
    endday = (dt.datetime(year,month+1,1)-dt.datetime(year,1,1)).days if month != 12 else (dt.datetime(year+1,1,1)-dt.datetime(year,1,1)).days
    fn = 'https://oceandata.sci.gsfc.nasa.gov/opendap/SeaWiFS/L3SMI/%04d/%03d/S%04d%03d%04d%03d.L3m_MO_RRS_Rrs_%03d_9km.nc'
    wavelengths = [412,443,490,510,555,670]

    nc = Dataset(fn%(year,beginday,year,beginday,year,endday,wavelengths[0]))
    latind = np.argmin(np.abs(nc.variables['lat'][:]-lat))
    loninds = range(np.argmin(np.abs(nc.variables['lon'][:]-lons[0])),
                    np.argmin(np.abs(nc.variables['lon'][:]-lons[-1])))
    nc.close()
    ncs = [Dataset(fn%(year,beginday,year,beginday,year,endday,wv)) for wv in wavelengths]

    Rrs = np.array([nc.variables['Rrs_%03d'%wv][latind,loninds] for nc,wv in zip(ncs,wavelengths)])

    return Rrs

def make_midi(Rrs,output_file,scale_type='diatonic',ensemble='woodwind_sextet',start_pitch=10,tempo=120):

    if scale_type=='diatonic':
        scale = np.array([0,2,4,5,7,9,11])
    elif scale_type=='todi':
        scale = np.array([0,1,3,6,7,8,10])
    elif scale_type=='hungarian':
        scale = np.array([0,2,3,6,7,8,11])
    elif scale_type=='istrian':
        scale = np.array([0,1,3,4,6,7])

    if ensemble=='woodwind_sextet':
        instruments = [72,68,69,71,60,70]
    elif ensemble=='strings':
        instruments = [40,40,40,40,40,40]
    elif ensemble=='piano':
        instruments = [0,0,0,0,0,0]

    pitches = np.concatenate([scale+start_pitch+12*i for i in range(int((115+1-start_pitch)/12))])

    Rrs_int = (np.array(Rrs)/np.nanmax(np.array(Rrs))*len(pitches)-1).astype('int')

    MyMIDI = MIDIFile(len(Rrs_int),adjust_origin=False)
    MyMIDI.addTempo(0,0,tempo)

    for i in range(len(Rrs_int)):
        MyMIDI.addProgramChange(i, 0, 0, instruments[i])


    for i in range(len(Rrs_int)):
        times = np.concatenate([[0],np.where(np.diff(Rrs_int[i]))[0]+1])
        unique_pitches = pitches[Rrs_int[i]][times]
        durations = np.diff(np.concatenate([times,[len(Rrs_int[i])]]))

        for pitch,time,duration in zip(unique_pitches,times,durations):
            MyMIDI.addNote(i,0,pitch,time,duration,100)

    with open(output_file,"wb") as output_file:
        MyMIDI.writeFile(output_file)
