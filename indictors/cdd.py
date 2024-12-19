import xarray as xr
from matplotlib import pyplot as plt
import pandas as pd
import xclim
from xclim.indicators.atmos import maximum_consecutive_dry_days
from utils import (
    get_origin_result_data_path,
    range_data_period,
    mean_by_region,
    reindex_ds_to_all_year,
    merge_intermediate_post_process,
    merge_intermediate,
)
from config import pr_colormap
from plot import draw_latlon_map, add_title

xclim.set_options(data_validation="log")
indicator_name = "cdd"
unit = "d"
default_value = 10


# 日降水量 < 1 mm 持续天数最大值
def process_cdd(ds: xr.Dataset):
    ds = reindex_ds_to_all_year(ds, default_value)
    result = maximum_consecutive_dry_days(ds["pr"], thresh="1 mm/day", freq="YS")
    result.name = indicator_name
    return result


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=pr_colormap)
    add_title(ax, f"CDD (${unit}$)")

def calculate(process: bool = True):
    if process:
        range_data_period("pr", process_cdd, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
