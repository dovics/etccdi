import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd

from xclim.indices import days_over_precip_thresh

from pathlib import Path
from utils import (
    get_result_data_path,
    merge_base_years_period,
    draw_latlon_map,
    range_era5_data_period,
    mean_by_region
)

base_ds = merge_base_years_period('pr',full_year=False)
r95 = percentile_doy(base_ds['pr'], per=95).sel(percentiles=95)
indicator_name = "r95p"
def process_r95p(ds:xr.Dataset):
    result = days_over_precip_thresh(ds['pr'], r95, freq="YS")
    result.name = indicator_name
    return result.sum(dim="time")
    
def draw_r95p(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 R95P')
    plt.show()

if __name__ == '__main__':
    range_era5_data_period("pr", process_r95p, mean_by_region)
    draw_r95p(get_result_data_path(indicator_name, "2000"))