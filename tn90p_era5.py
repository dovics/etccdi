import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import tn90p
from pathlib import Path
from utils import (
    new_plot,
    merge_base_years,
    get_result_data_path,
    range_era5_data
)

# why not tasmin???????????????
base_ds = merge_base_years('tasmin')
t90 = percentile_doy(base_ds['tasmin'], per=90, window=5).sel(percentiles=90)

indicator_name = "tn90p"
def process_tn90p(ds: xr.Dataset):
    result = tn90p(ds['tasmin'], t90, freq="YS") 
    result.name = indicator_name
    return result

def draw_tn90p(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    tn90p = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    TN90P = tn90p.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, TN90P, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Number of days with daily minimum temperature below the 10th percentile.',  orientation='vertical', pad=0.1)
    plt.title('ERA5 TN90P')
    plt.show()
    
if __name__ == '__main__':
    range_era5_data("tasmin", process_tn90p)
    draw_tn90p(get_result_data_path(indicator_name, "2000"))