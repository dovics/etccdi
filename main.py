import pandas as pd
from pathlib import Path
import importlib.util
from utils import (
    get_result_data_path,
    add_region_latlon
)
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
from scipy.stats import linregress
from plot import draw_point_map

indictor_list = [
    "cdd",
    "csdi",
    "cwd",
    "dtr",
    "fd",
    "gdd",
    "id",
    "r10",
    "r20",
    "r95p",
    "rx1day",
    "rx5day",
    "sdii",
    "tn10p",
    "tn90p",
    "tnn",
    "tx10p",
    "tx90p",
    "txx",
]


def calculate_indictors(indictor_list: list):
    for indictor in indictor_list:
        target = get_result_data_path(indictor)
        # if Path(target).exists(): 
        #     print(f"{indictor} already exists")
        #     continue
    
        
        module_path = f"indictors\\{indictor}.py"
        spec = importlib.util.spec_from_file_location(indictor, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "calculate"):
            try:
                module.calculate(process=False)
                print(f"{indictor} calculate success")
            except Exception as e:
                print(f"Error executing {indictor}: {e}")
        else:
            print(f"Function 'calculate' not found in {indictor}")


def merge_post_process_indictors(indictor_list: list):
    df_list = [
        pd.read_csv(get_result_data_path(indictor + "_post_process"), index_col=["name", "year"]).rename(
            columns={"value": indictor}
        )
        for indictor in indictor_list
    ]

    combined_df = pd.concat(df_list, axis=1)
    combined_df = combined_df[combined_df.index.get_level_values("year") >= 1989]
    combined_df.to_csv(get_result_data_path("combined_post_process"), float_format="%.2f")
    return combined_df


def merge_indictors(indictor_list: list):
    df_list = [
        pd.read_csv(get_result_data_path(indictor), index_col=["lat", "lon", "year"])[indictor]
        for indictor in indictor_list
    ]

    combined_df = pd.concat(df_list, axis=1)
    combined_df = combined_df[combined_df.index.get_level_values("year") >= 1989]
    combined_df.to_csv(get_result_data_path("combined"), float_format="%.2f")
    return combined_df

def calculate_slope(df: pd.DataFrame):
    def process_slope(county_df: pd.DataFrame):
        result = pd.Series()
        for c in county_df.columns:
            if c == "year":
                continue
            line = linregress(county_df["year"], county_df[c])

            result[c] = round(line.slope * 10, 2)
            result[c + "_up"] = line.slope > 0
            result[c + "_sign"] = line.pvalue < 0.05
        return result

    slope_result = df.groupby("name").apply(process_slope)

    return slope_result

def plot(indictor_list: list):
    point_df = pd.read_csv(get_result_data_path("combined_post_process"))
    slope = calculate_slope(point_df)
    slope = add_region_latlon(slope)
    
    csv_path = get_result_data_path("combined_mean")
    df = pd.read_csv(csv_path)
    fig = plt.figure(figsize=(30, 24))
    i = 0
    for indictor in indictor_list:
        module_path = f"indictors\\{indictor}.py"
        spec = importlib.util.spec_from_file_location(indictor, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ax = fig.add_subplot(4, 5, i+1, projection=ccrs.PlateCarree())
        module.draw(df, ax)
        draw_point_map(slope, indictor, ax)

        i += 1
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # calculate_indictors(indictor_list)
    # df = merge_post_process_indictors(indictor_list)
    # df = merge_indictors(indictor_list)
    # df.groupby(["lat", "lon"]).mean().to_csv(get_result_data_path("combined_mean"))
    
    plot(indictor_list)
