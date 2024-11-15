import pandas as pd
from pathlib import Path
import importlib.util
from utils import get_result_data_path

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
        if Path(target).exists(): 
            print(f"{indictor} already exists")
            continue
    
    
        module_path = f"indictors\\{indictor}.py"
        spec = importlib.util.spec_from_file_location(indictor, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "calculate"):
            try:
                module.calculate()
                print(f"{indictor} calculate success")
            except Exception as e:
                print(f"Error executing {indictor}: {e}")
        else:
            print(f"Function 'calculate' not found in {indictor}")


def merge_indictors(indictor_list: list):
    df_list = [
        pd.read_csv(get_result_data_path(indictor), index_col=["name", "year"]).rename(
            columns={"value": indictor}
        )
        for indictor in indictor_list
    ]

    combined_df = pd.concat(df_list, axis=1)
    combined_df = combined_df[combined_df.index.get_level_values("year") >= 1989]
    combined_df.to_csv(get_result_data_path("combined"), float_format="%.2f")


calculate_indictors(indictor_list)
merge_indictors(indictor_list)
