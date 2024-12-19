import xarray as xr
import pandas as pd
from utils import (
    merge_intermediate_post_process,
    range_data_period,
    get_origin_result_data_path,
    mean_by_region,
    merge_intermediate,
)
from plot import draw_latlon_map, add_title
from config import pr_colormap

# PR, Precipitation: Annual total precipitation.
indicator_name = "pr"
unit = "mm \cdot d^{-1}"

def process_pr(ds: xr.Dataset) -> xr.DataArray:
    pr = ds["pr"].sum(dim="time")
    pr.name = indicator_name
    return pr


def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=pr_colormap)
    add_title(ax, f"PR (${unit}$)")

def calculate(process: bool = True):
    if process:
        range_data_period("pr", process_pr, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
