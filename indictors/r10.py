import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
from xclim.indices import wetdays
from utils import (
    merge_intermediate_post_process,
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    merge_intermediate
)
from plot import draw_latlon_map

indicator_name = "r10"
def process_r10(ds:xr.Dataset):
    result = wetdays(ds['pr'],thresh='10.0 mm/day')
    result.name = indicator_name
    return result.sum(dim="time")
    
def draw(df: pd.DataFrame, ax = None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax)
    plt.title(' R10')
    
def calculate(process: bool = True):
    if process:
        range_era5_data_period("pr", process_r10, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))