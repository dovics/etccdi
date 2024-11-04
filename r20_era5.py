import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import wetdays
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data,
    draw_latlon_map,
    range_era5_data_period,
    mean_by_region
)

indicator_name = "r10"
def process_r10(ds:xr.Dataset):
    result = wetdays(ds['pr'],thresh='20.0 mm/day')
    result.name = indicator_name
    return result.sum(dim="time")
    
def draw_r10(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 R10')
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("pr", process_r10,mean_by_region)
    draw_r10(get_result_data_path(indicator_name, "2000"))  