from pathlib import Path
import pandas as pd
from datetime import datetime

from config import (
    indictor_type_list,
    mode_list,
    result_data_dir,
    indictor_list,
)
from plot import (
    map_plot_multi_mode,
    line_plot_by_zone,
    line_plot,
    map_plot,
)

from utils import (
    get_outlier_result_data_path_by_mode,
    get_delta_change_result_data_path_by_mode,
    get_git_commit_id,
    filter_by_year,
    get_result_data,
)

from common.zip_target import ZipTarget
from common.reshape import split_data_by_column
from common.sort import sort_by_contry


def save_output_data(df: pd.DataFrame, mode: str, target: str):
    Path(f"{target}").mkdir(parents=True, exist_ok=True)
    df = filter_by_year(df, mode)
    sort_by_contry(df).to_csv(
        f"{target}/all.csv", index=False, columns=["name", "year"] + indictor_list
    )
    split_data_by_column(df.set_index(["name", "year"]), f"{target}")


if __name__ == "__main__":
    target = ZipTarget()

    for indictor_type in indictor_type_list:
        map_plot_multi_mode(
            indictor_type_list[indictor_type],
            target=f"{result_data_dir}/map_{indictor_type}.png",
        )
        line_plot_by_zone(
            indictor_type_list[indictor_type],
            target=f"{result_data_dir}/line_{indictor_type}.png",
        )
        target.add_file(f"{result_data_dir}/map_{indictor_type}.png")
        target.add_file(f"{result_data_dir}/line_{indictor_type}.png")

    for mode in mode_list:
        target_dir = f"{result_data_dir}/{mode}"
        result_data = get_result_data(mode)
        save_output_data(result_data, mode, target_dir)
        map_plot(
            indictor_list,
            target=f"{target_dir}/map.png",
            local_mode=mode,
        )
        target.add_folder(target_dir)

    line_plot(
        indictor_list,
        target=f"{result_data_dir}/line.png",
        post_process=True,
    )
    target.add_file(f"{result_data_dir}/line.png")
    current = datetime.now().strftime("%Y%m%d_%H%M%S")
    commit_id = get_git_commit_id()
    target.save(f"{result_data_dir}/output_{current}_{commit_id}.zip")
