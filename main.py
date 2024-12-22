import pandas as pd
from pathlib import Path
from utils import (
    get_origin_result_data_path,
    get_outlier_result_data_path,
    import_indictor,
)

from config import use_cache, mode
from plot import map_plot, line_plot
from common.outlier import process_outlier_grid_all

from common.reshape import split_data_by_column

from logutil import info, error, warn

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


def calculate_indictors(indictor_list: list):
    for indictor in indictor_list:
        target = get_origin_result_data_path(indictor)
        if use_cache and Path(target).exists():
            info(f"{indictor} already exists")
            continue

        module = import_indictor(indictor)
        if hasattr(module, "calculate"):
            try:
                module.calculate()
                info(f"{indictor} calculate success")
            except Exception as e:
                error(f"Error executing {indictor}: {e}")
        else:
            warn(f"Function 'calculate' not found in {indictor}")


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


if __name__ == "__main__":
    calculate_indictors(indictor_list)
    df = merge_post_process_indictors(indictor_list)
    df = process_outlier_grid_all(df)
    split_data_by_column(df, get_outlier_result_data_path())
    df = merge_indictors(indictor_list)
    df.groupby(["lat", "lon"]).mean().to_csv(
        get_origin_result_data_path("all_mean"), float_format="%.2f"
    )

    map_plot(indictor_list)

    if mode != "era5":
        line_plot(indictor_list)
