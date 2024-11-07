import xarray as xr
from matplotlib import pyplot as plt 
import pandas as pd

from xclim.indices import max_n_day_precipitation_amount
from pathlib import Path
from datetime import datetime
from utils import (
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    draw_latlon_map
)
default_value = 0
indicator_name = "rx5day"
def process_rx5day(ds:xr.Dataset):
    times = ds['time'].dt.floor('D').values
    duration = pd.to_timedelta(times.max() - times.min())
    year = pd.to_datetime(times.max()).year
    start_time = datetime.fromisoformat(f'{year}-01-01')
    end_time = start_time + duration
    # print(ds.sel(time=f'{year-1}-12-30')['pr'].values[0])
    ds = ds.assign_coords(time=pd.date_range(start=start_time, end=end_time, freq='D'))
    ds = ds.reindex(time=pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='D'), fill_value=default_value)
    # print(ds.sel(time=f'{year}-04-01')['pr'].values[0])
    result = max_n_day_precipitation_amount(ds['pr'],window=5)
    result.name = indicator_name
    return result
    
def draw_rx5day(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 RX5DAY')
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("pr", process_rx5day,mean_by_region)
    draw_rx5day(get_result_data_path(indicator_name, "2000"))