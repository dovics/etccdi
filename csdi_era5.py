import xarray as xr
from matplotlib import pyplot as plt 
from xclim.core.calendar import percentile_doy
import pandas as pd
from xclim.indices import cold_spell_duration_index
from pathlib import Path
from datetime import datetime
from utils import (
    merge_base_years_period,
    merge_base_years,
    get_result_data_path,
    range_era5_data,
    range_era5_data_period,
    mean_by_region,
    reindex_ds_to_all_year,
    draw_latlon_map
)

indicator_name = "csdi"
default_value = 999

base_ds = merge_base_years_period('tasmin', reindex=True,full_year=False,default_value = default_value)
p10 = percentile_doy(base_ds['tasmin'], per=10).sel(percentiles=10)

# 日最低气温小于第10百分位数时，至少连续6天的年天数
# TODO: 考虑跨年时间计算
def process_csdi(ds: xr.Dataset):
    ds = reindex_ds_to_all_year(ds, default_value, full_year=False)
    result = cold_spell_duration_index(ds['tasmin'], p10, freq="YS")
    result.name = indicator_name
    return result

def draw_csdi(csv_path: Path):
    df = pd.read_csv(csv_path)
    draw_latlon_map(df, indicator_name, clip=True)
    plt.title('ERA5 CSDI')
    plt.show()
    
if __name__ == '__main__':
    range_era5_data_period("tasmin", process_csdi, mean_by_region)
    draw_csdi(get_result_data_path(indicator_name, "2011"))