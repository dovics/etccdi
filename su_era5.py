from matplotlib import pyplot as plt 
import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
from utils import (
    new_plot,
    range_era5_data,
    get_result_data_path,
    get_year_from_path
)
import cartopy.crs as ccrs
from xclim.indices import maximum_consecutive_tx_days

# SU, Number of summer days: Annual count of days when TX (daily maximum temperature) > 25oC.
indicator_name = "su"
def process_su(ds: xr.Dataset):
    su = maximum_consecutive_tx_days(ds['tasmax'], freq="YS")
    su.name = indicator_name
    return su

def draw_su(csv_path: Path):
    df = pd.read_csv(csv_path)

    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    t2m = df[indicator_name].values
    fig, ax = new_plot(lons, lats)

    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    T2M = t2m.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, T2M, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Number of summer  days',  orientation='vertical', pad=0.1)

    plt.title('ERA5 SU')
    plt.show()

if __name__ == '__main__':
    range_era5_data("tasmax", process_su)
    draw_su(get_result_data_path(indicator_name, "2000"))