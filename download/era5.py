import cdsapi
import os

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


train_start_year = 1961
train_end_year = 2020
train_years = [str(year) for year in range(train_start_year, train_end_year + 1)]
train_months = [f"{month:02d}" for month in range(1, 13)]
train_days = [f"{day:02d}" for day in range(1, 32)]

client = cdsapi.Client(wait_until_complete=False)

def get_era5_data(variable: str):
    result_buf = {}
    for year in range(train_start_year, train_end_year + 1):
        target = get_era5_data_path(variable, year)
        if os.path.exists(target): 
            print(f"{target} exists, skipping")
            continue
        result_buf[target] = retrieve_era5_data(variable, year)
    
    for target, result in result_buf.items():
        result.download(target)
    
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
