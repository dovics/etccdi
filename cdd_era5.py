import xarray as xr
from matplotlib import pyplot as plt 
import pandas as pd
import xclim
from xclim.indicators.atmos import maximum_consecutive_dry_days
from pathlib import Path
from utils import (
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    draw_latlon_map
)
xclim.set_options(data_validation='log')
indicator_name = "cdd"
default_value = 10

# 日降水量 < 1 mm 持续天数最大值
def process_cdd(ds: xr.Dataset):
    year = ds['time'].dt.year.values.max()
    new_time = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq='D')
    ds = ds.reindex(time=new_time, fill_value=default_value)
    result = maximum_consecutive_dry_days(ds['pr'], thresh='1 mm/day', freq='YS')
    result.name = indicator_name
    return result
    
def draw_cdd(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=False)
    plt.title('ERA5 CDD')
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("pr", process_cdd, mean_by_region)
    draw_cdd(get_result_data_path(indicator_name, "2021"))