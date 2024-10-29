import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import cold_spell_duration_index
from pathlib import Path
from utils import (
    new_plot,
    merge_base_years,
    get_result_data_path,
    range_era5_data
)

base_ds = merge_base_years('tasmin')
cs_di = percentile_doy(base_ds['tasmin'], per=10).sel(percentiles=10)

indicator_name = "csdi"
def process_csdi(ds: xr.Dataset):
    result = cold_spell_duration_index(ds['tasmin'], cs_di, freq="YS")
    result.name = indicator_name
    return result

def draw_csdi(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    csdi = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    CSDI = csdi.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, CSDI, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Annual count of days with at least 6 consecutive days when TN < 10th percentile',  orientation='vertical', pad=0.1)
    plt.title('ERA5 CSDI')
    plt.show()
    
if __name__ == '__main__':
    range_era5_data("tasmin", process_csdi)
    draw_csdi(get_result_data_path(indicator_name, "2000"))