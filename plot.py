import matplotlib.patches as mpatches
from matplotlib import pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import numpy as np
import pandas as pd
import geopandas as gpd
from matplotlib.path import Path
from utils import get_gdf_list, find_region_by_name
from config import country_list, target_crs, gdf_crs
from cartopy.mpl.patch import geos_to_path

province_full_geojson = "static/xinjiang_full.json"
province_border_geojson = "static/xinjiang.json"


def draw_border(ax, gdf=None):
    if gdf is None:
        gdf = gpd.read_file(province_border_geojson)
    provinces = cfeat.ShapelyFeature(
        gdf.geometry, gdf_crs, edgecolor="k", alpha=0.7, facecolor="none"
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


def draw_latlon_map(
    df: pd.DataFrame, variable: str, clip=True, cmap="coolwarm", ax=None
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

    contour = ax.contourf(LON, LAT, VALUE, levels=15, cmap=cmap, transform=gdf_crs)

    if clip:
        geom = ax.projection.project_geometry(gdf.geometry.unary_union, gdf_crs)
        path = Path.make_compound_path(*geos_to_path(geom))
        for col in ax.collections:
            col.set_clip_path(path, ax.transData)

    add_scaler(ax, length=200)

    plt.colorbar(contour, ax=ax, pad=0.05, fraction=0.03)


def add_point_map(df: pd.DataFrame, variable: str, ax: plt.Axes = None, unit=None, legend_location=None):
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
