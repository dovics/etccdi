from matplotlib import pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
from xclim.indices import frost_days
from utils import (
    merge_intermediate_post_process,
    range_era5_data_period,
    get_result_data_path,
    mean_by_region,
    merge_intermediate,
)
from plot import draw_latlon_map


# PR, Precipitation: Annual total precipitation.
indicator_name = "pr"


def process_pr(ds: xr.Dataset) -> xr.DataArray:
    pr = ds["pr"].sum(dim="time")
    pr.name = indicator_name
    return pr


def draw(df: pd.DataFrame, ax = None):
    cmap = plt.get_cmap("Greens")
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=cmap)
    plt.title("PR")



def calculate(process: bool = True):
    if process:
        range_era5_data_period("pr", process_pr, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))