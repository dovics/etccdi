import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import max_n_day_precipitation_amount
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data
)

indicator_name = "rx5day"
def process_rx5day(ds:xr.Dataset):
    result = max_n_day_precipitation_amount(ds['pr'],window=5)
    result.name = indicator_name
    return result
    
def draw_rx5day(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    rx5day = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    RX5DAY = rx5day.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, RX5DAY, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Number of days with daily minimum temperature below the 10th percentile.',  orientation='vertical', pad=0.1)
    plt.title('ERA5 RX5DAY')
    plt.show()

if __name__ == '__main__':
    range_era5_data("pr", process_rx5day)
    draw_rx5day(get_result_data_path(indicator_name, "2000"))