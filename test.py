from download.era5 import get_era5_data

if __name__ == "__main__":
    get_era5_data("tas")
    get_era5_data("tasmin")
    get_era5_data("tasmax")
    get_era5_data("pr")