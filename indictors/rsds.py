from matplotlib import pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
from xclim.indices import frost_days
from utils import (
    merge_intermediate_post_process,
    range_era5_data_period,
    get_origin_result_data_path,
    mean_by_region,
    merge_intermediate,
)
from plot import draw_latlon_map
from config import tas_colormap

indicator_name = "rsds"


def process_rsds(ds: xr.Dataset) -> xr.DataArray:
    rsds = ds["rsds"].sum(dim="time")
    rsds.name = indicator_name
    return rsds


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=tas_colormap)
    ax.set_title("RSDS", loc="right")


def calculate(process: bool = True):
    if process:
        range_era5_data_period("rsds", process_rsds, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
