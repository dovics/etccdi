import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import wetdays
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data
)

indicator_name = "r10"
def process_r10(ds:xr.Dataset):
    result = wetdays(ds['pr'],thresh='10.0 mm/day')
    result.name = indicator_name
    return result
    
def draw_r10(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    r10 = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    R10 = r10.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, R10, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Annual count of days when PRCP≥ 10mm',  orientation='vertical', pad=0.1)
    plt.title('ERA5 R10')
    plt.show()

if __name__ == '__main__':
    range_era5_data("pr", process_r10)
    draw_r10(get_result_data_path(indicator_name, "2000"))