import xarray as xr
from matplotlib import pyplot as plt
from xclim.indices import tn_min
import pandas as pd
from utils import (
    merge_intermediate_post_process,
    get_origin_result_data_path,
    range_era5_data_period,
    mean_by_region,
    merge_intermediate,
)
from plot import draw_latlon_map
from config import tas_colormap

indicator_name = "tnn"
unit = "°C"

def process_tnn(ds: xr.Dataset):
    ds["tasmin"].values -= 273.15
    result = tn_min(ds["tasmin"], freq="YS")
    result.name = indicator_name
    return result.min(dim="time")


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=tas_colormap)


def calculate(process: bool = True):
    if process:
        range_era5_data_period("tasmin", process_tnn, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
