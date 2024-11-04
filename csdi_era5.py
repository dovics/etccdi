import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import cold_spell_duration_index
from pathlib import Path
from utils import (
    new_plot,
    merge_base_years,
    get_result_data_path,
    range_era5_data,
    range_era5_data_period,
    mean_by_region,
    draw_latlon_map
)

base_ds = merge_base_years('tasmin')
cs_di = percentile_doy(base_ds['tasmin'], per=10).sel(percentiles=10)

indicator_name = "csdi"
def process_csdi(ds: xr.Dataset):
    result = cold_spell_duration_index(ds['tasmin'], cs_di, freq="YS")
    result.name = indicator_name
    return result.sum(dim="time")

def draw_csdi(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 CSDI')
    plt.show()
    
if __name__ == '__main__':
    range_era5_data_period("tasmin", process_csdi,mean_by_region)
    draw_csdi(get_result_data_path(indicator_name, "2000"))