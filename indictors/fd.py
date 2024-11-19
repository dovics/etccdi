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


# FD, Number of frost days: Annual count of days when TN (daily minimum temperature) < 0oC.
indicator_name = "fd"


def process_fd(ds: xr.Dataset) -> xr.DataArray:
    fd = (ds["tasmin"] - 273.15 < 0).sum(dim="time")
    fd.name = indicator_name
    return fd


def draw(df: pd.DataFrame, ax = None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax)
    plt.title("FD")



def calculate(process: bool = True):
    if process:
        range_era5_data_period("tasmin", process_fd, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
