import xarray as xr
from matplotlib import pyplot as plt
from xclim.core.calendar import percentile_doy
import pandas as pd
from xclim.indices import cold_spell_duration_index
from pathlib import Path
from datetime import datetime
from utils import (
    merge_base_years_period,
    get_origin_result_data_path,
    merge_intermediate,
    range_era5_data_period,
    mean_by_region,
    reindex_ds_to_all_year,
    merge_intermediate_post_process,
)
from plot import draw_latlon_map, add_title
from config import tas_colormap

indicator_name = "csdi"
unit = "d"
default_value = 999

base_ds = merge_base_years_period(
    "tasmin", reindex=True, full_year=False, default_value=default_value
)
p10 = percentile_doy(base_ds["tasmin"], per=10).sel(percentiles=10)


# 日最低气温小于第10百分位数时，至少连续6天的年天数
def process_csdi(ds: xr.Dataset):
    ds = reindex_ds_to_all_year(ds, default_value, full_year=False)
    result = cold_spell_duration_index(ds["tasmin"], p10, freq="YS")
    result.name = indicator_name
    return result


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=tas_colormap)
    add_title(ax, f"CSDI (${unit}$)")

def calculate(process: bool = True):
    if process:
        range_era5_data_period("tasmin", process_csdi, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
