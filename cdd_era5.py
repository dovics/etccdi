import xarray as xr
from matplotlib import pyplot as plt 
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indicators.atmos import maximum_consecutive_dry_days
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    draw_latlon_map
)

indicator_name = "cdd"
def process_cdd(ds: xr.Dataset):
    result = maximum_consecutive_dry_days(ds['pr'], thresh='1 mm/day', freq='YS')
    result.name = indicator_name
    return result.sum(dim='time')
    
def draw_cdd(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 CDD')
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("pr", process_cdd,mean_by_region)
    draw_cdd(get_result_data_path(indicator_name, "2000"))