import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import days_over_precip_thresh
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    merge_base_years,
    range_era5_data
)

base_ds = merge_base_years('pr')
r95 = percentile_doy(base_ds['pr'], per=5).sel(percentiles=95)
indicator_name = "r95p"
def process_r95p(ds:xr.Dataset):
    result = days_over_precip_thresh(ds['pr'],r95, freq="YS")
    result.name = indicator_name
    return result
    
def draw_r95p(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    r95p = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    R95P = r95p.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, R95P, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Number of days with daily minimum temperature below the 10th percentile.',  orientation='vertical', pad=0.1)
    plt.title('ERA5 R95P')
    plt.show()

if __name__ == '__main__':
    range_era5_data("pr", process_r95p)
    draw_r95p(get_result_data_path(indicator_name, "2000"))