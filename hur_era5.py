from download.era5 import get_era5_data
from utils import (range_era5_data, save_to_zarr, get_cf_daily_date_path)
import xarray as xr
from xclim.indicators.atmos import relative_humidity_from_dewpoint
def stat(ds: xr.Dataset):
    hur = relative_humidity_from_dewpoint(tas=ds['tas'], tdps=ds['tdps'])

    save_to_zarr(hur, get_cf_daily_date_path("hur", hur.time.dt.year.values[0]))
    return None

if __name__ == '__main__':
    #get_era5_data(["tdps", "tas"])
    range_era5_data(["tdps", "tas"], stat)