import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from plot import (
    calculate_slope,
    add_point_map,
    add_number,
    draw_base_map,
    add_title,
    mode_color_map,
)
from config import (
    long_term_indictor_list,
    temperature_indictor_list,
    rainfall_indictor_list,
    target_crs,
    mode_show_name,
    mode_list,
    zone_list,
)
from utils import (
    get_outlier_result_data_path_by_mode,
    get_delta_change_result_data_path_by_mode,
    import_indictor,
    add_region_latlon,
)


def get_filter(all_data):
    Q1 = np.percentile(all_data, 25)
    Q3 = np.percentile(all_data, 75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    lower_bound = Q1 - 1.5 * IQR

    def filter(df, indictor):
        df.loc[df[indictor] > upper_bound, indictor] = upper_bound
        df.loc[df[indictor] < lower_bound, indictor] = lower_bound
        return df

    return filter


def map_plot_multi_mode(
    indictor_list,
    target="result_data/map_multi_mode.png",
):
    slope = {}
    for mode in mode_list:
        point_df = pd.read_csv(get_outlier_result_data_path_by_mode("all", mode))
        slope[mode] = add_region_latlon(calculate_slope(point_df))

    i = 0
    row = len(indictor_list)
    col = len(mode_list)

    fig = plt.figure(figsize=(8 * col, 6 * row))
    for indictor in indictor_list:
        module = import_indictor(indictor)
        for mode in mode_list:
            i += 1
            ax = fig.add_subplot(row, col, i, projection=target_crs)
            draw_base_map(ax=ax, clip=True)
            add_title(ax, f"{module.show_name} (${module.unit}$)")

            add_point_map(
                slope[mode],
                indictor,
                ax,
                unit=module.unit + "\cdot 10a^{-1}",
                legend_location=(0, 0.625),
                color=True,
            )

            add_number(ax, f"({chr(96 + i)})")
            if i <= col:
                add_title(
                    ax, f"{mode_show_name[mode]}", fontsize=24, location=(0.1, 1.05)
                )

    plt.subplots_adjust(wspace=0, hspace=0)
    plt.savefig(target, dpi=300)


def line_plot_by_zone(indictor_list: list, target="result_data/line_by_zone.png"):
    row = 4  # zone count
    col = len(indictor_list)
    ax_dict = {}
    fig = plt.figure(figsize=(8 * col, 6 * row))

    for i in range(row):
        ax_dict[i] = {}
        for j, indictor in enumerate(indictor_list):
            index = i * col + j + 1
            ax_dict[i][indictor] = fig.add_subplot(row, col, index)
            module = import_indictor(indictor)
            add_title(ax_dict[i][indictor], module.show_name)
            add_number(ax_dict[i][indictor], f"({chr(96 + index)})")

    for mode in mode_list:
        if mode != "era5":
            df = pd.read_csv(
                get_delta_change_result_data_path_by_mode("all", local_mode=mode),
                index_col=["year"],
            )
        else:
            df = pd.read_csv(
                get_outlier_result_data_path_by_mode("all", local_mode=mode),
                index_col=["year"],
            )

        df["zone"] = df["name"].apply(
            lambda x: zone_list[x] if x in zone_list else "Unknown"
        )

        for zone, zone_df in df.groupby("zone"):
            zone_df = zone_df.drop(columns="name").groupby("year")
            percentile_10 = zone_df.quantile(0.1).rolling(window=5).mean()
            percentile_90 = zone_df.quantile(0.9).rolling(window=5).mean()
            mean_df = zone_df.mean()
            for indictor in indictor_list:
                ax = ax_dict[zone][indictor]
                mean_df[indictor].plot(
                    x="year",
                    y=indictor,
                    ax=ax,
                    color=mode_color_map[mode],
                    label=mode,
                )
                years = mean_df.index.values
                ax.fill_between(
                    years,
                    percentile_10[indictor],
                    percentile_90[indictor],
                    color=mode_color_map[mode],
                    alpha=0.2,
                    label=f"{mode} 10%-90% range",
                )
    
    for i in range(row):
        for j, indictor in enumerate(indictor_list):
            module = import_indictor(indictor)
            add_title(ax_dict[i][indictor], module.show_name)
            add_number(ax_dict[i][indictor], f"({chr(96 + index)})")

    for i in range(row):
        add_title(
            ax_dict[i][indictor_list[0]],
            f"Zone {i + 1}",
            fontsize=24,
            location=(-0.15, 0.5),
            rotation=90,
        )
        
    plt.subplots_adjust(wspace=0.1, hspace=0)
    plt.savefig(target, dpi=300)

if __name__ == "__main__":
    map_plot_multi_mode(long_term_indictor_list, target="result_data/map_long_term.png")
    map_plot_multi_mode(
        temperature_indictor_list, target="result_data/map_temperature.png"
    )
    map_plot_multi_mode(rainfall_indictor_list, target="result_data/map_rainfall.png")

    line_plot_by_zone(long_term_indictor_list, target="result_data/line_long_term.png")
    line_plot_by_zone(
        temperature_indictor_list, target="result_data/line_temperature.png"
    )
    line_plot_by_zone(rainfall_indictor_list, target="result_data/line_rainfall.png")