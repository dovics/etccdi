import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from xclim.indices import tx90p
from pathlib import Path
from utils import (
    new_plot,
    merge_base_years_period,
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    draw_latlon_map

)

# tasmax
base_ds = merge_base_years_period('tasmax',full_year=False)
t90 = percentile_doy(base_ds['tasmax'], per=90, window=5).sel(percentiles=90)

indicator_name = "tn90p"
def process_tx90p(ds: xr.Dataset):
    result = tx90p(ds['tasmax'], t90, freq="YS") 
    result.name = indicator_name
    return result.sum(dim="time")

def draw_tx90p(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 TX90P')
    plt.show()
    
if __name__ == '__main__':
    range_era5_data_period("tasmax", process_tx90p,mean_by_region)
    draw_tx90p(get_result_data_path(indicator_name, "2000"))