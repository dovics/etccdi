import pandas as pd
from common.reshape import split_data_by_column
from utils import (
    get_outlier_result_data_path_by_mode,
    get_delta_change_result_data_path_by_mode,
)
from config import mode, indictor_list
from logutil import info


def delta_change_by_year(
    df: pd.DataFrame,
    base_df: pd.DataFrame,
    variable: str,
    start: int = 2015,
    step: int = 5,
) -> pd.DataFrame:
    for year in range(start, df["year"].max(), step):
        start_year = year
        end_year = year + step
        first_df = df[(df["year"] >= start_year) & (df["year"] < end_year)]
        first_min = first_df[variable].min()
        first_max = first_df[variable].max()
        if first_max - first_min != 0 and first_max - first_min != 0.0:
            break

    if end_year >= df["year"].max():
        first_min = df[variable].min()
        first_max = df[variable].max()
        if first_max - first_min == 0 or first_max - first_min == 0.0:
            if first_max == 0 and first_min == 0.0:
                return df[variable]

            raise ValueError(
                f"Can't find valid data for {variable} in {df['name'].iloc[0]}"
            )
    info(f"start delta change for {variable} base {start_year} to {end_year}")
    base_min = base_df[variable].min()
    base_max = base_df[variable].max()
    scale_factor = (base_max - base_min) / (first_max - first_min)
    offset = base_min - scale_factor * first_min

    return df[variable] * scale_factor + offset


def delta_change_indictor(df: pd.DataFrame, base_df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for indictor in ["rsds", "hur","pr", "cwd", "r10", "r95p", "rx1day"]:
        result[indictor] = delta_change_by_year(df, base_df, indictor)

    return result


def delta_change(df: pd.DataFrame, base_df: pd.DataFrame) -> pd.DataFrame:
    base_groups = dict(list(base_df.groupby("name")))
    df = df.groupby("name").apply(
        lambda x: delta_change_indictor(
            x,
            base_groups[x.name],
        )
    )

    df = df.reset_index(drop=True)
    return df


def process_delta_change_all() -> pd.DataFrame:
    get_data_path = get_outlier_result_data_path_by_mode
    
    for mode in ["ssp126", "ssp245", "ssp370", "ssp585"]:
        info(f"Processing delta change for {mode}")
        df = pd.read_csv(get_data_path("all", mode))
        base_df = pd.read_csv(get_data_path("all", "era5"))

        result = delta_change(df, base_df)
        result.to_csv(get_delta_change_result_data_path_by_mode("all", mode), float_format="%.2f")
        result.set_index(["name", "year"], inplace=True)
        split_data_by_column(result, get_delta_change_result_data_path_by_mode(None, mode))
