import xarray as xr
from matplotlib import pyplot as plt 
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import maximum_consecutive_wet_days
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data,
    clip_dataset
)

indicator_name = "cwd"
def process_cwd(ds:xr.Dataset):
    result = maximum_consecutive_wet_days(ds['pr'], thresh='1 mm/day')
    result.name = indicator_name
    return result
    
def draw_cwd(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    cwd = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    CWD = cwd.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, CWD, levels=15, cmap='coolwarm_r', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Maximum consecutive wet days.',  orientation='vertical', pad=0.1)
    plt.title('ERA5 CWD')
    plt.show()

if __name__ == '__main__':
    range_era5_data("pr", process_cwd)
    draw_cwd(get_result_data_path(indicator_name, "2000"))