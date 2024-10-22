import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import tx90p
from pathlib import Path
from utils import (
    new_plot,
    merge_base_years,
    get_result_data_path,
    range_era5_data
)

# tasmax
base_ds = merge_base_years('tasmax')
t90 = percentile_doy(base_ds['tasmax'], per=10, window=5).sel(percentiles=90)

indicator_name = "tn90p"
def process_tx90p(ds: xr.Dataset):
    result = tx90p(ds['tasmax'], t90, freq="YS") 
    result.name = indicator_name
    return result

def draw_tx90p(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    tx10p = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    TX90P = tx10p.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, TX90P, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Number of days with daily minimum temperature below the 10th percentile.',  orientation='vertical', pad=0.1)
    plt.title('ERA5 TX90P')
    plt.show()
    
if __name__ == '__main__':
    range_era5_data("tasmax", process_tx90p)
    draw_tx90p(get_result_data_path(indicator_name, "2000"))