import pandas as pd
from pathlib import Path
import importlib.util
from utils import (
    get_origin_result_data_path,
    add_region_latlon,
    get_outlier_result_data_path,
)
from matplotlib import pyplot as plt
from config import target_crs, use_cache
from scipy.stats import linregress
from plot import add_point_map, add_number
from common.outlier import process_outlier_grid_all

from common.reshape import split_data_by_column

indictor_list = [
    # "rsds",
    # "hur",
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


def import_indictor(indictor: str):
    module_path = f"indictors\\{indictor}.py"
    spec = importlib.util.spec_from_file_location(indictor, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def calculate_indictors(indictor_list: list):
    for indictor in indictor_list:
        target = get_origin_result_data_path(indictor)
        if use_cache and Path(target).exists():
            print(f"{indictor} already exists")
            continue

        module = import_indictor(indictor)
        if hasattr(module, "calculate"):
            try:
                module.calculate()
                print(f"{indictor} calculate success")
            except Exception as e:
                print(f"Error executing {indictor}: {e}")
        else:
            print(f"Function 'calculate' not found in {indictor}")


def merge_post_process_indictors(indictor_list: list):
    df_list = [
        pd.read_csv(
            get_origin_result_data_path(indictor + "_post_process"),
            index_col=["name", "year"],
        ).rename(columns={"value": indictor})
        for indictor in indictor_list
    ]

    combined_df = pd.concat(df_list, axis=1)
    combined_df = combined_df[combined_df.index.get_level_values("year") >= 1989]
    combined_df.to_csv(
        get_origin_result_data_path("combined_post_process"), float_format="%.2f"
    )
    return combined_df


def merge_indictors(indictor_list: list):
    df_list = [
        pd.read_csv(
            get_origin_result_data_path(indictor), index_col=["lat", "lon", "year"]
        )[indictor]
        for indictor in indictor_list
    ]

    combined_df = pd.concat(df_list, axis=1)
    combined_df = combined_df[combined_df.index.get_level_values("year") >= 1989]
    combined_df.to_csv(get_origin_result_data_path("all"), float_format="%.2f")
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
    point_df = pd.read_csv(get_outlier_result_data_path("all"))
    slope = calculate_slope(point_df)
    slope = add_region_latlon(slope)

    csv_path = get_origin_result_data_path("all_mean")
    df = pd.read_csv(csv_path)
    fig = plt.figure(figsize=(24, 24))
    i = 0
    for indictor in indictor_list:
        module = import_indictor(indictor)
        ax = fig.add_subplot(4, 3, i + 1, projection=target_crs)
        module.draw(df, ax)

        if hasattr(module, "unit"):
            add_point_map(slope, indictor, ax, unit=module.unit + "\cdot 10a^{-1}", legend_location=(0, 0.625))
        else:
            add_point_map(slope, indictor, ax, legend_location=(0, 0.7))
        add_number(ax, f"({chr(97 + i)})")
        i += 1

    plt.savefig("result_data/plot.png", dpi=300)


if __name__ == "__main__":
    calculate_indictors(indictor_list)
    df = merge_post_process_indictors(indictor_list)
    df = process_outlier_grid_all(df)
    split_data_by_column(df, get_outlier_result_data_path())
    df = merge_indictors(indictor_list)
    df.groupby(["lat", "lon"]).mean().to_csv(
        get_origin_result_data_path("all_mean"), float_format="%.2f"
    )

    plot(indictor_list)
