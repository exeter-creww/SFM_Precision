# create vector grid to the extent of the DSM - 30-40m?
# delete any grid cells that don't intersect woodland vector.
# Use this modified grid as

import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import os
from matplotlib import pyplot as plt
import pandas as pd

zones_out = os.path.relpath('int_files/Woodland_Zones20m.gpkg')
grid_out = os.path.relpath('int_files/grid_20m.gpkg')
trees_vec = os.path.relpath('Rip_Area_vec/Rip_Vec_Sep17.gpkg')

def main():
    trees_gdf = gpd.read_file(trees_vec)

    xmin,ymin,xmax,ymax = trees_gdf.total_bounds

    length = 20
    wide = 20

    cols = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), wide))
    rows = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), length))
    rows.reverse()

    polygons = []
    for x in cols:
        for y in rows:
            polygons.append( Polygon([(x,y), (x+wide, y), (x+wide, y-length), (x, y-length)]) )

    grid = gpd.GeoDataFrame({'geometry':polygons})
    grid.crs = trees_gdf.crs
    grid.to_file(grid_out, driver='GPKG')

    zones = gpd.overlay(trees_gdf, grid,  how='intersection')

    intersect_grid = get_union(grid, trees_gdf)


    gdf_list = []
    for idx, row in intersect_grid.iterrows():

        z_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(row['geometry']))

        inter_objs = gpd.overlay(zones, z_gdf, how='intersection')
        inter_objs['val'] = 1
        inter_objs = inter_objs.dissolve(by='val')
        inter_objs = inter_objs.reset_index()
        inter_objs = inter_objs.drop(columns=['val'])
        # inter_objs.plot(edgecolor='black')
        # plt.show()
        # print(len(inter_objs))

        gdf_list.append(inter_objs)

        # print("BREAK")

    dissolved_zones = pd.concat(gdf_list)

    dissolved_zones.crs = trees_gdf.crs
    print(dissolved_zones.crs)
    dissolved_zones.plot(edgecolor='black')
    plt.show()
    dissolved_zones.to_file(zones_out, driver='GPKG')

def get_union(to_select, union_shp):
    """Alternative union function"""
    union = gpd.GeoDataFrame(
        gpd.GeoSeries([union_shp.unary_union]),
        columns=['geometry'],
        crs=union_shp.crs)

    clip_gdf = gpd.sjoin(to_select, union, op='intersects')
    clip_gdf = clip_gdf.drop(columns=['index_right'])

    return clip_gdf
if __name__ == '__main__':
    main()