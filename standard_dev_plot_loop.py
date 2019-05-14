import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

#define fucntion for calcuting the DMI and std_dev
def DMI(DS):
    sst=xr.open_dataset(DS).tos
    sst=sst.assign_coords(lon=(sst.lon % 360)).roll(lon=180, roll_coords=True)#get so 180 is central longitude
    climatology_mean=sst.groupby('time.month').mean('time')
    ssta=sst.groupby('time.month')-climatology_mean
    #detrend data with globally averaged sst
    sstade=ssta.rolling(time=264,center=True)
    sstade_TS=sstade.mean()#this timeseries is detreneded at every point individually
    # remove years with nan
    sstade_nan=sstade_TS.dropna('time',how='all')#this gets rid of all the years with nan ie the years consumed in the rolling average
    ssta=ssta-sstade_nan
    WTIO=ssta.sel(lat=slice(-10,10),lon=slice(50,70)).mean(['lat','lon'])
    SETIO=ssta.sel(lat=slice(-10,0),lon=slice(90,110)).mean(['lat','lon'])
    DMI=WTIO-SETIO
    std_dev=DMI.groupby('time.month').std(dim=('time'), keep_attrs=True)
    return std_dev
#define function for getting root mean square error
def rmse(predictions, targets):
    return np.sqrt(((np.array(predictions) - np.array(targets)) ** 2).mean())
#get observations as a varibale to use in RMSE calc
obs_std = DMI('dir/HadISST.nc')
#get list of files to iterate through
files = glob.glob('some_dir_with_all_files/*.nc')
#plot figure and start loop
plt.figure()
for i, file in enumerate(files):
    ax = plt.subplot(len(files), 1, i+1)
    std = DMI(file)
    RMSerror = rmse(std, obs_std)
    print (min(std), file)
    plt.imshow([std], vmin=0.180911, vmax=1.362, cmap = 'jet')
    plt.ylabel(str(os.path.splitext(os.path.basename(file))[0].rsplit('_tos', 1)[0]), labelpad=33, rotation=0)
    plt.yticks([])
    plt.xticks([])
    plt.text(12,0.4, str(RMSerror))
plt.xticks(range(0, 12, 1), ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))
plt.suptitle('Standard deviation by month of DMI in CMIP5')
plt.show()
