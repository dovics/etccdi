import matplotlib.patches as mpatches
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.path import Path

import cartopy.crs as ccrs
from cartopy.mpl.patch import geos_to_path
from cartopy.feature import ShapelyFeature
from cartopy import feature as cfeat
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from scipy.stats import linregress
from common.delta_change import delta_change
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr

from utils import (
    add_region_latlon,
    get_gdf_list,
    find_region_by_name,
    get_origin_result_data_path,
    get_origin_result_data_path_by_mode,
    get_outlier_result_data_path,
    get_delta_change_result_data_path_by_mode,
    get_outlier_result_data_path_by_mode,
    import_indictor,
    load_daily_data,
)
from config import country_list, target_crs, gdf_crs, mode, mode_list

province_full_geojson = "static/xinjiang_full.json"
province_border_geojson = "static/xinjiang.json"


def draw_border(ax, gdf=None):
    if gdf is None:
        gdf = gpd.read_file(province_border_geojson)
    provinces = cfeat.ShapelyFeature(
        gdf.geometry, gdf_crs, edgecolor="black", alpha=1, facecolor="none"
    )

    ax.add_feature(provinces, linewidth=1)


def new_plot(show_border=True, show_grid=True, show_country=False, subregions=None):
    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.subplots(1, 1, subplot_kw={"projection": gdf_crs})

    gdf = gpd.read_file(province_border_geojson)
    (minx, miny, maxx, maxy) = get_bounds(gdf, margin=1)
    ax.set_extent([minx, maxx, miny, maxy], crs=gdf_crs)
    if not show_country and show_border:
        draw_border(ax, gdf=gdf)

    if show_country:
        region_list = []
        for gdf in get_gdf_list():
            for _, region in gdf.iterrows():
                region_list.append(
                    gpd.GeoDataFrame([region], geometry=[region.geometry], crs=gdf_crs)
                )
        merged_gdf = gpd.pd.concat(region_list)
        provinces = cfeat.ShapelyFeature(
            merged_gdf.geometry, gdf_crs, edgecolor="k", alpha=0.7, facecolor="none"
        )
        ax.add_feature(provinces, linewidth=1)

    if show_grid:
        gl = ax.gridlines(
            crs=gdf_crs,
            draw_labels=True,
            linewidth=1.2,
            color="k",
            alpha=0.5,
            linestyle="--",
        )

    if subregions is not None:
        for subregion in subregions:
            region = find_region_by_name(subregion)
            regionFeature = cfeat.ShapelyFeature(
                region.geometry, gdf_crs, edgecolor="red", alpha=0.7, facecolor="none"
            )
            ax.add_feature(regionFeature, linewidth=1)

    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlocator = mticker.FixedLocator(np.arange(minx, maxx + 10, 10))
    gl.ylocator = mticker.FixedLocator(np.arange(miny, maxy + 10, 10))

    return fig, ax


def get_bounds(gdf, margin=1):
    from shapely.geometry import MultiPolygon

    minx, miny, maxx, maxy = float("inf"), float("inf"), float("-inf"), float("-inf")

    for geom in gdf.geometry:
        if isinstance(geom, MultiPolygon):
            for polygon in geom.geoms:
                bounds = polygon.bounds
                minx = min(minx, bounds[0])
                miny = min(miny, bounds[1])
                maxx = max(maxx, bounds[2])
                maxy = max(maxy, bounds[3])
        else:
            bounds = geom.bounds
            minx = min(minx, bounds[0])
            miny = min(miny, bounds[1])
            maxx = max(maxx, bounds[2])
            maxy = max(maxy, bounds[3])

    return (minx - margin, miny - margin, maxx + margin, maxy + margin)


def draw_country_map(df: pd.DataFrame, fill=True):
    region_list = []
    for gdf in get_gdf_list():
        for _, region in gdf.iterrows():
            region_value = df[df["name"] == region["name"]]
            if not region_value.empty:
                region["value"] = region_value["value"].item()
            else:
                region["value"] = None

            region_list.append(
                gpd.GeoDataFrame([region], geometry=[region.geometry], crs=gdf_crs)
            )
    merged_gdf = gpd.pd.concat(region_list)
    if fill:
        merged_gdf.plot(
            column="value", edgecolor="black", linewidth=1, cmap="coolwarm", legend=True
        )
    else:
        merged_gdf.boundary.plot(edgecolor="black", linewidth=1)


def clip_df_data(df: pd.DataFrame, gdf: gpd.GeoDataFrame = None):
    if gdf is None:
        gdf = gpd.read_file(province_border_geojson)
    (minx, miny, maxx, maxy) = get_bounds(gdf, margin=0.25)
    return df[
        (df["lat"] >= miny)
        & (df["lat"] <= maxy)
        & (df["lon"] >= minx)
        & (df["lon"] <= maxx)
    ]


def draw_latlon_map(
    df: pd.DataFrame, variable: str, clip=True, cmap="coolwarm", ax=None, levels=15
):
    gdf = gpd.read_file(province_border_geojson)
    (minx, miny, maxx, maxy) = get_bounds(gdf, margin=0.25)
    df = df[
        (df["lat"] >= miny)
        & (df["lat"] <= maxy)
        & (df["lon"] >= minx)
        & (df["lon"] <= maxx)
    ]
    lats = df["lat"].values
    lons = df["lon"].values
    LON, LAT = np.meshgrid(np.unique(lons), np.unique(lats))
    VALUE = df.pivot(index="lat", columns="lon", values=variable).values

    if ax is None:
        _, ax = new_plot(subregions=country_list)

    ax.set_extent([minx + 1, maxx - 0.5, miny + 2, maxy - 2], crs=gdf_crs)
    draw_border(ax, gdf=gdf)
    draw_north_arrow(ax)
    draw_line(ax)
    contour = ax.contourf(LON, LAT, VALUE, levels=levels, cmap=cmap, transform=gdf_crs)

    if clip:
        geom = ax.projection.project_geometry(gdf.geometry.unary_union, gdf_crs)
        path = Path.make_compound_path(*geos_to_path(geom))
        for col in ax.collections:
            col.set_clip_path(path, ax.transData)

    add_scaler(ax, length=200)

    plt.colorbar(contour, ax=ax, pad=0.05, fraction=0.03)


def add_point_map(
    df: pd.DataFrame,
    variable: str,
    ax: plt.Axes = None,
    unit=None,
    legend_location=None,
):
    symbols = {
        (True, False): "△",
        (True, True): "▲",
        (False, False): "▽",
        (False, True): "▼",
    }

    for (up, sign), symbol in symbols.items():
        subset = df[(df[variable + "_up"] == up) & (df[variable + "_sign"] == sign)]
        for _, row in subset.iterrows():
            ax.annotate(
                symbol,
                xy=(row["lon"], row["lat"]),
                transform=gdf_crs,
                fontsize="small",
            )

            # right
            # ax.annotate(
            #     str(abs(row[variable])),
            #     xy=(row["lon"] + 0.4, row["lat"] + 0.05),
            #     transform=gdf_crs,
            #     fontsize="small",
            # )

            # low
            value = row[variable]
            if value >= 10:
                formatted_value = f"{value:.1f}"
            else:
                formatted_value = f"{value:.2f}"
            ax.annotate(
                formatted_value,
                xy=(row["lon"] - 0.1, row["lat"] - 0.4),
                transform=gdf_crs,
                fontsize="xx-small",
            )
    handles = [
        plt.Line2D(
            [0],
            [0],
            marker="^",
            color="w",
            label="Significant increase",
            markeredgecolor="k",
            markerfacecolor="k",
            markersize=6,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="^",
            color="w",
            label="Increase",
            markeredgecolor="k",
            markerfacecolor="none",
            markersize=6,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="v",
            color="w",
            label="Significant decrease",
            markeredgecolor="k",
            markerfacecolor="k",
            markersize=6,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="v",
            color="w",
            label="Decrease",
            markeredgecolor="k",
            markerfacecolor="none",
            markersize=6,
        ),
    ]

    if unit is not None:
        title = f"Climate tendency rate \n( ${unit}$ )"
    else:
        title = "Climate tendency rate"

    if legend_location is None:
        ax.legend(
            handles=handles,
            loc="upper left",
            fontsize="small",
            title=title,
            frameon=False,
        )

        return

    ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=legend_location,
        fontsize="small",
        title=title,
        frameon=False,
    )


def add_title(ax: plt.Axes, title: str, location=(0.025, 0.95)):
    minx, maxx = ax.get_xlim()
    miny, maxy = ax.get_ylim()
    ylen = maxy - miny
    xlen = maxx - minx
    ax.text(
        x=minx + xlen * location[0],
        y=miny + ylen * location[1],
        s=title,
        ha="left",
        va="center",
        fontsize="large",
        fontweight="bold",
    )


def add_scaler(ax: plt.Axes, length: float, location=(0.075, 0.05), linewidth=3):
    distance = length * 1000
    x0, x1, y0, y1 = ax.get_extent(target_crs)
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    bar_xs = [sbx - distance / 2, sbx + distance / 2]
    ax.plot(bar_xs, [sby, sby], transform=target_crs, color="k", linewidth=linewidth)
    ax.text(
        sbx,
        sby + 0.02 * (y1 - y0),
        str(length) + " km",
        transform=target_crs,
        horizontalalignment="center",
        verticalalignment="bottom",
    )


def add_number(ax: plt.Axes, string: str, location=(0.9, 0.9)):
    minx, maxx = ax.get_xlim()
    miny, maxy = ax.get_ylim()
    ylen = maxy - miny
    xlen = maxx - minx

    ax.text(
        x=minx + xlen * location[0],
        y=miny + ylen * location[1],
        s=string,
        fontsize="xx-large",
    )


def draw_north_arrow(
    ax, labelsize=12, location=(0.9, 0.1), width=0.05, height=0.1, pad=0.02
):
    loc_x, loc_y = location
    minx, maxx = ax.get_xlim()
    miny, maxy = ax.get_ylim()
    ylen = maxy - miny
    xlen = maxx - minx

    left = [minx + xlen * (loc_x - width * 0.5), miny + ylen * (loc_y - pad)]
    right = [minx + xlen * (loc_x + width * 0.5), miny + ylen * (loc_y - pad)]
    top = [minx + xlen * loc_x, miny + ylen * (loc_y - pad + height)]
    center = [minx + xlen * loc_x, left[1] + (top[1] - left[1]) * 0.4]
    triangle = mpatches.Polygon([left, top, right, center], color="k")
    ax.text(
        s="N",
        x=minx + xlen * loc_x,
        y=miny + ylen * (loc_y - pad + height),
        fontsize=labelsize,
        horizontalalignment="center",
        verticalalignment="bottom",
    )
    ax.add_patch(triangle)


def draw_line(ax: plt.Axes):
    line_file = "static/line/line1.shp"

    gdf = gpd.read_file(line_file)
    gdf["geometry"] = gdf["geometry"].to_crs("epsg:4326")
    shape_feature = ShapelyFeature(
        gdf.geometry,
        ccrs.PlateCarree(),
        linewidth=2,
        alpha=0.7,
        edgecolor="black",
        facecolor="none",
    )

    ax.add_feature(shape_feature)

def calculate_slope(df: pd.DataFrame, method="yue_wang_mk"):
    def process_slope_by_yue_wang_mk(county_df: pd.DataFrame):
        import pymannkendall as mk
        result = pd.Series()
        for c in county_df.columns:
            if c == "year" or c == "name":
                continue
            mk_result = mk.yue_wang_modification_test(county_df[c])
            result[c] = round(mk_result.slope * 10, 2)
            result[c + "_up"] = mk_result.h
            result[c + "_sign"] = mk_result.p < 0.05
        return 
    
    def process_slope_by_linregress(county_df: pd.DataFrame):
        result = pd.Series()
        for c in county_df.columns:
            if c == "year":
                continue
            line = linregress(county_df["year"], county_df[c])

            result[c] = round(line.slope * 10, 2)
            result[c + "_up"] = line.slope > 0
            result[c + "_sign"] = line.pvalue < 0.05
        return result

    if method == "yue_wang_mk":
        process_slope = process_slope_by_yue_wang_mk
    elif method == "linregress":
        process_slope = process_slope_by_linregress
    else:
        raise ValueError("method not support")
    
    slope_result = df.groupby("name").apply(process_slope)
    return slope_result

def map_plot(indictor_list: list, col = 3):
    point_df = pd.read_csv(get_outlier_result_data_path("all"))
    slope = calculate_slope(point_df)
    slope = add_region_latlon(slope)

    csv_path = get_origin_result_data_path("all_mean")
    df = pd.read_csv(csv_path)
    fig = plt.figure(figsize=(24, 48))
    i = 0
    row = len(indictor_list) // col + (1 if len(indictor_list) % col != 0 else 0)
    for indictor in indictor_list:
        module = import_indictor(indictor)
        ax = fig.add_subplot(row, col, i + 1, projection=target_crs)
        module.draw(df, ax)

        if hasattr(module, "unit"):
            add_point_map(
                slope,
                indictor,
                ax,
                unit=module.unit + "\cdot 10a^{-1}",
                legend_location=(0, 0.625),
            )
        else:
            add_point_map(slope, indictor, ax, legend_location=(0, 0.7))
        add_number(ax, f"({chr(97 + i)})")
        i += 1

    plt.savefig(f"result_data/map_{mode}.png", dpi=300)


def drop_unuseful_columns(df: pd.DataFrame):
    if "time" in df.columns:
        df = df.drop(columns=["time"])

    if "lat" in df.columns:
        df = df.drop(columns=["lat"])

    if "lon" in df.columns:
        df = df.drop(columns=["lon"])

    if "name" in df.columns:
        df = df.drop(columns=["name"])

    return df


mode_color_map = {
    "era5": "blue",
    "ssp126": "green",
    "ssp245": "orange",
    "ssp370": "red",
    "ssp585": "purple",
}


def line_plot(indictor_list: list, delta_change=True, post_process=False):
    fig = plt.figure(figsize=(24, 24))
    ax_dict = {}
    for indictor in indictor_list:
        ax_dict[indictor] = fig.add_subplot(4, 3, indictor_list.index(indictor) + 1)
        add_title(ax_dict[indictor], indictor)
        add_number(ax_dict[indictor], f"({chr(97 + indictor_list.index(indictor))})")


    for local_mode in mode_list:
        if local_mode != "era5" and delta_change:
            df = pd.read_csv(
                get_delta_change_result_data_path_by_mode("all", local_mode=local_mode),
                index_col=["year"],
            )
        elif post_process:
            df = pd.read_csv(
                get_outlier_result_data_path_by_mode("all", local_mode=local_mode),
                index_col=["year"],
            )
        else:
            df = pd.read_csv(
                get_origin_result_data_path_by_mode("all", local_mode=local_mode),
                index_col=["year"],
            )
            
            df = clip_df_data(df)
            
        mean_df = df.drop(columns="name").groupby("year").mean()
        
        for indictor in indictor_list:
            mean_df[indictor].plot(
                x="year",
                y=indictor,
                ax=ax_dict[indictor],
                color=mode_color_map[local_mode],
                label=local_mode,
            )
            mean_df[indictor].to_csv(f"result_data/mean/{indictor}_{local_mode}.csv", index=False)
        mean_df.to_csv(f"result_data/mean/all_{local_mode}.csv", index=True, float_format="%.2f")
  
    for indictor in indictor_list:
        add_title(ax_dict[indictor], indictor)
        add_number(ax_dict[indictor], f"({chr(97 + indictor_list.index(indictor))})")
    plt.savefig(f"result_data/line_{mode}.png", dpi=300)


def get_common_levels(era5_data: xr.DataArray, cmip6_data: xr.DataArray):
    global_min = min(era5_data.min().values, cmip6_data.min().values)
    global_max = max(era5_data.max().values, cmip6_data.max().values)
    levels = np.linspace(global_min, global_max, 20)
    return levels


def trim_bound_data(data: xr.Dataset) -> xr.Dataset:
    gdf = gpd.read_file(province_border_geojson)
    (minx, miny, maxx, maxy) = get_bounds(gdf, margin=0.25)

    return data.sel(lon=slice(minx, maxx), lat=slice(maxy, miny))


def draw_compare_map(indictor_list: list, time: str):
    fig = plt.figure(figsize=(20, 6 * len(indictor_list)))
    year = time.split("-")[0]
    for i, indictor in enumerate(indictor_list):
        era5_ds = load_daily_data(indictor, year, "era5")
        cmip6_ds = load_daily_data(indictor, year, "ssp126")

        era5_data = trim_bound_data(era5_ds).sel(time=time)[indictor]
        cmip6_data = trim_bound_data(cmip6_ds).sel(time=time)[indictor]

        levels = get_common_levels(era5_data, cmip6_data)

        era5_ax = fig.add_subplot(
            len(indictor_list), 2, 2 * i + 1, projection=target_crs
        )
        cmip6_ax = fig.add_subplot(
            len(indictor_list), 2, 2 * i + 2, projection=target_crs
        )

        draw_border(era5_ax)
        draw_border(cmip6_ax)
        era5_contour = era5_ax.contourf(
            era5_data["lon"],
            era5_data["lat"],
            era5_data,
            levels=levels,
            cmap="coolwarm",
        )
        cmip6_contour = cmip6_ax.contourf(
            cmip6_data["lon"],
            cmip6_data["lat"],
            cmip6_data,
            levels=levels,
            cmap="coolwarm",
        )
        era5_ax.set_title(f"ERA5 {indictor} {time}")
        cmip6_ax.set_title(f"CMIP6 {indictor} {time}")

        plt.colorbar(cmip6_contour, ax=cmip6_ax, pad=0.05, fraction=0.03)
        plt.colorbar(era5_contour, ax=era5_ax, pad=0.05, fraction=0.03)

    plt.savefig(f"result_data/compare_{time}.png", dpi=300)
