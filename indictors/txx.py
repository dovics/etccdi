import xarray as xr
from xclim.indices import tx_max
import pandas as pd
from utils import (
    get_origin_result_data_path,
    range_data_period,
    mean_by_region,
    merge_intermediate_post_process,
    merge_intermediate,
)
from plot import draw_latlon_map, add_title
from config import tas_colormap

indicator_name = "txx"
unit = "°C"
show_name = "TXx"


def process_txx(ds: xr.Dataset):
    ds["tasmax"].values -= 273.15
    result = tx_max(
        ds["tasmax"],
        freq="YS",
    )
    result.name = indicator_name
    return result.max(dim="time")


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=tas_colormap)
    add_title(ax, f"{show_name} (${unit}$)")


def calculate(process: bool = True):
    if process:
        range_data_period("tasmax", process_txx, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
