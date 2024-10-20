import xarray as xr
from pathlib import Path
from utils import range_era5_data, get_result_data_path, get_year_from_path
import numpy as np
import dask
# GSL, Growing season length: Annual (1st Jan to 31st Dec in Northern Hemisphere (NH), 
# 1st July to 30th June in Southern Hemisphere (SH)) count between first span of
# at least 6 days with daily mean temperature TG>5oC and first span after July 1st 
# (Jan 1st in SH) of 6 days with TG<5oC.

def process_gsl_nh(file: Path):
    if not file.name.startswith('tas'):
        return
    ds = xr.open_dataset(file)
    ds = ds.chunk({"latitude": 20, "longitude": 20}) 
    ds['t2m'] -= 273.15
    
    gsl_start = xr.apply_ufunc(find_gsl_start, ds['t2m'], input_core_dims=[["valid_time"]], output_core_dims=[[]], vectorize=True, dask='parallelized', output_dtypes=[int] )
    gsl_end = xr.apply_ufunc(find_gsl_end, ds['t2m'], input_core_dims=[["valid_time"]], output_core_dims=[[]], vectorize=True, dask='parallelized', output_dtypes=[int] )
    gsl = gsl_end - gsl_start
    ds = xr.Dataset({
        'gsl': gsl,
        'gsl_start': gsl_start,
        'gsl_end': gsl_end,
    })
    ds.to_dataframe().to_csv(get_result_data_path('gsl', get_year_from_path(file.name)))
    return gsl

def find_gsl_start(arr, span_length = 6):
    for i in range(len(arr) - span_length + 1):
        if np.all(arr[i:i+span_length] > 5):
            return i
    return len(arr)

def find_gsl_end(arr, span_length = 6):
    for i in range(int(len(arr) / 2), len(arr) - span_length + 1):
        if np.all(arr[i:i+span_length] < 5):
            return i
    return len(arr)

if __name__ == '__main__':
    range_era5_data(process_gsl_nh)