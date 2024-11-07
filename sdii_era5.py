import xarray as xr
from matplotlib import pyplot as plt 
import pandas as pd
from xclim.indicators.atmos import daily_pr_intensity
from pathlib import Path
from utils import (
    get_result_data_path,
    draw_latlon_map,
    range_era5_data_period,
    mean_by_region
)
from datetime import datetime

indicator_name = "sdii"
default_value = 0

# 非闰年 
# 调整前    调整后
# 10/01 -> 01/01
# 11/01 -> 02/01
# 11/29 -> 03/01
# 12/30 -> 04/01

# 闰年
# 调整前    调整后
# 10/01 -> 01/01
# 11/01 -> 02/01
# 11/30 -> 03/01
# 12/31 -> 04/01

def process_sdii(ds:xr.Dataset):
    times = ds['time'].dt.floor('D').values
    duration = pd.to_timedelta(times.max() - times.min())
    year = pd.to_datetime(times.max()).year
    start_time = datetime.fromisoformat(f'{year}-01-01')
    end_time = start_time + duration
    # print(ds.sel(time=f'{year-1}-12-30')['pr'].values[0])
    ds = ds.assign_coords(time=pd.date_range(start=start_time, end=end_time, freq='D'))
    ds = ds.reindex(time=pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='D'), fill_value=default_value)
    # print(ds.sel(time=f'{year}-04-01')['pr'].values[0])
    result = daily_pr_intensity(ds['pr'])
    result.name = indicator_name
    return result
    
def draw_sdii(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title(csv_path)
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("pr", process_sdii, mean_by_region)
    draw_sdii(get_result_data_path(indicator_name, "2021"))