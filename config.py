import os

era5_data_dir = "era5_data"
result_data_dir = "result_data"
intermediate_data_dir = "intermediate_data"

period_start = "10-01"
period_end = "06-30"
start_year = 1980
end_year = 2020

base_start_year = 1980
base_end_year = 1990

# cds_api_key = os.environ.get("CDS_API_KEY")
cds_api_key = "11a309e4-98cb-4f04-a1c9-215cf56c2c1b"

use_cache = True

download_era5 = True
use_download_cache = use_cache
