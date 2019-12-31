# Issues: currently the rasters are not equally sized - I've managed to even up the sizes but they are not corresponding
# parts of the scene. currently, the resized raster is just the top left corner not the area in the other scene.
# perhaps warp align target on all rasters line them all up then work on them...

import rasterio
from rasterio.mask import mask
from rasterio.enums import Resampling
from rasterio import warp
from shapely.geometry import box
import geopandas as gpd
import tempfile
from rasterio.crs import CRS
import json

def dem_of_diff(raster_1, raster_2, prec_point_cloud_1, prec_point_cloud_2, **kwargs):
    print("calculating DEM of difference...")
    epsg_code = kwargs.get('epsg', None)
    if epsg_code is not None:
        epsg_code = CRS.from_epsg(epsg_code)
    dem_od_process = deom_od(raster_1, raster_2, epsg_code, prec_point_cloud_1, prec_point_cloud_2)
    dem_od_process.load_rasters()

    dem_od_process.resample_rasters()
    # dem_od_process.set_bounds()

    dem_od_process.run_raster_calcs()
    dem_od_process.remove_temps()


class deom_od:
    def __init__(self, rast1, rast2, epsg_c, prec_ras1, prec_ras2):
        self.raster_pths = [rast1, rast2, prec_ras1, prec_ras2]
        self.rasters = [None, None, None, None]
        # self.snap_ras = None

        self.epsg = epsg_c

        self.temp_log = []

    def load_rasters(self):

        self.rasters[0] = rasterio.open(self.raster_pths[0], 'r+')
        self.rasters[1] = rasterio.open(self.raster_pths[1], 'r+')
        self.rasters[2] = rasterio.open(self.raster_pths[2], 'r+')
        self.rasters[3] = rasterio.open(self.raster_pths[3], 'r+')

    def resample_rasters(self):
        # areas = []
        # for i in self.rasters:
        #     # for i in [self.ras1, self.ras2, self.pras1, self.pras2]:
        #     x_len = i.bounds[2] - i.bounds[0]
        #     y_len = i.bounds[3] - i.bounds[1]
        #     area = x_len * y_len
        #     areas.append(area)
        #
        # if areas.index(min(areas)) == 0:
        #     b_ras = self.rasters[0]
        # elif areas.index(min(areas)) == 1:
        #     b_ras = self.rasters[1]
        # elif areas.index(min(areas)) == 2:
        #     b_ras = self.rasters[2]
        # else:
        #     b_ras = self.rasters[3]
        #
        # self.snap_ras = b_ras

        print("resampling raster to equalise all arrays...")
        res_list = []
        for i in self.rasters:
            # for i in [self.ras1, self.ras2, self.pras1, self.pras2]:
            x_res = (i.bounds[2] - i.bounds[0]) / i.width
            y_res = (i.bounds[3] - i.bounds[1]) / i.height

            res_list.append((x_res, y_res))
        min_res = min(res_list)

        # res = ((self.snap_ras.bounds[2] - self.snap_ras.bounds[0]) / self.snap_ras.width,
        #        (self.snap_ras.bounds[3] - self.snap_ras.bounds[1]) / self.snap_ras.height)

        for idx, i in enumerate(self.rasters):
            # for i in [self.ras1, self.ras2, self.pras1, self.pras2]:
            x_res = (i.bounds[2] - i.bounds[0]) / i.width
            y_res = (i.bounds[3] - i.bounds[1]) / i.height

            if (x_res, y_res) != min_res:
                print("resizing rasters")

                out_meta = i.meta.copy()

                x_res_factor = x_res / min_res[0]
                y_res_factor = y_res / min_res[1]

                # resample data to target shape
                data = i.read(
                    out_shape=(
                        i.count,
                        int(i.width * x_res_factor),
                        int(i.height * y_res_factor)
                    ),
                    resampling=Resampling.bilinear)

                # scale image transform

                # trans, wid, high = warp.calculate_default_transform(self.epsg, self.epsg, self.snap_ras.width,
                #                                                     self.snap_ras.height, left=self.snap_ras.bounds[0],
                #                                                     bottom=self.snap_ras.bounds[1],
                #                                                     right=self.snap_ras.bounds[2],
                #                                                     top=self.snap_ras.bounds[3],
                #                                                     resolution=res)

                trans = i.transform * i.transform.scale(
                    (i.width / data.shape[-2]),
                    (i.height / data.shape[-1])
                )

                out_meta.update(
                    {"driver": "GTiff", "height": data.shape[2], "width": data.shape[1], "transform": trans,
                     "crs": self.epsg, "compress": "lzw", "nodata": -999})
                temp_ras = tempfile.NamedTemporaryFile(suffix=".tif").name

                with rasterio.open(temp_ras, "w", **out_meta) as dest:
                    dest.write(data)

                self.rasters[idx] = rasterio.open(temp_ras)

                self.temp_log.append(temp_ras)

        for i in self.rasters:
            # print(i.bounds)
            print(i.shape)

        # function to return the index of the smallest raster
        def rasNum(ras_list):
            size_list = []
            for i in ras_list:
                n = i.shape[0]*i.shape[1]
                size_list.append(n)
            # print(size_list)
            sras = size_list.index(min(size_list))
            return sras

        s_ras = rasNum(self.rasters)


        # if (len(set([i.shape for i in self.rasters])) <= 1) is False: # checks if dims of rasters are not equal
        # do something here to resize the arrays - looks like the lower left corner is consistant but there can be
        # overlap depending on cell size so just remove from the right and upper edges of array and reproject with the
        # smaller raster affine.

        print("pause")

    def set_bounds(self):

        def getFeatures(gdf):
            """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
            return [json.loads(gdf.to_json())['features'][0]['geometry']]

        bbox = box(self.snap_ras.bounds[0], self.snap_ras.bounds[1], self.snap_ras.bounds[2], self.snap_ras.bounds[3])
        geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0])
        coords = getFeatures(geo)

        for idx, i in enumerate(self.rasters):

            if bbox != box(i.bounds[0], i.bounds[1], i.bounds[2], i.bounds[3]):
                mosaic, out_trans = mask(dataset=i, shapes=coords, crop=True, nodata=(-999), all_touched=False)
                out_meta = i.meta.copy()
                out_meta.update(
                    {"driver": "GTiff", "height": mosaic.shape[1], "width": mosaic.shape[2], "transform": out_trans,
                     "crs": self.epsg, "compress": "lzw", "nodata": -999})
                temp_ras = tempfile.NamedTemporaryFile(suffix=".tif").name

                with rasterio.open(temp_ras, "w", **out_meta) as dest:
                    dest.write(mosaic)

                self.rasters[idx] = rasterio.open(temp_ras)

                self.temp_log.append(temp_ras)

        for i in self.rasters:
            print(i.shape)

        print("pause")


        from rasterio.plot import show
        show(self.rasters[0], cmap='magma')
        show(self.rasters[3], cmap='magma')
        # show(self.ras2, cmap='viridis')
        #
        # import numpy as np
        # from matplotlib import pyplot as plt
        # for i in range(1,7):
        #     a = self.ras1.read(i)
        #     a[a==-999] = np.nan
        #
        #     fig, ax = plt.subplots(figsize=(8, 8))
        #     img = ax.imshow(a, cmap='viridis')
        #     fig.colorbar(img, ax=ax)
        #     ax.set_axis_off()
        #     plt.show()





    def run_raster_calcs(self):

        print("run the raster calculations here...")

    def remove_temps(self):


        print('delete the temp raster files.')






