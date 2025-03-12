import pandas as pd
import numpy as np
from scipy import stats
from utils import get_outlier_result_data_path
from config import max_outlier
from common.reshape import split_data_by_column

def outliers_framework(df: pd.DataFrame, process, variable: str, group_by):
    df = df.astype(float)
    grouped = df[variable].groupby(group_by)

    df_list = []

    grouped.apply(process, df_list)
    result = pd.concat(df_list)
    return result.rename(variable)


def df_outliers_zcore(
    df: pd.DataFrame,
    variable: str = "value",
    fill_method="mean",
    group_by="name",
    threshold=3,
):
    def process(x: pd.Series, df_list: list):
        z_scores = stats.zscore(x)
        outliers = np.abs(z_scores) > threshold
        if len(x[outliers]) > max_outlier:
            raise Exception(f"Too many outliers({len(outliers)})")

        if fill_method == "mean":
            x[outliers] = x[~outliers].mean()
        elif fill_method == "median":
            x[outliers] = x[~outliers].median()
        elif fill_method == "none":
            x[outliers] = None
        else:
            x = x.drop(x[outliers].index)
        df_list.append(x)

    return outliers_framework(df, process, variable, group_by)


def df_outliers_iqr(
    df: pd.DataFrame,
    variable: str = "value",
    fill_method="mean",
    group_by="name",
    threshold=1.5,
) -> pd.DataFrame:
    def process(x: pd.Series, df_list: list):
        q1 = x.quantile(0.25)
        q3 = x.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        if len(x[(x < lower_bound) | (x > upper_bound)]) > max_outlier:
            raise Exception(
                f"Too many outliers({len(x[(x < lower_bound) | (x > upper_bound)])})"
            )

        if fill_method == "mean":
            x[(x < lower_bound) | (x > upper_bound)] = x.mean()
        elif fill_method == "median":
            x[(x < lower_bound) | (x > upper_bound)] = x.median()
        elif fill_method == "none":
            x[(x < lower_bound) | (x > upper_bound)] = None
        else:
            x = x.drop(x[(x < lower_bound) | (x > upper_bound)].index)
        df_list.append(x)

    return outliers_framework(df, process, variable, group_by)


def df_outliers_mad(
    df: pd.DataFrame,
    variable: str = "value",
    fill_method="mean",
    group_by="name",
    threshold=3,
) -> pd.DataFrame:
    def process(x: pd.Series, df_list: list):
        median = x.median()

        mad = (x - median).abs().median()
        outlier = np.abs(x - median) > threshold * mad
        if len(x[outlier]) > max_outlier:
            raise Exception(f"Too many outliers({len(x[outlier])})")

        if fill_method == "mean":
            x.mask(outlier, x.mean(), inplace=True)
        elif fill_method == "median":
            x.mask(outlier, x.median(), inplace=True)
        elif fill_method == "none":
            x.mask(outlier, None, inplace=True)
        else:
            x = x.drop(outlier.index)
        df_list.append(x)

    return outliers_framework(df, process, variable, group_by)


def df_outliers_none(
    df: pd.DataFrame,
    variable: str = "value",
    fill_method="mean",
    group_by="name",
    threshold=3,
) -> pd.DataFrame:
    def process(x: pd.Series, df_list: list):
        df_list.append(x)

    return outliers_framework(df, process, variable, group_by)


df_outlier_method = {
    "iqr": df_outliers_iqr,
    "mad": df_outliers_mad,
    "none": df_outliers_none,
    "zcore": df_outliers_zcore,
}

outlier_fill_method = {
    "mean": "mean",
    "median": "median",
    "none": "none",
}


def process_outlier(
    df: pd.DataFrame,
    variable: str,
    method: str = "mad",
    threshold: float = 3,
    fill_method: str = "median",
) -> pd.DataFrame:
    process = df_outlier_method[method]

    result = process(
        df,
        variable=variable,
        group_by="name",
        fill_method=fill_method,
        threshold=threshold,
    )
    result = result.reset_index()

    return result


def process_outlier_grid(
    df: pd.DataFrame,
    variable: str,
    method: str = "mad",
    start_threshold: float = 0,
    end_threshold: float = 10,
    stop: float = 0.5,
):
    for i in np.arange(start_threshold, end_threshold, stop):
        try:
            return process_outlier(df, variable, method, i)
        except Exception as e:
            print(f"Info: {variable} {method} failed {i}: {e}")
            continue

def process_outlier_grid_all(df: pd.DataFrame, method: str = "mad") -> pd.DataFrame:
    total_result = df.copy()
    for variable in df.columns:
        result = process_outlier_grid(df, variable, method)
        if result is None:
            print(f"{variable} {method} error")
            continue
        total_result[variable] = result.set_index(["name", "year"])[variable]
        print(f"{variable} {method} success")

    total_result.to_csv(get_outlier_result_data_path(f"all"), float_format="%.2f")
    split_data_by_column(df, get_outlier_result_data_path())
    return total_result
