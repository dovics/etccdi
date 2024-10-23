from matplotlib import pyplot as plt 
import xarray as xr
import numpy as np
import pandas as pd
from xclim.indices import daily_temperature_range
from pathlib import Path
from utils import (
    new_plot,
    range_era5_data,
    get_result_data_path
)
import cartopy.crs as ccrs
from download.era5 import get_era5_data

indicator_name = "dtr"
def process_dtr(ds: xr.Dataset) -> xr.DataArray:
    ds = ds.sortby('time')
    
    dtr = daily_temperature_range(ds['tasmin'], ds['tasmax'])
    dtr.name = indicator_name
    
    return dtr

def draw_dtr(csv_path: Path):
    df = pd.read_csv(csv_path)

    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    dtr = df[indicator_name].values
    fig, ax = new_plot(lons, lats)

    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    DTR= dtr.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, DTR, levels=15, cmap='coolwarm_r', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Monthly mean difference between TX and TN',  orientation='vertical', pad=0.1)

    plt.title('ERA5 DTR')
    plt.show()

if __name__ == '__main__':
    get_era5_data(["tasmax", "tasmin"])
    range_era5_data(["tasmax", "tasmin"], process_dtr)
    draw_dtr(get_result_data_path(indicator_name, "2000"))