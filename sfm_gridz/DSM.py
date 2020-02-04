###  Script to convert the Precision point cloud from MS_Prec_Estim.py into a Raster.

import pdal
import rasterio
import json
from datetime import datetime
from sfm_gridz.mask_AOI import mask_it
# import sfm_gridz.create_temp_aoi as create_temp



def height_map(point_cloud, out_raster, resolution, window_size, epsg, bounds, mask):

    startTime = datetime.now()

    dsm_process = Dsm(point_cloud, out_raster, resolution, window_size, epsg, bounds, mask)
    # dsm_process.readPC_xyerr()
    dsm_process.get_reader()
    dsm_process.Run()

    print("Total Time: " + str(datetime.now() - startTime))  # get the time
    return dsm_process


class Dsm:

    def __init__(self, real_pc, ras_path, ras_res, window, epsg, bbox, maskit):
        self.rpc = real_pc
        self.res = ras_res
        self.path = ras_path
        self.wind = window
        self.bounds = bbox
        self.mask = maskit
        if epsg is None:
            self.epsg_code = []
        else:
            self.epsg_code = "EPSG:{0}".format(epsg)

        self.statval = 'mean'  # we could add the string to the pdal pipline but in case we decide to later add other
                               # stats it will be more strightforward.
        self.reader = None

    def get_reader(self):

        if self.rpc[-4:] == '.las' or self.rpc[-4:] == '.laz':
            self.reader = 'readers.las'
        elif self.rpc[-4:] == '.txt':
            self.reader = 'readers.text'
        else:
            raise InputError("the Point cloud format provided is not supported "
                             "provide file with extension: .las, .laz, .txt")

    def Run(self):

        # if self.mask is None:
        #     mask_section = {}
        #     range_filter = {}
        # else:
        #     aoi = create_temp.temp_gpkg(self.mask, self.epsg_code)
        #     mask_section = {
        #         "column": "key",
        #         "datasource": aoi,
        #         "dimension": "Classification",
        #         "type": "filters.overlay"}
        #     range_filter = {
        #         "limits": "Classification[8:8]",
        #         "type": "filters.range"}

        if self.bounds is None:
            writers_section = {
                "type": "writers.gdal",
                "filename": self.path,  # output file name
                "resolution": self.res,
                "dimension": 'Z',  # raster resolution
                "nodata": -999,
                "output_type": "{0}, stdev".format(self.statval),
                "window_size": self.wind}

        else:
            writers_section = {
                "type": "writers.gdal",
                "filename": self.path,  # output file name
                "resolution": self.res,
                "dimension": 'Z',  # raster resolution
                "nodata": -999,
                "bounds": str(self.bounds),
                "output_type": "{0}, stdev".format(self.statval),
                "window_size": self.wind},


        print("Generating DSM raster...")

        dtm_gen = {
            "pipeline": [
                {
                    "type": self.reader,
                    "filename":  self.rpc,
                    "override_srs": self.epsg_code
                },
                # mask_section,
                # range_filter,
                writers_section,

            ]
        }

        pipeline = pdal.Pipeline(json.dumps(dtm_gen)) # define the pdal pipeline
        pipeline.validate()  # validate the pipeline
        pipeline.execute()   #  run the pipeline

        metadata = pipeline.metadata
        print(metadata)

        if self.mask is not None:
            mask_it(raster=self.path, shp_path=self.mask, epsg=self.epsg_code)

        if self.bounds is None:
            with rasterio.open(self.path) as src:
                self.bounds = ([src.bounds[0], src.bounds[2]], [src.bounds[1], src.bounds[3]])

        # from sfm_gridz.create_temp_aoi import temp_gpkg



class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
