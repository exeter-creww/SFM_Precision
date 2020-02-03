import rasterio
from rasterio.mask import mask
from rasterio.plot import show
import json
import geopandas as gpd


def mask_it(raster, shp_path, epsg):

    aoi = gpd.read_file(shp_path)
    if epsg is not None:
        aoi.crs = {'init': 'epsg:{0}'.format(epsg)}
    geom = getFeatures(gdf=aoi)

    with rasterio.open(raster, 'r') as src:
        out_image, out_transform = mask(src, geom, crop=True, invert=False, nodata=-999)

        out_meta = src.meta

    out_meta.update({"transform": out_transform})

    with rasterio.open(raster, "w", **out_meta) as dest:
        dest.write(out_image)

    # with rasterio.open(raster, 'r') as src:
    #     show(src)

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


