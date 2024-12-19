import xarray as xr
from xclim.core.calendar import percentile_doy
import pandas as pd
from xclim.indices import tx90p
from utils import (
    merge_intermediate_post_process,
    merge_base_years_period,
    get_origin_result_data_path,
    range_data_period,
    mean_by_region,
    merge_intermediate,
)
from plot import draw_latlon_map, add_title
from config import tas_colormap

# tasmax
base_ds = merge_base_years_period("tasmax", full_year=False)
t90 = percentile_doy(base_ds["tasmax"], per=90, window=5).sel(percentiles=90)

indicator_name = "tx90p"
unit = "d"

def process_tx90p(ds: xr.Dataset):
    result = tx90p(ds["tasmax"], t90, freq="YS")
    result.name = indicator_name
    return result.sum(dim="time")


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=tas_colormap)
    add_title(ax, f"TX90p (${unit}$)")

def calculate(process: bool = True):
    if process:
        range_data_period("tasmax", process_tx90p, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
