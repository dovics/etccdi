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
import dask
import zarr
import pandas as pd

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

geojson_path = "D:/CMIP6/DataV_GeoJSON/geojson/province/650000.json"

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

def load_era5_daily_data(variable: str, year: str):
    path = get_cf_daily_date_path(variable, year)
    if use_cache and Path(path).exists():
        print(f"Using cached {path}")
        return xr.open_zarr(path)
    
    era5_ds = load_era5_date(variable, year)
    ds = convert_era5_to_cf_daily(era5_ds.sel(valid_time=slice(f"{year}-01-01", f"{year}-12-31")), variable)
    
    ds = dask.optimize(ds)[0]
    t = ds.to_zarr(path, mode='w', compute=False, safe_chunks=False)
    t.compute(retries=5)
    zarr.consolidate_metadata(path)
    
    return ds

def range_era5_data(variable: str, process: callable):
    for file in Path(era5_data_dir).rglob(f'{variable}_era5_origin_*.nc'):
        if file.is_file():
            ds = process(convert_era5_to_cf_daily(xr.open_dataset(file), variable))
            ds.to_dataframe().to_csv(get_result_data_path(ds.name, get_year_from_path(file.name)))

def range_era5_data_period(variable: str, process: callable):
    if datetime.strptime(period_start, '%m-%d') > datetime.strptime(period_end, '%m-%d'): 
        for year in range(start_year + 1, end_year + 1):
            last_year_ds = load_era5_daily_data(variable, str(year - 1))
            this_year_ds = load_era5_daily_data(variable, str(year))
            merged_ds = xr.concat([last_year_ds, this_year_ds], dim="time")
            selected_ds = merged_ds.sel(time=slice(f"{year - 1}-{period_start}", f"{year}-{period_end}"))
            ds = process(selected_ds)
            print(ds)
            ds.to_dataframe().to_csv(get_result_data_path(ds.name, str(year)))   
    else:
        for year in range(start_year, end_year + 1):
            ds = process(load_era5_daily_data(variable, str(year)))
            ds.to_dataframe().to_csv(get_result_data_path(ds.name, str(year)))

def merge_base_years(variable: str) -> xr.Dataset:
    datesets = []
    for year in range(base_start_year, base_end_year + 1):
        datesets.append(load_era5_daily_data(variable, str(year)))
    
    return convert_era5_to_cf_daily(xr.concat(datesets, dim='valid_time'), variable)

def get_result_data_path(variable: str, year: str):
    if Path(result_data_dir).exists() == False: Path(result_data_dir).mkdir()
    return f"{result_data_dir}/{variable}_era5_{year}.csv"

era5_variables = {
    "tas": "t2m",
    "tasmin": "mn2t"
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

    return ds.rename({
        time_variable: 'time', 
        "longitude": "lon",
        "latitude": "lat", 
        era5_variables[variable]: variable
    })

def new_plot(lons, lats):
    proj = ccrs.PlateCarree()
    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.subplots(1, 1, subplot_kw={'projection': proj}) 
    
    reader = Reader('static/province.shp')
    provinces = cfeat.ShapelyFeature(reader.geometries(), proj, edgecolor='k', facecolor='none')
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