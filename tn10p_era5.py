import xarray as xr
from xclim.core.calendar import percentile_doy
from xclim.indices import tn10p
from pathlib import Path
from utils import (
    merge_base_years,
    get_result_data_path,
    get_year_from_path,
    range_era5_data
)

base_ds = merge_base_years('tas').rename({"valid_time": "time"}) # TODO : 'tasmin'
t10 = percentile_doy(base_ds['t2m'], per=10, window=5).sel(percentiles=10)
   
def process_tn10p(file: Path):
    if not file.name.startswith('tas_'): # TDDO : 'tasmin'
        return
    ds = xr.open_dataset(file)
    ds = ds.rename({"valid_time": "time"})
    
    result = tn10p(ds['t2m'], t10, freq="YS")
    result.name = 'tn10p'
    result.to_dataframe().to_csv(get_result_data_path('tn10p', get_year_from_path(file.name)))
    
if __name__ == '__main__':
    range_era5_data(process_tn10p)