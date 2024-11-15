import xarray as xr
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import maximum_consecutive_wet_days
from pathlib import Path
from utils import (
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    draw_latlon_map,
    reindex_ds_to_all_year,
    merge_intermediate_post_process,
)

default_value = 0
indicator_name = "cwd"


def process_cwd(ds: xr.Dataset):
    ds = reindex_ds_to_all_year(ds, default_value)
    result = maximum_consecutive_wet_days(ds["pr"], thresh="1 mm/day")
    result.name = indicator_name
    return result


def draw_cwd(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True, cmap="coolwarm_r")
    plt.title("ERA5 CWD")
    plt.show()


def calculate():
    range_era5_data_period("pr", process_cwd, mean_by_region)
    df = merge_intermediate_post_process(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
