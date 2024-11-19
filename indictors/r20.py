import xarray as xr
from matplotlib import pyplot as plt 
from xclim.indices import wetdays
import pandas as pd
from utils import (
    get_result_data_path,
    merge_intermediate_post_process,

    range_era5_data_period,
    mean_by_region,
    merge_intermediate
)
from plot import draw_latlon_map
indicator_name = "r20"
def process_r20(ds:xr.Dataset):
    result = wetdays(ds['pr'],thresh='20.0 mm/day')
    result.name = indicator_name
    return result.sum(dim="time")
    
def draw(df: pd.DataFrame, ax = None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax)
    plt.title('R20')

def calculate(process: bool = True):
    if process:
        range_era5_data_period("pr", process_r20,mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))