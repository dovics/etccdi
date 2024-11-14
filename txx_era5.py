import xarray as xr
from matplotlib import pyplot as plt
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import tx_max
from pathlib import Path
from utils import (
    get_result_data_path,
    range_era5_data_period,
    draw_latlon_map,
    mean_by_region,
    merge_intermediate_post_process
)

indicator_name = "txx"


def process_txx(ds: xr.Dataset):
    ds["tasmax"].values -= 273.15
    result = tx_max(
        ds["tasmax"],
        freq="YS",
    )
    result.name = indicator_name
    return result.max(dim="time")


def draw_txx(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True)
    plt.title("ERA5 TXX")
    plt.show()


if __name__ == "__main__":
    range_era5_data_period("tasmax", process_txx, mean_by_region)
    df = merge_intermediate_post_process(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
