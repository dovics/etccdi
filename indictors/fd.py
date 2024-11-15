from matplotlib import pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
from xclim.indices import frost_days
from utils import (
    merge_intermediate_post_process,
    range_era5_data_period,
    get_intermediate_data,
    get_result_data_path,
    mean_by_region,
    draw_latlon_map,
    get_result_data,
)


import cartopy.crs as ccrs


# FD, Number of frost days: Annual count of days when TN (daily minimum temperature) < 0oC.
indicator_name = "fd"


def process_fd(ds: xr.Dataset) -> xr.DataArray:
    fd = (ds["tasmin"] - 273.15 < 0).sum(dim="time")
    fd.name = indicator_name
    return fd


def draw_fd(df: pd.DataFrame):
    draw_latlon_map(df, indicator_name, clip=True)
    plt.title("ERA5 FD")
    plt.show()


def calculate():
    range_era5_data_period("tasmin", process_fd, mean_by_region)
    df = merge_intermediate_post_process(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
