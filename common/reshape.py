import pandas as pd
from pathlib import Path


def split_data_by_column(df: pd.DataFrame, path_prefix = "result_data"):
    if Path(path_prefix).exists() == False:
        Path(path_prefix).mkdir()

    for variable in df.columns:
        result = df[variable].reset_index().pivot(
            index="name", columns="year", values=variable
        )
        result.to_csv(f"{path_prefix}/{variable}.csv", float_format="%.2f")
