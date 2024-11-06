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

indicator_name = "sdii"
default_value = 0
def process_sdii(ds:xr.Dataset):
    year = ds['time'].dt.year.values.max()
    new_time = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq='D')
    ds = ds.reindex(time=new_time, fill_value=default_value)

    result = daily_pr_intensity(ds['pr'])
    result.name = indicator_name
    return result
    
def draw_sdii(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title(csv_path)
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("pr", process_sdii,mean_by_region)
    draw_sdii(get_result_data_path(indicator_name, "2021"))