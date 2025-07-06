import xarray as xr
import pandas as pd
from xclim.indices import growing_degree_days
from utils import (
    get_origin_result_data_path,
    range_data_period,
    max_by_region,
    merge_intermediate_post_process,
    merge_intermediate,
)

from plot import draw_latlon_map, add_title
from config import tas_colormap

indicator_name = "gdd"
show_name = "GDD"
unit = "°C \cdot d"


def process_gdd(ds: xr.Dataset):
    result = growing_degree_days(ds["tas"], thresh="0 degC", freq="YS")
    result.name = indicator_name
    return result.sum(dim="time")


def draw(df: pd.DataFrame, ax=None, show_colorbar=True):
    draw_latlon_map(
        df,
        indicator_name,
        clip=True,
        ax=ax,
        cmap=tas_colormap,
        show_colorbar=show_colorbar,
    )
    add_title(ax, f"{show_name} (${unit}$)")


def calculate(process: bool = True):
    if process:
        range_data_period("tas", process_gdd, max_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
