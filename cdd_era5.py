import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import maximum_consecutive_dry_days
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data
)

indicator_name = "cdd"
def process_cdd(ds:xr.Dataset):
    result = maximum_consecutive_dry_days(ds['pr'],thresh='1 mm/day')
    result.name = indicator_name
    return result
    
def draw_cdd(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    cdd = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    CDD = cdd.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, CDD, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Maximum consecutive dry days.',  orientation='vertical', pad=0.1)
    plt.title('ERA5 CDD')
    plt.show()

if __name__ == '__main__':
    range_era5_data("pr", process_cdd)
    draw_cdd(get_result_data_path(indicator_name, "2000"))