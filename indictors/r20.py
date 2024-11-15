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
    merge_intermediate_post_process,
    draw_latlon_map,
    range_era5_data_period,
    mean_by_region
)

indicator_name = "r20"
def process_r20(ds:xr.Dataset):
    result = wetdays(ds['pr'],thresh='20.0 mm/day')
    result.name = indicator_name
    return result.sum(dim="time")
    
def draw_r10(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 R20')
    plt.show()

def calculate():
    range_era5_data_period("pr", process_r20,mean_by_region)
    df = merge_intermediate_post_process(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))