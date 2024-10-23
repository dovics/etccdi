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


# ID, Number of icing days: Annual count of days when TX (daily maximum temperature) < 0oC.
indicator_name = "id"
def process_id(ds: xr.Dataset) -> xr.DataArray:
    id = (ds['tasmax'] - 273.15 < 0).sum(dim='time')
    id.name = indicator_name
    return id

def draw_id(csv_path: Path):
    df = pd.read_csv(csv_path)

    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    indicator_name = df[indicator_name].values
    fig, ax = new_plot(lons, lats)

    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    ID = indicator_name.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, ID, levels=15, cmap='coolwarm_r', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Number of ice days',  orientation='vertical', pad=0.1)

    plt.title('ERA5 ID')
    plt.show()

if __name__ == '__main__':
    range_era5_data("tasmax", process_id)
    draw_id(get_result_data_path(indicator_name, "2000"))