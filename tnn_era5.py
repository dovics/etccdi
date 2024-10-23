import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import tn_min
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data
)

# why not tasminmin???????????????

indicator_name = "tnn"
def process_tnn(ds: xr.Datasminet):
    result = tn_min(ds['tasmin'], freq="YS")
    result.name = indicator_name
    return result

def draw_tnn(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    tnn = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    TNN = tnn.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, TNN, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Minimum of daily minimum temperature.',  orientation='vertical', pad=0.1)
    plt.title('ERA5 TNN')
    plt.show()
    
if __name__ == '__main__':
    range_era5_data("tasmin", process_tnn)
    draw_tnn(get_result_data_path(indicator_name, "2000"))