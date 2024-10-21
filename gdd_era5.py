import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import growing_degree_days
from pathlib import Path
from utils import (
    new_plot,
    merge_base_years,
    get_result_data_path,
    get_year_from_path,
    range_era5_data
)

indicator_name = "gdd"
def process_gdd(ds: xr.Dataset):
    # ds['t2m'].values=ds['t2m'].values-273.15
    # print(ds['t2m'].values)
    
    result = growing_degree_days(ds['tas'], thresh="0 degC", freq="YS")
    result.name = indicator_name
    return result


def draw_gdd(csv_path: Path):
    df = pd.read_csv(csv_path)
    # 提取经纬度和温度
    lats = df['lat'].values
    lons = df['lon'].values
    gdd = df[indicator_name].values
    fig, ax = new_plot(lons, lats)
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    GDD = gdd.reshape(LON.shape)
    contour = ax.contourf(LON, LAT, GDD, levels=15, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour, label='Effective growing degree days',  orientation='vertical', pad=0.1)

    plt.title('ERA5 GDD')
    plt.show()
    

if __name__ == '__main__':
    range_era5_data("tas", process_gdd)
    draw_gdd(get_result_data_path(indicator_name, "2000"))