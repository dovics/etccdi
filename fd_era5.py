from matplotlib import pyplot as plt 
import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
from xclim.indices import frost_days
from utils import (
    new_plot,
    range_era5_data_period,
    get_result_data_path,
    mean_by_region,
    draw_latlon_map
)
import cartopy.crs as ccrs


# FD, Number of frost days: Annual count of days when TN (daily minimum temperature) < 0oC.
indicator_name = "fd"
def process_fd(ds: xr.Dataset) -> xr.DataArray:
    fd = (ds['tasmin'] - 273.15 < 0).sum(dim='time')
    fd.name = indicator_name
    return fd

def draw_fd(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 FD')
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("tasmin", process_fd, mean_by_region)
    draw_fd(get_result_data_path(indicator_name, "2000"))