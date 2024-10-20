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
from config import  (
    era5_data_dir,
    result_data_dir,
    base_start_year, 
    base_end_year
)

geojson_path = "D:/CMIP6/DataV_GeoJSON/geojson/province/650000.json"

def get_year_from_path(path: str):
    match = re.search(r'(\d{4})\.nc', path)

    if match:
        return match.group(1)
    
    return ""

def get_era5_data_path(variable: str, year: str):
    return f"{era5_data_dir}/{variable}_era5_daily_{year}.nc"

def load_era5_daily_tas_data(year: str):
    return load_era5_daily_data('tas', year)

def load_era5_daily_data(variable: str, year: str):
    return xr.open_dataset(get_era5_data_path(variable, year))

def range_era5_data(process):
    for file in Path(era5_data_dir).rglob('*_era5_daily_*.nc'):
        if file.is_file():
            process(file)

def merge_base_years(variable: str) -> xr.Dataset:
    datesets = []
    for year in range(base_start_year, base_end_year + 1):
        datesets.append(load_era5_daily_data(variable, str(year)))
    
    return xr.concat(datesets, dim='valid_time')

def get_result_data_path(variable: str, year: str):
    return f"{result_data_dir}/{variable}_era5_{year}.csv"

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