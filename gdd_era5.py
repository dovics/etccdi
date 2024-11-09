import xarray as xr
from matplotlib import pyplot as plt 
import pandas as pd
from xclim.indices import growing_degree_days

from pathlib import Path
from utils import (
    get_result_data_path,
    mean_by_region,
    range_era5_data,
    max_by_region,
    range_era5_data_period,
    draw_country_map,
    draw_latlon_map,
    merge_post_process_result
)

indicator_name = "gdd"
def process_gdd(ds: xr.Dataset):
    result = growing_degree_days(ds['tas'], thresh="0 degC", freq="YS")
    result.name = indicator_name
    return result.sum(dim="time")

def draw_gdd(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True)
    plt.title('ERA5 GDD')
    plt.show()

def draw_gdd2(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_country_map(df)
    plt.show()
    

if __name__ == '__main__':
    #range_era5_data_period("tas", process_gdd, max_by_region)
    #draw_gdd(get_result_data_path(indicator_name, "2000"))
    #draw_gdd2(get_result_data_path(indicator_name + "_post_process", "2000"))
    merge_post_process_result(indicator_name)