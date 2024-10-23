from utils import (load_era5_daily_data, get_year_from_path)
from config import era5_data_dir
from pathlib import Path

if __name__ == "__main__":
    for file in Path(era5_data_dir).rglob(f'tasmin_era5_daily_*.nc'):
        if file.is_file():
            file.rename(f"{era5_data_dir}/tasmin_era5_origin_{get_year_from_path(file.name)}.nc")
    # ds = load_era5_daily_data("tasmin", "2019")
    # ds = ds.chunk({'valid_time': 100})
    # mn2t = ds.sortby('valid_time')

    # # 按日期分组并计算每组的最小值
    # daily_min_temps = mn2t.groupby('valid_time.date').min(dim='valid_time')

    # # 打印结果
    # print(daily_min_temps)