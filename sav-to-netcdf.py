# -*- coding: utf-8 -*-

__author__       = "Stefanie Feuerstein"
__version__      = "April 2020"
__maintainer__   = "S. Feuerstein"
__status__       = "Production"

# STEP 0 - load libraries
import netCDF4
from netCDF4 import Dataset  
import numpy as np           # numerical python
import numpy.ma as ma        # masked arrays
import gc                    # Garbage collector to clean memory
import datetime              # Date-time manage
import sys
import os
import scipy
from scipy import io
import scipy.interpolate    as spint
from   mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot    as plt
from   mpl_toolkits.basemap import maskoceans
import glob
import pandas as pd
from pyproj import Proj
from pyproj import transform
from scipy.interpolate import griddata
import datetime as dt
from datetime import date, time, timedelta, datetime
from netCDF4 import num2date, date2num
import matplotlib
from matplotlib import dates

## uncommand next two lines for flexible year and month entry
#year = str(raw_input("year eingeben >> "))
#month = str(raw_input("month eingeben >> "))


## define some basic variables 
year = 2009
years = str(year)
month = 11
months = str(month)
days = 30+1
direc = "aod_"+years+months
numdays = (np.arange(1, days, 1))


#create list of times
for day in numdays:
	from datetime import time, datetime, timedelta
	t = []
	def perdelta(start, end, delta):
		curr = start
		while curr < end:
			yield curr
			curr += delta

	for result in perdelta(datetime(year, month, day, 6, 00, 00), datetime(year, month, day, 16, 30, 0), timedelta(minutes=30)):
			t.append(result)



# Step 1: Create netcdf file with correct dimensions

# create NC file
	AOT_nc_file = direc+'/AOT_055_'+years+months+'0'+str(day)+'.nc'
	print AOT_nc_file
	root_grp = Dataset(AOT_nc_file, 'w', format='NETCDF4')
	root_grp.description = """Dataset with AOT at 550nm from instrument MSG Seviri provided by Jamie Banks, Leeds"""

# define dimensions
	root_grp.createDimension('lat',800)
	root_grp.createDimension('lon',1440)
	root_grp.createDimension('time', 21)

#define variables
	latitudes  = root_grp.createVariable('lat', 'f4', ('lat',))
	longitudes = root_grp.createVariable('lon', 'f4', ('lon',))
	times = root_grp.createVariable('time', 'f8', ('time',))

	aod_data   = root_grp.createVariable('aod_data', 'f4', ('time','lat', 'lon',), fill_value=-999.)

# define attributes
	root_grp.variables['lat'].standard_name = 'latitude'
	root_grp.variables['lon'].standard_name = 'longitude'
	latitudes.units  = 'degrees north'
	longitudes.units = 'degrees east'
	aod_data.standard_name = 'mean_aod_value'
	times.units = 'hours since 0001-01-01 00:00'
	times.calendar = 'gregorian'



#Fill in values for 'Latitude' and 'Longitude': 
#Load .SAV file with coordinates
	coords = scipy.io.readsav("grid_lat_lon_new.sav")  ## .sav file that includes the lat-lon grid of all .sav-files
	nlat = coords.latr
	nlon = coords.lonr

#add data to variables latitude / longitude and time variable
	xi = np.arange(min(nlon), max(nlon), 0.0625)
	xi = np.around(xi, decimals=3)
	yi = np.arange(min(nlat), max(nlat), 0.0625)
	yi = np.around(yi, decimals = 3)

	xj,yj = np.meshgrid(xi, yi)

	latitudes[:] = yi
	longitudes[:] = xi
	times[:] = date2num(t, units=times.units,calendar=times.calendar)

#____________________________________________________
# add data! assign to unlimited times variable each time step of a day
# create list of files in the folder

	savlist = glob.glob(direc+'/*.sav')
	col = day-1
#loop through list
	start = -1
	for file in savlist:
		start+=1
		end = start+1
		step = 1
		data = scipy.io.readsav(file)
		mean = data.mean_aod055_ir[:,col]
		points=np.vstack((nlon, nlat)).T
		values= mean
		wanted = (xj, yj)
		zi=griddata(points, values, wanted, method='nearest',fill_value=-999.)
		aod_data[start:end:step,:,:] = zi
	
	


	root_grp.close()


