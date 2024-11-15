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
    draw_latlon_map,
    reindex_ds_to_all_year,
    merge_intermediate_post_process,
)

xclim.set_options(data_validation="log")
indicator_name = "cdd"
default_value = 10


# 日降水量 < 1 mm 持续天数最大值
def process_cdd(ds: xr.Dataset):
    ds = reindex_ds_to_all_year(ds, default_value)
    result = maximum_consecutive_dry_days(ds["pr"], thresh="1 mm/day", freq="YS")
    result.name = indicator_name
    return result


def draw_cdd(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=False)
    plt.title("ERA5 CDD")
    plt.show()


def calculate():
    range_era5_data_period("pr", process_cdd, mean_by_region)
    df = merge_intermediate_post_process(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))