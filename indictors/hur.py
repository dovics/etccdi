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

from xclim.indicators.atmos import relative_humidity_from_dewpoint


# HUR, Relative humidity: Daily mean relative humidity.
indicator_name = "hur"


def process_hur(ds: xr.Dataset) -> xr.DataArray:
    hur = relative_humidity_from_dewpoint(tas=ds["tas"], tdps=ds["tdps"])

    result = hur.mean(dim="time")
    result.name = indicator_name
    return result


def draw(df: pd.DataFrame, ax = None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax)
    plt.title("HUR")



def calculate(process: bool = True):
    if process:
        range_era5_data_period(["tdps", "tas"], process_hur, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))