import numpy as np
import datetime as dt
from netCDF4 import Dataset
import sys
import os

version = '0.0'
contact = 'zachary.k.erickson@nasa.gov'
usage   = 'Enter year, month (num), latitude, starting longitude, ending longitude, output file'
example = ['Example: python get_oceancolor_data.py 2000 7 0 -30 -20 out.json']
restrictions = ['Output file must be .txt, .csv, or .json.']

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

year = int(sys.argv[1])
month = int(sys.argv[2])
lat = float(sys.argv[3])
lon_start = float(sys.argv[4])
lon_end = float(sys.argv[5])
output_file = sys.argv[6]

#year=2000
#month=7
#lat=10
#lon_start=59.2
#lon_end=69.1
#output_file = 'test.csv'

# set variables
beginday = (dt.datetime(year,month,1)-dt.datetime(year,1,1)).days + 1
endday = (dt.datetime(year,month+1,1)-dt.datetime(year,1,1)).days if month != 12 else (dt.datetime(year+1,1,1)-dt.datetime(year,1,1)).days
fn = 'https://oceandata.sci.gsfc.nasa.gov/opendap/SeaWiFS/L3SMI/%04d/%03d/S%04d%03d%04d%03d.L3m_MO_RRS_Rrs_%03d_9km.nc'
wavelengths = [412,443,490,510,555,670]

# find indices to use for given latitude and longitude
print('Finding indices...',end=' ')
nc = Dataset(fn%(year,beginday,year,beginday,year,endday,wavelengths[0]))
latind = np.argmin(np.abs(nc.variables['lat'][:]-lat))
loninds = range(np.argmin(np.abs(nc.variables['lon'][:]-lon_start)),
                np.argmin(np.abs(nc.variables['lon'][:]-lon_end)))

# download data
Rrs = ();
print('Downloading data...',end=' ')
for wv in wavelengths:
    print(wv,end=' ')
    nc = Dataset(fn%(year,beginday,year,beginday,year,endday,wv))
    Rrs += (nc.variables['Rrs_%03d'%wv][latind,loninds],)
    if np.any(np.ma.getmask(Rrs[-1])):
        sys.exit('Persistent clouds in part of scene...quitting program.')

ext = os.path.splitext(output_file)
if ext=='.csv' or 'txt':
    np.savetxt(output_file,np.array(Rrs),delimiter=',')
elif ext=='.json':
    import json
    data_dict = dict(zip(wavelengths,np.array(Rrs).tolist()))
    with open(output_file,'w') as json_file:
        json.dump(data_dict,json_file)
