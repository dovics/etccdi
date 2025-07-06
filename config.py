import cartopy.crs as ccrs
import os
import matplotlib.pyplot as plt

long_term_indictor_list = ["gdd", "pr", "hur", "rsds"]

temperature_indictor_list = [
    "tnn",
    "txx",
    "tn90p",
    "tx90p",
    "tn10p",
    "tx10p",
    "fd",
    "dtr",
]

rainfall_indictor_list = ["rx1day", "rx5day", "r10", "r95p", "sdii", "cdd", "cwd"]

indictor_list = [
    "rsds",
    "hur",
    "gdd",
    "pr",
    "cdd",
    "cwd",
    "r10",
    "r20",
    "r95p",
    "sdii",
    "rx1day",
    "rx5day",
    "tn10p",
    "tn90p",
    "tx10p",
    "tx90p",
    "tnn",
    "txx",
    "fd",
    # "id",
    "dtr",
    # "csdi"
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

zone_list = {
    "裕民县": 0,
    "额敏县": 0,
    "伊宁县": 0,
    "察布查尔锡伯自治县": 0,
    "霍城县": 0,
    "巩留县": 0,
    "温泉县": 0,
    "尼勒克县": 0,
    "新源县": 0,
    "呼图壁县": 1,
    "玛纳斯县": 1,
    "奇台县": 1,
    "吉木萨尔县": 1,
    "木垒哈萨克自治县": 1,
    "拜城县": 1,
    "轮台县": 2,
    "且末县": 2,
    "温宿县": 2,
    "沙雅县": 2,
    "新和县": 2,
    "乌什县": 2,
    "阿瓦提县": 2,
    "柯坪县": 2,
    "阿克陶县": 3,
    "疏附县": 3,
    "疏勒县": 3,
    "英吉沙县": 3,
    "泽普县": 3,
    "莎车县": 3,
    "叶城县": 3,
    "麦盖提县": 3,
    "岳普湖县": 3,
    "伽师县": 3,
    "巴楚县": 3,
    "和田县": 3,
    "墨玉县": 3,
    "皮山县": 3,
    "洛浦县": 3,
    "策勒县": 3,
    "于田县": 3,
}


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

mode_show_name = {
    "era5": "Historical",
    "ssp126": "SSP126",
    "ssp245": "SSP245",
    "ssp370": "SSP370",
    "ssp585": "SSP585",
}

downscaling_methods = {
    "rsds": "gard",
    "hur": "gard",
    "tas": "bcsd",
    "tasmax": "bcsd",
    "tasmin": "bcsd",
    "pr": "bcsd",
}

deltachange_methods = {
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
# start_year = 1980
# end_year = 2023
start_year = 2015
end_year = 2100
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

mode = "ssp245"
base_mode = "era5"
