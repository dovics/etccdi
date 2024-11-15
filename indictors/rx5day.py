import xarray as xr
from matplotlib import pyplot as plt
import pandas as pd

from xclim.indices import max_n_day_precipitation_amount
from pathlib import Path
from utils import (
    get_result_data_path,
    range_era5_data_period,
    mean_by_region,
    draw_latlon_map,
    reindex_ds_to_all_year,
    merge_intermediate_post_process,
)

default_value = 0
indicator_name = "rx5day"


def process_rx5day(ds: xr.Dataset):
    ds = reindex_ds_to_all_year(ds, default_value)
    result = max_n_day_precipitation_amount(ds["pr"], window=5)
    result.name = indicator_name
    return result


def draw_rx5day(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True)
    plt.title("ERA5 RX5DAY")
    plt.show()


def calculate():
    range_era5_data_period("pr", process_rx5day, mean_by_region)
    df = merge_intermediate_post_process(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
