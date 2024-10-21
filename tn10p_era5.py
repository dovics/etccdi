import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import tn10p
from pathlib import Path
from utils import (
    new_plot,
    merge_base_years,
    get_result_data_path,
    get_year_from_path,
    range_era5_data
)

base_ds = merge_base_years('tas').rename({"valid_time": "time"}) # TODO : 'tasmin'
t10 = percentile_doy(base_ds['t2m'], per=10, window=5).sel(percentiles=10)
   
def process_tn10p(file: Path):
    if not file.name.startswith('tas_'): # TDDO : 'tasmin'
        return
    ds = xr.open_dataset(file)
    ds = ds.rename({"valid_time": "time"})
    
    result = tn10p(ds['t2m'], t10, freq="YS")
    result.name = 'tn10p'
    result.to_dataframe().to_csv(get_result_data_path('tn10p', get_year_from_path(file.name)))

def draw_tn10p(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['latitude'].values
    lons = df['longitude'].values
    tn10p = df['tn10p'].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    TN10P = tn10p.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, TN10P, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Number of days with daily minimum temperature below the 10th percentile.',  orientation='vertical', pad=0.1)

    plt.title('ERA5 TN10P')
    plt.show()
    
if __name__ == '__main__':
    range_era5_data(process_tn10p)
    draw_tn10p(get_result_data_path("tn10p", "2000"))