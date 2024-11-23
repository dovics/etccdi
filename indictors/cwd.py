import xarray as xr
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from xclim.indices import maximum_consecutive_wet_days
from utils import (
    get_origin_result_data_path,
    range_era5_data_period,
    mean_by_region,
    reindex_ds_to_all_year,
    merge_intermediate_post_process,
    merge_intermediate,
)

from plot import draw_latlon_map, add_title
from config import pr_colormap

default_value = 0
indicator_name = "cwd"
unit = "d"

def process_cwd(ds: xr.Dataset):
    ds = reindex_ds_to_all_year(ds, default_value)
    result = maximum_consecutive_wet_days(ds["pr"], thresh="1 mm/day")
    result.name = indicator_name
    return result


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=pr_colormap)
    add_title(ax, f"CWD (${unit}$)")

def calculate(process: bool = True):
    if process:
        range_era5_data_period("pr", process_cwd, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
