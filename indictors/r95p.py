import xarray as xr
from matplotlib import pyplot as plt
from xclim.core.calendar import percentile_doy
import pandas as pd

from xclim.indices import days_over_precip_thresh

from pathlib import Path
from utils import (
    get_result_data_path,
    merge_base_years_period,
    range_era5_data_period,
    mean_by_region,
    merge_intermediate_post_process,
    merge_intermediate
)
from plot import draw_latlon_map

base_ds = merge_base_years_period("pr", full_year=False)
r95 = percentile_doy(base_ds["pr"], per=95).sel(percentiles=95)
indicator_name = "r95p"


def process_r95p(ds: xr.Dataset):
    result = days_over_precip_thresh(ds["pr"], r95, freq="YS")
    result.name = indicator_name
    return result.sum(dim="time")


def draw(df: pd.DataFrame, ax = None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax)
    plt.title(" R95P")


def calculate(process: bool = True  ):
    if process:
        range_era5_data_period("pr", process_r95p, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
