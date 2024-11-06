import xarray as xr
from matplotlib import pyplot as plt 
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import maximum_consecutive_wet_days
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data,
    range_era5_data_period,
    mean_by_region,
    draw_latlon_map
)
default_value = 10
indicator_name = "cwd"
def process_cwd(ds:xr.Dataset):
    year = ds['time'].dt.year.values.max()
    new_time = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq='D')
    ds = ds.reindex(time=new_time, fill_value=default_value)

    result = maximum_consecutive_wet_days(ds['pr'], thresh='1 mm/day')
    result.name = indicator_name
    return result
    
def draw_cwd(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True, cmap="coolwarm_r")
    plt.title('ERA5 CWD')
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("pr", process_cwd, mean_by_region)
    draw_cwd(get_result_data_path(indicator_name, "2022"))