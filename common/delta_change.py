import pandas as pd
from common.reshape import split_data_by_column
from utils import (
    get_outlier_result_data_path_by_mode,
    get_delta_change_result_data_path_by_mode,
    get_origin_result_data_path_by_mode,
)
from config import indictor_list
from logutil import info
from common.sort import sort_by_contry

def delta_change_by_scale(
    df: pd.DataFrame,
    base_df: pd.DataFrame,
    variable: str,
    start: int = 2015,
    step: int = 5,
    scale: float = 1.0,
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

    base_min = base_df[variable].min()
    base_max = base_df[variable].max()
    scale_factor = (base_max - base_min) / (first_max - first_min)
    offset = base_min - scale_factor * first_min * scale
    info(
        f"start delta change for {variable} base {start_year} to {end_year}, scale_factor {scale_factor}. offset {offset}"
    )
    result = df[variable] * scale_factor * scale + offset
    return result.abs()


def delta_change_by_mean(
    df: pd.DataFrame,
    base_df: pd.DataFrame,
    variable: str,
    start: int = 2015,
    step: int = 5,
):

    base_mean = base_df[variable].mean()
    start_mean = df[(df["year"] >= start) & (df["year"] < start + step)][
        variable
    ].mean()
    result = df[variable] - start_mean + base_mean
    return result.abs()

def delta_change_old(df: pd.DataFrame, base_df: pd.DataFrame, variable: str) -> pd.DataFrame:
    # 假设 df 和 base_df 中有一个时间列 'year'
    df_2020_2025 = df[(df['year'] >= 2020) & (df['year'] <= 2025)]
    
    # 计算 2020-2025 年的最小值和最大值
    base_min = base_df[variable].min()
    base_max= base_df[variable].max()
    
    df_min_2020_2025 = df_2020_2025[variable].min()
    df_max_2020_2025 = df_2020_2025[variable].max()
    
    # 应用最小-最大归一化公式，将 2020-2025 年的数据缩放到新的范围
    df.loc[(df['year'] >= 2020) & (df['year'] <= 2025), variable] = (
        (df_2020_2025[variable] - df_min_2020_2025) / (df_max_2020_2025 - df_min_2020_2025)
    ) * (base_max - base_min) + base_min
    
    # 计算缩放比例
    scale_factor = (base_max - base_min) / (df_max_2020_2025 - df_min_2020_2025)
    offset = base_min - scale_factor * df_min_2020_2025
    
    # 将缩放比例应用到其他年份的数据
    df.loc[(df['year'] < 2020) | (df['year'] > 2025), variable] = (
        df.loc[(df['year'] < 2020) | (df['year'] > 2025), variable] * scale_factor + offset
    )
    
    return df[variable]

def delta_change_indictor(
    df: pd.DataFrame, base_df: pd.DataFrame, mode: str
) -> pd.DataFrame:
    result = df.copy()
    for indictor in ["rsds", "hur", "pr", "cwd", "r10", "r95p", "rx1day"]:
        if indictor in df.columns:
            result[indictor] = delta_change_by_scale(df, base_df, indictor)

    for indictor in ["rsds"]:
        if indictor in df.columns:
            result[indictor] = delta_change_old(df, base_df, indictor)

    return result


def delta_change(
    df: pd.DataFrame, base_df: pd.DataFrame, mode, index_col
) -> pd.DataFrame:
    base_groups = dict(list(base_df.groupby(index_col)))
    df = df.groupby(index_col).apply(
        lambda x: delta_change_indictor(
            x,
            base_groups[x.name],
            mode,
        )
    )

    df = df.reset_index(drop=True)
    return df


def process_delta_change_all(post_process: bool = False) -> pd.DataFrame:
    if post_process:
        get_era5_data_path = get_outlier_result_data_path_by_mode
        get_cmip6_data_path = lambda x, local_mode: get_origin_result_data_path_by_mode(
            x + "_post_process", local_mode
        )
        index = "name"
    else:
        get_cmip6_data_path = get_origin_result_data_path_by_mode
        get_era5_data_path = get_origin_result_data_path_by_mode
        index = ["lat", "lon"]

    for mode in ["ssp126", "ssp245", "ssp370", "ssp585"]:
        info(f"Processing delta change for {mode}")
        df = pd.read_csv(get_cmip6_data_path("all", mode))
        base_df = pd.read_csv(get_era5_data_path("all", "era5"))

        result = delta_change(df, base_df, mode, index)
        sort_by_contry(result).to_csv(
            get_delta_change_result_data_path_by_mode("all", mode),
            float_format="%.2f",
            index=False,
        )
        if post_process:
            result.set_index(["name", "year"], inplace=True)
            split_data_by_column(
                result,
                get_delta_change_result_data_path_by_mode(None, mode),
                index,
            )
