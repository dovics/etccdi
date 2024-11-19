import xarray as xr
from matplotlib import pyplot as plt
from xclim.indices import tx_max
import pandas as pd
from utils import (
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    merge_intermediate_post_process,
    merge_intermediate
)
from plot import draw_latlon_map

indicator_name = "txx"


def process_txx(ds: xr.Dataset):
    ds["tasmax"].values -= 273.15
    result = tx_max(
        ds["tasmax"],
        freq="YS",
    )
    result.name = indicator_name
    return result.max(dim="time")


def draw(df: pd.DataFrame, ax = None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax)
    plt.title("TXX")



def calculate(process: bool = True):
    if process:
        range_era5_data_period("tasmax", process_txx, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
