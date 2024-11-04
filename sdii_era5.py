import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import daily_pr_intensity
from pathlib import Path
from utils import (
    new_plot,
    get_result_data_path,
    range_era5_data,
    draw_latlon_map,
    range_era5_data_period,
    mean_by_region
)

indicator_name = "sdii"
def process_sdii(ds:xr.Dataset):
    result = daily_pr_intensity(ds['pr'])
    result.name = indicator_name
    return result.sum(dim="time")
    
def draw_sdii(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 SDII')
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("pr", process_sdii,mean_by_region)
    draw_sdii(get_result_data_path(indicator_name, "2000"))