import rasterio
from rasterio.mask import mask
import json
import geopandas as gpd
import warnings
# from rasterio.features import geometry_mask

def mask_it(raster, shp_path, epsg):

    aoi = gpd.read_file(shp_path)

    if epsg is None:
        warnings.warn("No CRS set for mask - if alignment issues occur set a CRS to the feature")
    elif aoi.crs != epsg:
        aoi = aoi.to_crs(epsg)

    geom = getFeatures(gdf=aoi)

    with rasterio.open(raster, 'r') as src:
        out_image, out_transform = mask(src, geom, crop=True, invert=False, nodata=-999, all_touched=True, pad=True)

        out_meta = src.meta

    out_meta.update({"height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    with rasterio.open(raster, "w", **out_meta) as dest:
        dest.write(out_image)

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


