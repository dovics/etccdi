import xarray as xr
import pandas as pd
from xclim.indicators.atmos import daily_pr_intensity
from utils import (
    get_origin_result_data_path,
    range_era5_data_period,
    mean_by_region,
    reindex_ds_to_all_year,
    merge_intermediate_post_process,
    merge_intermediate,
)
from plot import draw_latlon_map, add_title
from config import pr_colormap

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

default_value = 0
unit = "mm \cdot d^{-1}"

def process_sdii(ds: xr.Dataset):
    ds = reindex_ds_to_all_year(ds, default_value)
    result = daily_pr_intensity(ds["pr"])
    result.name = indicator_name
    return result


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=pr_colormap)
    add_title(ax, f"SDII (${unit}$)")

def calculate(process: bool = True):
    if process:
        range_era5_data_period("pr", process_sdii, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
