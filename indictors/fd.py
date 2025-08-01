import xarray as xr

import pandas as pd

from utils import (
    merge_intermediate_post_process,
    range_data_period,
    get_origin_result_data_path,
    mean_by_region,
    merge_intermediate,
)
from plot import draw_latlon_map, add_title
from config import tas_colormap

# FD, Number of frost days: Annual count of days when TN (daily minimum temperature) < 0oC.
indicator_name = "fd"
unit = "d"
show_name = "FD"


def process_fd(ds: xr.Dataset) -> xr.DataArray:
    fd = (ds["tasmin"] - 273.15 < 0).sum(dim="time")
    fd.name = indicator_name
    return fd


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=tas_colormap)
    add_title(ax, f"{show_name} (${unit}$)")


def calculate(process: bool = True):
    if process:
        range_data_period("tasmin", process_fd, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
