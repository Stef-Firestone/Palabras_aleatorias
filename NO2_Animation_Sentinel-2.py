#### creates an animation of NO2 variations derived from the SENTINEL-5 NO2 product. Used product: S5P_NRTI_L2__NO2____*.nc

## Create animation

import numpy as np
import glob
from netCDF4 import Dataset
from scipy import interpolate
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from netCDF4 import num2date
from matplotlib.colors import LogNorm


def make_figure():
    fig = plt.figure(figsize=(4, 5))
    ax = fig.add_subplot(1, 1, 1)
    map = Basemap(projection='merc',llcrnrlon=6,llcrnrlat=46,urcrnrlon=18,urcrnrlat=55,resolution='i')

    # generate a basemap with country borders, oceans and coastlines
    map.drawcoastlines()
    map.drawstates()
    map.drawcountries()
    return fig, ax

NO2 = sorted(glob.glob("/Path/to/Sentinel-5-files/S5P*.nc"))


frames = len(NO2)        # Number of frames
fig, ax = make_figure()
def draw(frame, add_colorbar):
    fig, ax = make_figure()

    print(NO2[frame])
    no2_fname = Dataset(NO2[frame])
    time = no2_fname['PRODUCT'].variables['time'][:][0]
    date = num2date(times=time ,units=u'seconds since 2010-01-01 00:00:00',calendar='standard')
    timestampStr = date.strftime("%d-%b-%Y")
    no2 = no2_fname['PRODUCT'].variables['nitrogendioxide_tropospheric_column_precision'][0,:,:].data
    no2_micro = no2*1000000
    map = Basemap(projection='merc',llcrnrlon=6,llcrnrlat=46,urcrnrlon=18,urcrnrlat=55,resolution='i')
    lat = no2_fname['PRODUCT'].variables['latitude'][0,:,0]
    lon = no2_fname['PRODUCT'].variables['longitude'][0,0,:]
    lons,lats= np.meshgrid(lon,lat) # for this dataset, longitude is 0 through 360, so you need to subtract 180 to properly display on map
    x,y = map(lons,lats)
    cmap = plt.get_cmap('jet')
    cmap.set_under('k', alpha=0)
    cmap.set_over('k', alpha=0)
    no2_map = map.pcolormesh(x,y,np.squeeze(no2_micro[:,:]), cmap=cmap, norm=LogNorm(),vmin=1, vmax=500)
    cb = map.colorbar(no2_map,"bottom", size="5%", pad="2%")
    map.drawcountries()
    plt.title(timestampStr)
    cb.set_label(u'N=\u2082 (\u03bcmol/m\u00B2)')
    plt.close(fig)
    return map


def init():
    return draw(0, add_colorbar=True)


def animate(frame):
    return draw(frame, add_colorbar=False)


ani = animation.FuncAnimation(fig, animate, frames, interval=200, blit=False,
                              init_func=init, repeat=False)
ani.save('NO2.mp4', writer=animation.FFMpegWriter(fps=1))

plt.close(fig)
