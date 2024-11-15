import xarray as xr
from matplotlib import pyplot as plt
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import tn10p
from pathlib import Path
from utils import (
    draw_latlon_map,
    merge_base_years_period,
    get_result_data_path,
    merge_intermediate_post_process,
    range_era5_data,
    mean_by_region,
)

base_ds = merge_base_years_period("tasmin", full_year=False)
t10 = percentile_doy(base_ds["tasmin"], per=10, window=5).sel(percentiles=10)

indicator_name = "tn10p"


def process_tn10p(ds: xr.Dataset):
    result = tn10p(ds["tasmin"], t10, freq="YS")
    result.name = indicator_name
    return result.sum(dim="time")


def draw_tn10p(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True)
    plt.title("ERA5 TN10P")
    plt.show()


def calculate():
    range_era5_data("tasmin", process_tn10p, mean_by_region)
    df = merge_intermediate_post_process(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))