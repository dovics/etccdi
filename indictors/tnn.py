import xarray as xr
from matplotlib import pyplot as plt
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import tn_min
from pathlib import Path
from utils import (
    merge_intermediate_post_process,
    get_result_data_path,
    range_era5_data_period,
    draw_latlon_map,
    mean_by_region,
    merge_intermediate
)

indicator_name = "tnn"


def process_tnn(ds: xr.Dataset):
    ds["tasmin"].values -= 273.15
    result = tn_min(ds["tasmin"], freq="YS")
    result.name = indicator_name
    return result.min(dim="time")


def draw_tnn(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True)
    plt.title("ERA5 TNN")
    plt.show()


def calculate(process: bool = True):
    if process:
        range_era5_data_period("tasmin", process_tnn, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
