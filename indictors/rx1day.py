import xarray as xr
from matplotlib import pyplot as plt
import pandas as pd
from xclim.indices import max_1day_precipitation_amount
from pathlib import Path
from utils import (
    get_result_data_path,
    mean_by_region,
    range_era5_data_period,
    merge_intermediate_post_process,
    merge_intermediate,
)
from plot import draw_latlon_map
from config import pr_colormap

indicator_name = "rx1day"


def process_rx1day(ds: xr.Dataset):
    result = max_1day_precipitation_amount(ds["pr"])
    result.name = indicator_name
    return result.max(dim="time")


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=pr_colormap)
    plt.title("RX1DAY", loc="right")


def calculate(process: bool = True):
    if process:
        range_era5_data_period("pr", process_rx1day, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
