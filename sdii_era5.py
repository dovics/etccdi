import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import daily_pr_intensity
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data
)

indicator_name = "sdii"
def process_sdii(ds:xr.Dataset):
    result = daily_pr_intensity(ds['pr'])
    result.name = indicator_name
    return result
    
def draw_sdii(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    sdii = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    SDII = sdii.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, SDII, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='verage precipitation for days with daily precipitation above a given threshold.',  orientation='vertical', pad=0.1)
    plt.title('ERA5 SDII')
    plt.show()

if __name__ == '__main__':
    range_era5_data("pr", process_sdii)
    draw_sdii(get_result_data_path(indicator_name, "2000"))