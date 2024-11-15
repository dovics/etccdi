import xarray as xr
from matplotlib import pyplot as plt
import pandas as pd
from xclim.indices import max_1day_precipitation_amount
from pathlib import Path
from utils import (
    get_result_data_path,
    mean_by_region,
    range_era5_data_period,
    draw_latlon_map,
    merge_intermediate_post_process,
)

indicator_name = "rx1day"


def process_rx1day(ds: xr.Dataset):
    result = max_1day_precipitation_amount(ds["pr"])
    result.name = indicator_name
    return result.max(dim="time")


def draw_rx1day(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True)
    plt.title("ERA5 RX1DAY")
    plt.show()


def calculate():
    range_era5_data_period("pr", process_rx1day, mean_by_region)
    df = merge_intermediate_post_process(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
