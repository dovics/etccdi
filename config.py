import cartopy.crs as ccrs
import os
import matplotlib.pyplot as plt

indictor_list = [
    "rsds",
    "hur",
    "gdd",
    "pr",
    "cwd",
    "r10",
    "r95p",
    "rx1day",
    "tn90p",
    "tx90p",
    "txx",
    "fd",
]

country_list = [
    "裕民县",
    "额敏县",
    "伊宁县",
    "察布查尔锡伯自治县",
    "霍城县",
    "巩留县",
    "温泉县",
    "尼勒克县",
    "新源县",
    "呼图壁县",
    "玛纳斯县",
    "奇台县",
    "吉木萨尔县",
    "木垒哈萨克自治县",
    "拜城县",
    "轮台县",
    "且末县",
    "温宿县",
    "沙雅县",
    "新和县",
    "乌什县",
    "阿瓦提县",
    "柯坪县",
    "阿克陶县",
    "疏附县",
    "疏勒县",
    "英吉沙县",
    "泽普县",
    "莎车县",
    "叶城县",
    "麦盖提县",
    "岳普湖县",
    "伽师县",
    "巴楚县",
    "和田县",
    "墨玉县",
    "皮山县",
    "洛浦县",
    "策勒县",
    "于田县",
]

cmip6_model_list = [
    "ACCESS-CM2",
    "ACCESS-ESM1-5",
    "BCC-CSM2-MR",
    "CanESM5",
    "EC-Earth3",
    "FGOALS-g3",
    "INM-CM4-8",
    "INM-CM5-0",
    "IPSL-CM6A-LR",
    "KACE-1-0-G",
    "MIROC-ES2L",
    "MIROC6",
    "MPI-ESM1-2-HR",
    "MRI-ESM2-0",
    "NorESM2-MM",
    "UKESM1-0-LL",
]

mode_list = [
    "era5",
    "ssp126",
    "ssp245",
    "ssp370",
    "ssp585",
]  # "ssp126", "ssp245", "ssp370", "ssp585"
downscaling_methods = {
    # "rsds": "gard",
    # "hur": "gard",
    # "tas": "bcsd",
    # "tasmax": "bcsd",
    # "tasmin": "bcsd",
    # "pr": "bcsd",
    "rsds": "none",
    "hur": "dcm",
    "hurs": "dcm",
    "tas": "dcm",
    "tasmax": "dcm",
    "tasmin": "dcm",
    "pr": "qdm",
}

cmip6_data_dir = "Z:/fangjiamin/bias_correction/result_data"
era5_data_dir = "era5_data"
result_data_dir = "result_data"
intermediate_data_dir = "intermediate_data"

period_start = "10-01"
period_end = "06-30"
start_year = 1980
end_year = 2023
# start_year = 2015
# end_year = 2100
base_start_year = 1961
base_end_year = 1990

cds_api_key = os.environ.get("CDS_API_KEY")

use_cache = True

download_era5 = False
use_download_cache = use_cache


target_crs = ccrs.AlbersEqualArea(
    central_longitude=105, central_latitude=35, standard_parallels=(25, 47)
)

gdf_crs = ccrs.PlateCarree()

tas_colormap = plt.get_cmap("OrRd")
pr_colormap = plt.get_cmap("Blues")

max_outlier = 5

mode = "ssp126"
base_mode = "ssp585"
