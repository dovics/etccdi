from matplotlib import pyplot as plt 
import xarray as xr
import pandas as pd
from pathlib import Path
from utils import (
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    draw_latlon_map,
    merge_intermediate_post_process,
    merge_intermediate
)


# ID, Number of icing days: Annual count of days when TX (daily maximum temperature) < 0oC.
indicator_name = "id"
def process_id(ds: xr.Dataset) -> xr.DataArray:
    id = (ds['tasmax'] - 273.15 < 0).sum(dim='time')
    id.name = indicator_name
    return id

def draw_id(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name,clip=True)
    plt.title('ERA5 ID')
    plt.show()

def calculate(process: bool = True  ):
    if process:
        range_era5_data_period("tasmax", process_id,mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(get_result_data_path(indicator_name + "_post_process"))

    df = merge_intermediate(indicator_name)
    df.to_csv(get_result_data_path(indicator_name)) 