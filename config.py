import cartopy.crs as ccrs

country_list = [
    "伊宁县",
    "察布查尔锡伯自治县",
    "霍城县",
    "巩留县",
    "新源县",
    "尼勒克县",
    "额敏县",
    "裕民县",
    "温泉县",
    "呼图壁县",
    "玛纳斯县",
    "奇台县",
    "吉木萨尔县",
    "木垒哈萨克自治县",
    "轮台县",
    "且末县",
    "温宿县",
    "沙雅县",
    "新和县",
    "拜城县",
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

era5_data_dir = "era5_data"
result_data_dir = "result_data"
intermediate_data_dir = "intermediate_data"

period_start = "10-01"
period_end = "06-30"
start_year = 1980
end_year = 2023

base_start_year = 1961
base_end_year = 1990

# cds_api_key = os.environ.get("CDS_API_KEY")
# cds_api_key = "11a309e4-98cb-4f04-a1c9-215cf56c2c1b" # wang
cds_api_key = "d8d390f1-abf3-46f7-b3c0-6bfa8b5e1f4c"  # fang
use_cache = True

download_era5 = False
use_download_cache = use_cache

# crs = ccrs.UTM(zone=48, southern_hemisphere=False)
# crs = ccrs.PlateCarree()
# crs = ccrs.Mercator()
crs = ccrs.Robinson()