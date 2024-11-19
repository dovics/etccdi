import xarray as xr
from matplotlib import pyplot as plt
from xclim.core.calendar import percentile_doy
import pandas as pd
from xclim.indices import tn90p
from pathlib import Path
from utils import (
    merge_base_years_period,
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    merge_intermediate_post_process,
    merge_intermediate
)
from plot import draw_latlon_map
base_ds = merge_base_years_period("tasmin", full_year=False)
t90 = percentile_doy(base_ds["tasmin"], per=90, window=5).sel(percentiles=90)

indicator_name = "tn90p"


def process_tn90p(ds: xr.Dataset):
    result = tn90p(ds["tasmin"], t90, freq="YS")
    result.name = indicator_name
    return result.sum(dim="time")


def draw(df: pd.DataFrame, ax = None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax)
    plt.title("TN90P")



def calculate(process: bool = True):
    if process:
        range_era5_data_period("tasmin", process_tn90p, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
