from matplotlib import pyplot as plt 
import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
from utils import (
    new_plot,
    range_era5_data,
    get_result_data_path
)
import cartopy.crs as ccrs


# FD, Number of frost days: Annual count of days when TN (daily minimum temperature) < 0oC.
indicator_name = "fd"
def process_fd(ds: xr.Dataset) -> xr.DataArray:
    fd = (ds['tasmin'] - 273.15 < 0).sum(dim='time')
    fd.name = indicator_name
    return fd

def draw_fd(csv_path: Path):
    df = pd.read_csv(csv_path) 

    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    t2m = df[indicator_name].values
    fig, ax = new_plot(lons, lats)

    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    T2M = t2m.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, T2M, levels=15, cmap='coolwarm_r', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Number of frost days',  orientation='vertical', pad=0.1)

    plt.title('ERA5 FD')
    plt.show()

if __name__ == '__main__':
    range_era5_data("tasmin", process_fd)
    draw_fd(get_result_data_path(indicator_name, "2000"))