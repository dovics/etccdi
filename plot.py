import matplotlib.patches as mpatches
from matplotlib import pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib.ticker as mticker
from cartopy.io.shapereader import Reader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from utils import get_gdf_list, find_region_by_name
from config import country_list
from cartopy.mpl.patch import geos_to_path

province_full_geojson = "static/xinjiang_full.json"
province_border_geojson = "static/xinjiang.json"

def draw_border(ax, gdf = None):
    if gdf is None:
        gdf = gpd.read_file(province_border_geojson)
    provinces = cfeat.ShapelyFeature(
        gdf.geometry, ccrs.PlateCarree(), edgecolor="k", alpha=0.7, facecolor="none"
    )
    ax.add_feature(provinces, linewidth=1)

def new_plot(show_border=True, show_grid=True, show_country=False, subregions=None):
    proj = ccrs.PlateCarree()
    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.subplots(1, 1, subplot_kw={"projection": proj})

    gdf = gpd.read_file(province_border_geojson)
    (minx, miny, maxx, maxy) = get_bounds(gdf, margin=1)
    ax.set_extent([minx, maxx, miny, maxy], crs=proj)
    if not show_country and show_border:
        draw_border(ax, gdf=gdf)

    if show_country:
        region_list = []
        for gdf in get_gdf_list():
            for _, region in gdf.iterrows():
                region_list.append(
                    gpd.GeoDataFrame([region], geometry=[region.geometry], crs=gdf.crs)
                )
        merged_gdf = gpd.pd.concat(region_list)
        provinces = cfeat.ShapelyFeature(
            merged_gdf.geometry, proj, edgecolor="k", alpha=0.7, facecolor="none"
        )
        ax.add_feature(provinces, linewidth=1)

    if show_grid:
        gl = ax.gridlines(
            crs=proj,
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
                region.geometry, proj, edgecolor="red", alpha=0.7, facecolor="none"
            )
            ax.add_feature(regionFeature, linewidth=1)

    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlocator = mticker.FixedLocator(np.arange(minx, maxx + 10, 10))
    gl.ylocator = mticker.FixedLocator(np.arange(miny, maxy + 10, 10))

    return fig, ax

def draw_north(ax, labelsize=8, loc_x=75, loc_y=50, width=1.2, height=1.8, pad=4):
    minx, maxx = ax.get_xlim()
    miny, maxy = ax.get_ylim()
    ylen = maxy - miny
    xlen = maxx - minx
    left = [minx + xlen*(loc_x - width*.5), miny + ylen*(loc_y - pad)]
    right = [minx + xlen*(loc_x + width*.5), miny + ylen*(loc_y - pad)]
    top = [minx + xlen*loc_x, miny + ylen*(loc_y - pad + height)]
    center = [minx + xlen*loc_x, left[1] + (top[1] - left[1])*.4]
    triangle = mpatches.Polygon([left, top, right, center], color='k')
    ax.text(s='N',
            x=minx + xlen*loc_x,
            y=miny + ylen*(loc_y - pad + height),
            fontsize=labelsize,
            horizontalalignment='center',
            verticalalignment='bottom')
    ax.add_patch(triangle)
    

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
                gpd.GeoDataFrame([region], geometry=[region.geometry], crs=gdf.crs)
            )
    merged_gdf = gpd.pd.concat(region_list)
    if fill:
        merged_gdf.plot(
            column="value", edgecolor="black", linewidth=1, cmap="coolwarm", legend=True
        )
    else:
        merged_gdf.boundary.plot(edgecolor="black", linewidth=1)

def draw_latlon_map(df: pd.DataFrame, variable: str, clip=True, cmap="coolwarm", ax = None):
    gdf = gpd.read_file(province_border_geojson)
    (minx, miny, maxx, maxy) = get_bounds(gdf, margin=1)
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
    else:
        draw_border(ax)
        draw_north(ax)
        
    contour = ax.contourf(
        LON, LAT, VALUE, levels=15, cmap=cmap, transform=ccrs.PlateCarree()
    )
    
    if clip:
        geom = ax.projection.project_geometry(gdf.geometry.unary_union, ccrs.PlateCarree())
        path = Path.make_compound_path(*geos_to_path(geom))
        for col in ax.collections:
            col.set_clip_path(path, ax.transData)
            
    plt.colorbar(contour, label=variable, ax=ax, pad=0.05, fraction=0.03)
    
def draw_point_map(df: pd.DataFrame, variable: str, ax: plt.Axes = None):
    symbols = {
        (True, False): "△",
        (True, True): "▲",
        (False, False): "▽",
        (False, True): "▼"
    }
    
    for (up, sign), symbol in symbols.items():
        subset = df[(df[variable + "_up"] == up) & (df[variable + "_sign"] == sign)]
        for _, row in subset.iterrows():
            ax.annotate(symbol, xy=(row["lon"], row["lat"]), transform=ccrs.PlateCarree(), fontsize='xx-small')

    handles = [
        plt.Line2D([0], [0], marker='^', color='w', label='Sig. increase', markeredgecolor='k', markerfacecolor='k', markersize=6),
        plt.Line2D([0], [0], marker='^', color='w', label='increase', markeredgecolor='k', markerfacecolor='none', markersize=6),
        plt.Line2D([0], [0], marker='v', color='w', label='Sig. decrease', markeredgecolor='k', markerfacecolor='k', markersize=6),
        plt.Line2D([0], [0], marker='v', color='w', label='decrease', markeredgecolor='k', markerfacecolor='none', markersize=6)
    ]

    ax.legend(handles=handles, loc='upper left', fontsize='xx-small')