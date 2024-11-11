import pandas as pd
from xclim.core.calendar import percentile_doy
import numpy as np
import xarray as xr


def df_outliers_iqr(
    df: pd.DataFrame, variable: str = "value", fill_method="mean", group_by="name", threshold=1.5
) -> pd.DataFrame:
    df = df.astype(float)
    grouped = df.groupby(group_by)[variable]

    df_list = []

    def process(x: pd.Series):
        q1 = x.quantile(0.25)
        q3 = x.quantile(0.75)
        
        iqr = q3 - q1

        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        if fill_method == "mean":
            x[(x < lower_bound) | (x > upper_bound)] = x.mean()
        elif fill_method == "median":
            x[(x < lower_bound) | (x > upper_bound)] = x.median()
        elif fill_method == "none":
            x[(x < lower_bound) | (x > upper_bound)] = None
        else:
            x = x.drop(x[(x < lower_bound) | (x > upper_bound)].index)
        df_list.append(x)

    grouped.apply(process)
    result = pd.concat(df_list)
    return result.rename(variable)

def df_outliers_mad(df: pd.DataFrame, variable: str = "value", fill_method="mean", group_by="name", threshold=3) -> pd.DataFrame:
    df = df.astype(float)
    grouped = df.groupby(group_by)[variable]

    df_list = []

    def process(x):
        median = x.median()
        
        mad = (x - median).abs().median()
        outlier = (np.abs(x - median) > threshold * mad)
        if fill_method == "mean":
            x.mask(outlier, x.mean(), inplace=True)
        elif fill_method == "median":
            x.mask(outlier, x.median(), inplace=True)
        elif fill_method == "none":
            x.mask(outlier, None, inplace=True)
        else:
            x = x.drop(outlier.index)
        df_list.append(x)

    grouped.apply(process)
    result = pd.concat(df_list)
    return result.rename(variable)

def df_outliers_none(df: pd.DataFrame, variable: str = "value", fill_method="mean", group_by="name", threshold=3) -> pd.DataFrame:
    df = df.astype(float)
    grouped = df.groupby(group_by)[variable]

    df_list = []

    def process(x):            
        df_list.append(x)

    grouped.apply(process)
    result = pd.concat(df_list)
    return result.rename(variable)