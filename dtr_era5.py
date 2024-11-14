from matplotlib import pyplot as plt
import xarray as xr
import pandas as pd
from xclim.indices import daily_temperature_range
from pathlib import Path
from utils import (
    get_result_data_path,
    draw_latlon_map,
    range_era5_data_period,
    mean_by_region,
    merge_intermediate_post_process,
)

indicator_name = "dtr"


def process_dtr(ds: xr.Dataset) -> xr.DataArray:
    ds = ds.sortby("time")
    dtr = daily_temperature_range(ds["tasmin"], ds["tasmax"])
    dtr.name = indicator_name
    return dtr.sum(dim="time")


def draw_dtr(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True)
    plt.title("ERA5 DTR")
    plt.show()


if __name__ == "__main__":
    range_era5_data_period(["tasmax", "tasmin"], process_dtr, mean_by_region)
    df = merge_intermediate_post_process(indicator_name)
    df.to_csv(get_result_data_path(indicator_name))
