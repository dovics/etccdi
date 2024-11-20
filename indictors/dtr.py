from matplotlib import pyplot as plt
import xarray as xr
import pandas as pd
from xclim.indices import daily_temperature_range
from pathlib import Path
from utils import (
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    merge_intermediate_post_process,
    merge_intermediate
)

from plot import draw_latlon_map

indicator_name = "dtr"


def process_dtr(ds: xr.Dataset) -> xr.DataArray:
    ds = ds.sortby("time")
    dtr = daily_temperature_range(ds["tasmin"], ds["tasmax"])
    dtr.name = indicator_name
    return dtr.sum(dim="time")


def draw(df: pd.DataFrame, ax = None):
    cmap = plt.get_cmap("OrRd")
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=cmap)
    plt.title("DTR")


def calculate(process: bool = True):
    if process:
        range_era5_data_period(["tasmax", "tasmin"], process_dtr, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
