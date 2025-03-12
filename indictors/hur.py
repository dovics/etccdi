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
from config import tas_colormap, mode
from xclim.indicators.atmos import relative_humidity_from_dewpoint


# HUR, Relative humidity: Daily mean relative humidity.
indicator_name = "hur"
unit = "\%"


def process_hur_era5(ds: xr.Dataset) -> xr.DataArray:
    hur = relative_humidity_from_dewpoint(tas=ds["tas"], tdps=ds["tdps"])

    result = hur.mean(dim="time")
    result.name = indicator_name
    return result

def process_hur_cmip6(ds: xr.Dataset) -> xr.DataArray:
    ds = ds.rename({"hurs": "hur"})
    hur = ds["hur"].mean(dim="time")
    hur.name = indicator_name
    return hur 
    

def draw(df: pd.DataFrame, ax=None):
    draw_latlon_map(df, indicator_name, clip=True, ax=ax, cmap=tas_colormap)
    add_title(ax, f"RH (${unit}$)")


def calculate(process: bool = True):

    if process:
        if mode == "era5":
            range_data_period(["tdps", "tas"], process_hur_era5, mean_by_region)
        else:
            range_data_period(["hurs"], process_hur_cmip6, mean_by_region)

    df_post_process = merge_intermediate_post_process(indicator_name)
    df_post_process.to_csv(
        get_origin_result_data_path(indicator_name + "_post_process")
    )

    df = merge_intermediate(indicator_name)
    df.to_csv(get_origin_result_data_path(indicator_name))
