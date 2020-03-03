# Import Raw Lidar layers - merge and clip to extent. resample and align with Sep17 DSM.
# Create Canopy height model from DSM and DTM.
# Identify canopy >2m and classify
# create polygon of woodland area.

import rasterio
from rasterio.plot import show
from rasterio.mask import mask
import geopandas as gpd
from rasterio.enums import Resampling
from shapely.geometry import box
import os
import numpy as np
import json
import warnings


def canopy_height(dsm_path, dtm_path, chm_out):
    print("Calculating Canopy Height Model...")

    chm_process = CanopyHeightModel(dsm_path, dtm_path, chm_out)
    chm_process.get_chm()

    return chm_process


class CanopyHeightModel:
    def __init__(self, dsm_pth, dtm_pth, chm_out_pth):
        self.dsm_path = dsm_pth
        self.dtm_path = dtm_pth
        self.path = chm_out_pth
        self.epsg = None


    def get_chm(self):

        def reshape_arr(b_arr, difference):
            if difference[0] > 0:
                b_arr = np.delete(b_arr, (range(0, difference[0])), axis=0)
            else:
                ins_list = []
                for i in range(0, abs(difference[0])):
                    ins_list.append(0)
                b_arr = np.insert(b_arr, ins_list, -999, axis=0)
            if difference[1] > 0:
                b_arr = np.delete(b_arr, (range(b_arr.shape[-1] - (difference[1]), b_arr.shape[-1])),
                                  axis=1)
            else:
                ind = b_arr.shape[1]
                ins_list = []
                for i in range(0, abs(difference[1])):
                    ins_list.append(ind)
                b_arr = np.insert(b_arr, ins_list, -999, axis=1)

            return b_arr

        def getFeatures(gdf):
            """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
            return [json.loads(gdf.to_json())['features'][0]['geometry']]

        with rasterio.open(self.dsm_path) as src:
            dsm_arr = src.read(1)
            roughness = src.read(2)
            bounds = src.bounds
            bbox = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
            geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=src.crs.data)
            coords = getFeatures(geo)
            dsm_meta = src.meta
            loc_crs = src.crs
            no_dat_val = src.nodata
            target_xres, target_yres = src.transform[0], abs(src.transform[4])

        with rasterio.open(self.dtm_path, 'r+') as dataset:
            if dataset.crs is None:
                warnings.warn("DTM CRS is not set - continuing assuming it matches the DSM")
                dataset.crs = loc_crs
            elif dataset.crs != loc_crs:
                raise CrsError("DTM CRS and DSM CRS do not match - reproject DTM before running chm module.")

            xscale = dataset.transform[0]/target_xres
            yscale = abs(dataset.transform[4])/target_yres

            data = dataset.read(
                out_shape=(
                    dataset.count,
                    int(dataset.width * xscale),
                    int(dataset.height * yscale)
                ),
                resampling=Resampling.bilinear
            )
            data = data.reshape((data.shape[-2], data.shape[-1]))

            transform = dataset.transform * dataset.transform.scale(
                (dataset.width / data.shape[-2]),
                (dataset.height / data.shape[-1])
            )

            save_meta = dataset.meta

        save_meta.update(transform=transform, count=1, height=data.shape[-1], width=data.shape[-2], nodata=no_dat_val)

        with rasterio.open(self.path, 'w+', **save_meta) as chm:
            chm.write(data, 1)

            out_img, out_transform = mask(chm, shapes=coords, crop=True)
            out_img = out_img.reshape((out_img.shape[-2], out_img.shape[-1]))

            if out_img.shape != dsm_arr.shape:

                diff = tuple(x - y for x, y in zip(out_img.shape,  dsm_arr.shape))

                out_img = reshape_arr(out_img, diff)

            out_img[dsm_arr == no_dat_val] = -999

        save_meta.update(transform=out_transform, count=3, height=out_img.shape[-2], width=out_img.shape[-1])

        with rasterio.open(self.path, 'w+', **save_meta) as chm:
            chm.write(out_img, 3)
            chm.write(roughness.astype('float32'), 2)
            chm_arr = out_img.copy()
            chm_arr[chm_arr != -999] = dsm_arr[out_img != -999] - out_img[out_img != -999]
            chm.write(chm_arr, 1)

            # show(chm.read(1, masked=True), cmap='viridis', transform=dataset.transform)
            # show(chm.read(2, masked=True), cmap='magma', transform=dataset.transform)
            # show(chm.read(3, masked=True), cmap='terrain', transform=dataset.transform)

            self.epsg = chm.crs.data

        print("DONE")





class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class CrsError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """
# if __name__ == '__main__':
#     home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v3")
#     dsm_path = os.path.join(home, "dsm1.tif")
#     chm_out = os.path.join(home, "chm1.tif")
#     dtm_path = os.path.abspath('C:/HG_Projects/CWC_Drone_work/DTM/Lidar_mosaic/CWC_Lidar_DTM.tif')
#
#     canopy_height(dsm_path, dtm_path, chm_out)

