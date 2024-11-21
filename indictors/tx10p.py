import xarray as xr
from matplotlib import pyplot as plt
from xclim.core.calendar import percentile_doy
import pandas as pd
from xclim.indices import tx10p
from pathlib import Path
from utils import (
    merge_base_years_period,
    get_origin_result_data_path,
    merge_intermediate_post_process,
    range_era5_data_period,
    mean_by_region,
    merge_intermediate,
)
from plot import draw_latlon_map
from config import tas_colormap

base_ds = merge_base_years_period("tasmax", full_year=False)
t10 = percentile_doy(base_ds["tasmax"], per=10, window=5).sel(percentiles=10)

indicator_name = "tx10p"


def process_tx10p(ds: xr.Dataset):
    result = tx10p(ds["tasmax"], t10, freq="YS")
    result.name = indicator_name
    return result.sum(dim="time")


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=tas_colormap)
    plt.title("TX10P", loc="right")


def calculate(process: bool = True):
    if process:
        range_era5_data_period("tasmax", process_tx10p, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
