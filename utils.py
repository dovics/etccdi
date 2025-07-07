import xarray as xr
from pathlib import Path
import numpy as np
import re
from datetime import datetime
from typing import Union
import dask
import zarr
import pandas as pd
import geopandas as gpd
from logutil import info, error
import importlib.util as importlib
import zipfile

from config import (
    era5_data_dir,
    result_data_dir,
    intermediate_data_dir,
    country_list,
    start_year,
    end_year,
    base_start_year,
    base_end_year,
    period_start,
    period_end,
    use_cache,
    cmip6_data_dir,
    cmip6_model_list,
    deltachange_methods,
    mode,
    base_mode,
)


def import_indictor(indictor: str):
    module_path = f"indictors\\{indictor}.py"
    spec = importlib.spec_from_file_location(indictor, module_path)
    module = importlib.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_year_from_path(path: str):
    match = re.search(r"(\d{4})\.nc", path)

    if match:
        return match.group(1)

    return ""


def get_era5_data_path(variable: str, year: str):
    return f"{era5_data_dir}/{variable}_era5_origin_{year}.nc"


def load_era5_date(variable: str, year: str) -> xr.Dataset:
    return xr.open_dataset(get_era5_data_path(variable, year))


def load_cmip6_data(variable: str, year: str, local_mode: str) -> xr.Dataset:
    ds_list = []
    for model in cmip6_model_list:
        path = (
            Path(cmip6_data_dir)
            .joinpath(model)
            .joinpath(
                f"{variable}_{local_mode}_{model}_{deltachange_methods[variable]}.zarr"
            )
        )
        ds = xr.open_zarr(path)    
        ds = ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31"))
        ds_list.append(ds)
    info(f"concat {len(ds_list)} models")
    concat_ds = xr.concat(ds_list, dim="model")
    return concat_ds.mean(dim="model")


def get_cf_daily_date_path(variable: str, year: str, local_mode: str):
    if Path(intermediate_data_dir).exists() == False:
        Path(intermediate_data_dir).mkdir()
    return f"{intermediate_data_dir}/{variable}_cf_daily_{year}_{local_mode}.zarr"


def load_daily_data(var_list: Union[list[str], str], year: str, local_mode: str):
    if isinstance(var_list, str):
        var_list = [var_list]

    dataset_list = []
    for var in var_list:
        dataset_list.append(load_daily_data_single(var, year, local_mode=local_mode))

    ds = xr.merge(dataset_list)
    return ds


def load_daily_data_single(variable, year, local_mode: str):
    path = get_cf_daily_date_path(variable, year, local_mode=local_mode)
    if use_cache and Path(path).exists():
        info(f"Using cached {path}")
        return xr.open_zarr(path)
    else:
        info(f"Generating {path}")
    if local_mode == "era5":
        era5_ds = load_era5_date(variable, year)
        ds = convert_era5_to_cf_daily(
            era5_ds.sel(valid_time=slice(f"{year}-01-01", f"{year}-12-31")), variable
        )
    else:
        ds = load_cmip6_data(variable, year, local_mode=local_mode)
        if "month" in ds.coords:
            ds = ds.reset_coords("month", drop=True)
        if "number" in ds.coords:
            ds = ds.reset_coords("number", drop=True)
        if variable == "pr":
            ds[variable] = xr.where(ds[variable] < 0, 0, ds[variable])
        ds = add_unit_for_cmip6(ds, variable)
    ds = ds.chunk({"time": 1000, "lat": -1, "lon": -1})
    save_to_zarr(ds, path)
    if ds[variable].isnull().any():
        error(f"{variable} {year} has null")
        exit(1)

    return ds


def save_to_zarr(ds: xr.Dataset, path: Path):
    ds = dask.optimize(ds)[0]
    t = ds.to_zarr(path, mode="w", compute=False, safe_chunks=False)
    t.compute(retries=5)
    zarr.consolidate_metadata(path)


def range_data(
    var_list: Union[list[str], str], process: callable, postprocess: callable = None
):
    if isinstance(var_list, str):
        var_list = [var_list]

    for year in range(start_year, end_year + 1):
        ds = process(load_daily_data(var_list, str(year), mode=mode))
        if ds is None:
            continue
        ds.to_dataframe().to_csv(get_intermediate_data_path(ds.name, str(year)))
        if postprocess:
            df = postprocess(ds)
            df.to_csv(
                get_intermediate_data_path(ds.name + "_post_process", str(year)),
                index=False,
            )


def range_data_period(
    var_list: Union[list[str], str], process: callable, postprocess: callable = None
):
    if isinstance(var_list, str):
        var_list = [var_list]

    if datetime.strptime(period_start, "%m-%d") < datetime.strptime(
        period_end, "%m-%d"
    ):
        for year in range(start_year, end_year + 1):
            ds = process(load_daily_data(var_list, str(year), local_mode=mode))
            ds.to_dataframe().to_csv(get_intermediate_data_path(ds.name, str(year)))
            if postprocess:
                df = postprocess(ds)
                df.to_csv(
                    get_intermediate_data_path(ds.name + "_post_process", str(year)),
                    index=False,
                )
        return

    for year in range(start_year + 1, end_year + 1):
        last_year_ds = load_daily_data(var_list, str(year - 1), local_mode=mode)
        this_year_ds = load_daily_data(var_list, str(year), local_mode=mode)
        merged_ds = xr.concat([last_year_ds, this_year_ds], dim="time")
        selected_ds = merged_ds.sel(
            time=slice(f"{year - 1}-{period_start}", f"{year}-{period_end}")
        )
        ds = process(selected_ds)
        ds.to_dataframe().to_csv(get_intermediate_data_path(ds.name, str(year)))
        if postprocess:
            df = postprocess(ds)
            df.to_csv(
                get_intermediate_data_path(ds.name + "_post_process", str(year)),
                index=False,
            )


def merge_base_years(var_list: Union[list[str], str]) -> xr.Dataset:
    datesets = []
    for year in range(base_start_year, base_end_year + 1):
        datesets.append(load_daily_data(var_list, str(year), local_mode=base_mode))

    return xr.concat(datesets, dim="time", coords="minimal")


def merge_base_years_period(
    var_list: Union[list[str], str], reindex=False, full_year=True, default_value=0
) -> xr.Dataset:
    datesets = []
    if datetime.strptime(period_start, "%m-%d") > datetime.strptime(
        period_end, "%m-%d"
    ):
        for year in range(base_start_year + 1, base_end_year + 1):
            last_year_ds = load_daily_data(
                var_list, str(year - 1), local_mode=base_mode
            )
            this_year_ds = load_daily_data(var_list, str(year), local_mode=base_mode)
            merged_ds = xr.concat([last_year_ds, this_year_ds], dim="time")
            selected_ds = merged_ds.sel(
                time=slice(f"{year - 1}-{period_start}", f"{year}-{period_end}")
            )
            if reindex:
                datesets.append(
                    reindex_ds_to_all_year(selected_ds, full_year, default_value)
                )
            else:
                datesets.append(selected_ds)
    else:
        for year in range(base_start_year, base_end_year + 1):
            ds = load_daily_data(var_list, str(year), local_mode=base_mode)
            selected_ds = ds.sel(
                time=slice(f"{year}-{period_start}", f"{year}-{period_end}")
            )
            datesets.append(selected_ds)
    return xr.concat(datesets, dim="time", coords="minimal")


def get_origin_result_data_path(variable: str):
    if Path(result_data_dir).exists() == False:
        Path(result_data_dir).mkdir()
    return f"{result_data_dir}/{variable}_{mode}.csv"


def get_result_data(variable: str, year: str = None):
    df = pd.read_csv(get_origin_result_data_path(variable))
    if year is None:
        return df

    return df[df["year"] == year]


def get_intermediate_data_path(variable: str, year: str = None):
    if Path(intermediate_data_dir).exists() == False:
        Path(intermediate_data_dir).mkdir()
    if year is None:
        return f"{intermediate_data_dir}/{variable}_{mode}.csv"
    return f"{intermediate_data_dir}/{variable}_{mode}_{year}.csv"


def get_intermediate_data(variable: str, year: str = None):
    return pd.read_csv(get_intermediate_data_path(variable, year))


era5_variables = {
    "tas": "t2m",
    "tasmin": "mn2t",
    "pr": "tp",
    "tasmax": "mx2t",
    "rsds": "cdir",
    "tdps": "d2m",
}


def convert_era5_to_cf_daily(ds: xr.Dataset, variable: str) -> xr.Dataset:
    time_variable = "valid_time"
    if variable == "tasmin" or variable == "tasmax":
        ds = (
            ds.chunk({"valid_time": 100})
            .sortby("valid_time")
            .groupby("valid_time.date")
        )
        if variable == "tasmin":
            ds = ds.min(dim="valid_time")
        else:
            ds = ds.max(dim="valid_time")
        ds["date"] = pd.to_datetime(ds["date"])
        time_variable = "date"

    if variable == "pr" and ds[era5_variables[variable]].attrs["units"] == "m":
        ds[era5_variables[variable]] = ds[era5_variables[variable]] * 1000 * 24
        ds[era5_variables[variable]].attrs["units"] = "mm/day"

    if variable == "rsds" and ds[era5_variables[variable]].attrs["units"] == "J m**-2":
        ds[era5_variables[variable]] = ds[era5_variables[variable]] / 1000000 * 24
        ds[era5_variables[variable]].attrs["units"] = "MJ m**-2"

    ds = ds.drop("number")
    return ds.rename(
        {
            time_variable: "time",
            "longitude": "lon",
            "latitude": "lat",
            era5_variables[variable]: variable,
        }
    )


def add_unit_for_cmip6(ds: xr.Dataset, variable: str) -> xr.Dataset:
    if variable == "tas" or variable == "tasmin" or variable == "tasmax":
        ds[variable].attrs["units"] = "K"

    if variable == "pr":
        ds[variable].attrs["units"] = "mm/day"

    if variable == "rsds":
        ds = ds * 24 * 3600 / 1000000
        ds[variable].attrs["units"] = "MJ m**-2"
    return ds


def max_by_gdf(da: xr.DataArray, gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    da = da.load().astype(float)
    da = da.rio.write_crs(gdf.crs)
    da = da.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
    averages = []
    for _, region in gdf.iterrows():
        if region["name"] not in country_list:
            continue
        try:
            clipped = da.rio.clip([region.geometry])
            mean_value = clipped.max(dim=["lat", "lon"], skipna=True)
            if isinstance(mean_value.values, list):
                if len(mean_value.values) != 1:
                    error(
                        f"error for mean value length not equal to 1 for region {region["name"]}"
                    )
                averages.append({"name": region["name"], "value": mean_value.values[0]})
            else:
                averages.append({"name": region["name"], "value": mean_value.values})

        except Exception as e:
            error(region["name"], "error:", e)
            continue

    results_df = pd.DataFrame(averages)
    return results_df


def mean_by_gdf(da: xr.DataArray, gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    da = da.load().astype(float)
    da = da.rio.write_crs(gdf.crs)
    da = da.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
    averages = []
    for _, region in gdf.iterrows():
        if region["name"] not in country_list:
            continue
        try:
            clipped = da.rio.clip([region.geometry])
            mean_value = clipped.mean(dim=["lat", "lon"], skipna=True)
            if isinstance(mean_value.values, list):
                if len(mean_value.values) != 1:
                    error(
                        f"error for mean value length not equal to 1 for region {region["name"]}"
                    )
                averages.append({"name": region["name"], "value": mean_value.values[0]})
            elif isinstance(mean_value.values, np.ndarray):
                averages.append(
                    {"name": region["name"], "value": mean_value.values.mean()}
                )
            else:
                averages.append({"name": region["name"], "value": mean_value.values})

        except Exception as e:
            error(region["name"], "error:", e)
            continue

    results_df = pd.DataFrame(averages)
    return results_df


gdf_list = []


def get_gdf_list():
    if len(gdf_list) != 0:
        return gdf_list
    for file in Path("static").glob(pattern="*_full.json"):
        gdf_list.append(gpd.read_file(file))

    return gdf_list


def mean_by_region(da: xr.DataArray) -> pd.DataFrame:
    df_list = []
    for gdf in get_gdf_list():
        df_list.append(mean_by_gdf(da, gdf))

    return pd.concat(df_list, ignore_index=True)


def max_by_region(da: xr.DataArray) -> pd.DataFrame:
    df_list = []
    for gdf in get_gdf_list():
        df_list.append(max_by_gdf(da, gdf))

    return pd.concat(df_list, ignore_index=True)


def generate_region_map():
    region_map = {}
    for gdf in get_gdf_list():
        for _, region in gdf.iterrows():
            region_map[region["name"]] = region.geometry
    return region_map


def add_region_latlon(df: pd.DataFrame):
    df = df.reset_index()
    region_map = generate_region_map()
    df["lat"] = df["name"].map(region_map).apply(lambda x: x.centroid.y)
    df["lon"] = df["name"].map(region_map).apply(lambda x: x.centroid.x)
    return df


def find_region_by_name(name: str) -> gpd.GeoDataFrame:
    for gdf in get_gdf_list():
        for _, region in gdf.iterrows():
            if region["name"] == name:
                return region


def reindex_ds_to_all_year(ds: xr.Dataset, default_value, full_year=True):
    times = ds["time"].dt.floor("D").values
    duration = pd.to_timedelta(times.max() - times.min())
    year = pd.to_datetime(times.max()).year
    start_time = datetime.fromisoformat(f"{year}-01-01")
    end_time = start_time + duration
    ds = ds.assign_coords(time=pd.date_range(start=start_time, end=end_time, freq="D"))
    if full_year:
        ds = ds.reindex(
            time=pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq="D"),
            fill_value=default_value,
        )
    return ds


def merge_intermediate_post_process(variable_name: str):
    df_list = []
    for year in range(start_year + 1, end_year + 1):
        csv_path = get_intermediate_data_path(variable_name + "_post_process", year)
        df = pd.read_csv(csv_path)
        df["year"] = year
        df.set_index(["year", "name"])
        df_list.append(df)

    df = pd.concat(df_list)
    df.to_csv(get_intermediate_data_path(variable_name + "_post_process"))
    df.set_index(["year", "name"], inplace=True)
    return df


def merge_intermediate(variable_name: str):
    df_list = []
    for year in range(start_year + 1, end_year + 1):
        csv_path = get_intermediate_data_path(variable_name, year)
        df = pd.read_csv(csv_path)
        df["year"] = year
        df.set_index(["year", "lat", "lon"])
        df_list.append(df)

    df = pd.concat(df_list)
    df.to_csv(get_intermediate_data_path(variable_name))
    df.set_index(["year", "lat", "lon"], inplace=True)
    return df


def get_origin_result_data_path(variable: str = None):
    return get_origin_result_data_path_by_mode(variable, mode)


def get_origin_result_data_path_by_mode(
    variable: str = None, local_mode: str = None
) -> str:
    if Path(result_data_dir + f"/origin_{local_mode}").exists() == False:
        Path(result_data_dir + f"/origin_{local_mode}").mkdir()
    if variable is None:
        return f"{result_data_dir}/origin_{local_mode}"

    return f"{result_data_dir}/origin_{local_mode}/{variable}.csv"


def get_outlier_result_data_path(variable: str = None) -> str:
    return get_outlier_result_data_path_by_mode(variable, mode)


def get_outlier_result_data_path_by_mode(
    variable: str = None, local_mode: str = None
) -> str:
    if Path(result_data_dir + f"/outlier_{local_mode}").exists() == False:
        Path(result_data_dir + f"/outlier_{local_mode}").mkdir()

    if variable is None:
        return f"{result_data_dir}/outlier_{local_mode}"
    return f"{result_data_dir}/outlier_{local_mode}/{variable}.csv"

def get_delta_change_result_data_path(variable: str = None) -> str:
    return get_delta_change_result_data_path_by_mode(variable, mode)


def get_delta_change_result_data_path_by_mode(
    variable: str = None, local_mode: str = None
) -> str:
    if Path(result_data_dir + f"/delta_change_{local_mode}").exists() == False:
        Path(result_data_dir + f"/delta_change_{local_mode}").mkdir()

    if variable is None:
        return f"{result_data_dir}/delta_change_{local_mode}"
    return f"{result_data_dir}/delta_change_{local_mode}/{variable}.csv"
