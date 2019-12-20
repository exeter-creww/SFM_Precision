import rasterio
from rasterio.mask import mask
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
    dem_od_process.set_bounds()
    dem_od_process.run_raster_calcs()
    dem_od_process.remove_temps()


class deom_od:
    def __init__(self, rast1, rast2, epsg_c, prec_ras1, prec_ras2):
        self.ras1_p = rast1
        self.ras2_p = rast2
        self.pras1_p = prec_ras1
        self.pras1_p = prec_ras2
        self.epsg = epsg_c
        self.ras1 = None
        self.ras2 = None
        self.pras1 = None
        self.pras1 = None

    def load_rasters(self):
        self.ras1 = rasterio.open(self.ras1_p)
        self.ras2 = rasterio.open(self.ras2_p)
        self.pras1 = rasterio.open(self.ras1_p)
        self.pras2 = rasterio.open(self.ras2_p)

    def set_bounds(self):
        areas = []
        for i in [self.ras1, self.ras2, self.pras1, self.pras2]:
            x_len = i.bounds[2] - i.bounds[0]
            y_len = i.bounds[3] - i.bounds[1]
            area = x_len*y_len
            areas.append(area)

        if areas.index(min(areas)) == 0:
            b_ras = self.ras1
        elif areas.index(min(areas)) == 1:
            b_ras = self.ras2
        elif areas.index(min(areas)) == 2:
            b_ras = self.pras1
        else:
            b_ras = self.pras2

        def getFeatures(gdf):
            """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
            return [json.loads(gdf.to_json())['features'][0]['geometry']]
        
        bbox = box(b_ras.bounds[0], b_ras.bounds[1], b_ras.bounds[2], b_ras.bounds[3])
        geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0])
        coords = getFeatures(geo)

        Clipped_ras_list = []
        for i in [self.ras1, self.ras2, self.pras1, self.pras2]:
            mosaic, out_trans = mask(dataset=i, shapes=coords, crop=True, nodata=(-999), all_touched=False)
            out_meta = i.meta.copy()
            out_meta.update(
                {"driver": "GTiff", "height": mosaic.shape[1], "width": mosaic.shape[2], "transform": out_trans,
                 "crs": self.epsg, "compress": "lzw", "nodata": -999})
            temp_ras = tempfile.NamedTemporaryFile(suffix=".tif").name

            with rasterio.open(temp_ras, "w", **out_meta) as dest:
                dest.write(mosaic)

            # clip_ras = rasterio.open(temp_ras)
            Clipped_ras_list.append(temp_ras)

        self.ras1, self.ras2, self.pras1, self.pras2 = [rasterio.open(i) for i in Clipped_ras_list]
        # a = rasterio.open(Clipped_ras_list[0])

        # from rasterio.plot import show
        # show(self.ras1, cmap='magma')
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






