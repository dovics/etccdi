import xarray as xr
from matplotlib import pyplot as plt
from pathlib import Path
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib.ticker as mticker
from cartopy.io.shapereader import Reader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import numpy as np
import re
from datetime import datetime
from typing import Union
import dask
import zarr
import pandas as pd
import geopandas as gpd
import rioxarray

from config import  (
    era5_data_dir,
    result_data_dir,
    intermediate_data_dir,
    
    start_year,
    end_year,
    base_start_year, 
    base_end_year,
    
    period_start,
    period_end,
    
    use_cache,
)

def get_year_from_path(path: str):
    match = re.search(r'(\d{4})\.nc', path)

    if match:
        return match.group(1)
    
    return ""

def get_era5_data_path(variable: str, year: str):
    return f"{era5_data_dir}/{variable}_era5_origin_{year}.nc"

def load_era5_date(variable: str, year: str):
    return xr.open_dataset(get_era5_data_path(variable, year))
    
def get_cf_daily_date_path(variable: str, year: str):
    if Path(result_data_dir).exists() == False: Path(result_data_dir).mkdir()
    return f"{intermediate_data_dir}/{variable}_cf_daily_{year}.zarr"

def load_era5_daily_data(var_list: Union[list[str], str], year: str):
    if isinstance(var_list, str): var_list = [var_list]
    
    dataset_list = []
    for var in var_list:
        dataset_list.append(load_era5_daily_data_single(var, year))

    ds = xr.merge(dataset_list)
    return ds

def load_era5_daily_data_single(variable, year):
    path = get_cf_daily_date_path(variable, year)
    if use_cache and Path(path).exists():
        print(f"Using cached {path}")
        return xr.open_zarr(path)
    
    era5_ds = load_era5_date(variable, year)
    ds = convert_era5_to_cf_daily(era5_ds.sel(valid_time=slice(f"{year}-01-01", f"{year}-12-31")), variable)
    
    save_to_zarr(ds, path)
    return ds

def save_to_zarr(ds: xr.Dataset, path: Path):
    ds = dask.optimize(ds)[0]
    t = ds.to_zarr(path, mode='w', compute=False, safe_chunks=False)
    t.compute(retries=5)
    zarr.consolidate_metadata(path)
    
def range_era5_data(var_list: Union[list[str], str], process: callable, postprocess: callable = None):
    if isinstance(var_list, str): var_list = [var_list]
    
    for year in range(start_year, end_year + 1):
        ds = process(load_era5_daily_data(var_list, str(year)))
        if ds == None: continue
        ds.to_dataframe().to_csv(get_result_data_path(ds.name, str(year)))
        if postprocess: 
            df = postprocess(ds)
            df.to_csv(get_result_data_path(ds.name + "_post_process", str(year)), index=False)

def range_era5_data_period(var_list: Union[list[str], str], process: callable, postprocess: callable = None):
    if isinstance(var_list, str): var_list = [var_list]
    
    if datetime.strptime(period_start, '%m-%d') < datetime.strptime(period_end, '%m-%d'): 
        for year in range(start_year, end_year + 1):
            ds = process(load_era5_daily_data(var_list, str(year)))
            ds.to_dataframe().to_csv(get_result_data_path(ds.name, str(year)))
            if postprocess: 
                df = postprocess(ds)
                df.to_csv(get_result_data_path(ds.name + "_post_process", str(year)), index=False)
        return
    
    for year in range(start_year + 1, end_year + 1):
        last_year_ds = load_era5_daily_data(var_list, str(year - 1))
        this_year_ds = load_era5_daily_data(var_list, str(year))
        merged_ds = xr.concat([last_year_ds, this_year_ds], dim="time")
        selected_ds = merged_ds.sel(time=slice(f"{year - 1}-{period_start}", f"{year}-{period_end}"))
        ds = process(selected_ds)
        ds.to_dataframe().to_csv(get_result_data_path(ds.name, str(year)))   
        if postprocess: 
            df = postprocess(ds)
            df.to_csv(get_result_data_path(ds.name + "_post_process", str(year)), index=False)

def merge_base_years(var_list: Union[list[str], str]) -> xr.Dataset:
    datesets = []
    for year in range(base_start_year, base_end_year + 1):
        datesets.append(load_era5_daily_data(var_list, str(year)))
    
    return xr.concat(datesets, dim='time')

def get_result_data_path(variable: str, year: str):
    if Path(result_data_dir).exists() == False: Path(result_data_dir).mkdir()
    return f"{result_data_dir}/{variable}_era5_{year}.csv"

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
        ds = ds.chunk({'valid_time': 100}).sortby('valid_time').groupby('valid_time.date')
        if variable == "tasmin":
            ds = ds.min(dim='valid_time')
        else:
            ds = ds.max(dim='valid_time')
        ds['date'] = pd.to_datetime(ds['date'])
        time_variable = "date"
   
    if variable == "pr" and ds[era5_variables[variable]].attrs['units'] == 'm':
        ds[era5_variables[variable]] = ds[era5_variables[variable]] * 1000 * 24
        ds[era5_variables[variable]].attrs['units'] = 'mm/day'

    if variable == "rsds" and ds[era5_variables[variable]].attrs['units'] == 'J m**-2':
        ds[era5_variables[variable]] = ds[era5_variables[variable]] / 3600
        ds[era5_variables[variable]].attrs['units'] = 'W m-2'

    return ds.rename({
        time_variable: 'time', 
        "longitude": "lon",
        "latitude": "lat", 
        era5_variables[variable]: variable
    })
    
province_geojson="static/xinjiang.json"

def new_plot(lons, lats):
    proj = ccrs.PlateCarree()
    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.subplots(1, 1, subplot_kw={'projection': proj}) 
    
    gdf = gpd.read_file(province_geojson)
    provinces = cfeat.ShapelyFeature(gdf.geometry, proj, edgecolor='k', alpha=0.7, facecolor='none')
    ax.add_feature(provinces, linewidth=1)
    
    ax.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=proj)
    
    gl = ax.gridlines(crs=proj, draw_labels=True, linewidth=1.2, color='k', alpha=0.5, linestyle='--')
    gl.xlabels_top = False 
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER 
    gl.yformatter = LATITUDE_FORMATTER  
    gl.xlocator = mticker.FixedLocator(np.arange(lons.min(), lons.max()+10, 10))
    gl.ylocator = mticker.FixedLocator(np.arange(lats.min(), lats.max()+10, 10))
    
    return fig, ax

def mean_by_gdf(da: xr.DataArray, gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    da = da.load().astype(float)
    da = da.rio.write_crs(gdf.crs)
    averages = []
    for _, region in gdf.iterrows():
        try:
            clipped = da.rio.clip([region.geometry])
            mean_value = clipped.mean(dim=['lat', 'lon'], skipna=True)
            averages.append({"name": region["name"], "value": str(mean_value.values)})
        except Exception as e:
            print(region["name"], "error:", e)
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
