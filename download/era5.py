import cdsapi
import os
import pickle
from pathlib import Path
from config import (
    download_era5,
    era5_data_dir,
    use_download_cache,
    cds_api_key,
    start_year,
    end_year
)
from utils import get_era5_data_path

dataset = "derived-era5-single-levels-daily-statistics"
area = [55, 70, 30, 100]
variable_name_dict = {
    "tas": "2m_temperature",
    "tasmax": "maximum_2m_temperature_since_previous_post_processing",
    "tasmin": "minimum_2m_temperature_since_previous_post_processing",
    "pr": "total_precipitation",  
}

variable_rename_dict = {
    'tas': 't2m'
}

statistic_dict = {
    "tas": "daily_mean",
    "tasmax": "daily_maximum",
    "tasmin": "daily_minimum",
    "pr": "daily_mean",
}

train_years = [str(year) for year in range(start_year, end_year + 1)]
train_months = [f"{month:02d}" for month in range(1, 13)]
train_days = [f"{day:02d}" for day in range(1, 32)]

client = cdsapi.Client(wait_until_complete=False, key=cds_api_key, url="https://cds.climate.copernicus.eu/api")

def get_era5_data(variable: str):
    if not download_era5:
        return
    
    status_file = 'era5_download_status.pkl'
    if os.path.exists(status_file):
        with open(status_file, 'rb') as f:
            result_buf = pickle.load(f)
    else:
        result_buf = {}
        
    for year in train_years:
        target = f"{era5_data_dir}/{variable}_era5_origin_{year}.nc"
        if use_download_cache and os.path.exists(target): 
            print(f"{target} exists, skipping")
            continue
    
        if use_download_cache and target in result_buf:
            print(f"{target} already in buffer, skipping")
            continue
        
        result_buf[target] = retrieve_era5_data(variable, year)
        
        # 将 result_buf 暂存到文件
        with open(status_file, 'wb') as f:
            pickle.dump(result_buf, f)
    
    for target, result in result_buf.items():
        if use_download_cache and os.path.exists(target):
            print(f"{target} exists, skipping")
            continue
        if use_download_cache and not Path(target).name.startswith(f"{variable}_"):
            print(f"{target} does not start with {variable}, skipping")
            continue
        try:
            result.download(target)
        except Exception as e:
            print(e)

def retrieve_era5_data(key: str, year: str):
    print(f"Downloading {key} data for {year}")
    request = {
        "product_type": ["reanalysis"],
        "variable": [variable_name_dict[key]],
        "year": year,
        "month": train_months,
        "day": train_days,
        "area": area,
        "daily_statistic": statistic_dict[key],
        "time_zone": "utc+08:00",
        "frequency": "1_hourly"
    }
    
    return client.retrieve(dataset, request)
