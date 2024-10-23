import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import tx_max
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data
)

# why not tasmaxmin???????????????

indicator_name = "txx"
def process_txx(ds: xr.Datasmaxet):
    result = tx_max(ds['tasmax'], freq="YS")
    result.name = indicator_name
    return result

def draw_txx(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    txx = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    TXX = txx.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, TXX, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Maximum of daily maximum temperature.',  orientation='vertical', pad=0.1)
    plt.title('ERA5 TXX')
    plt.show()
    
if __name__ == '__main__':
    range_era5_data("tasmax", process_txx)
    draw_txx(get_result_data_path(indicator_name, "2000"))