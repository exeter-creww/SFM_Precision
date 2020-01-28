###  Script to convert the Precision point cloud from MS_Prec_Estim.py into a Raster.

import pdal
import rasterio
import json
from datetime import datetime


def height_map(point_cloud, out_raster, resolution, **kwargs):
    window_size = kwargs.get('window_size', 0)
    epsg = kwargs.get('epsg', None)
    bounds = kwargs.get('bounds', None)

    startTime = datetime.now()

    dsm_process = Dsm(point_cloud, out_raster, resolution, window_size, epsg, bounds)
    # dsm_process.readPC_xyerr()
    dsm_process.get_reader()
    dsm_process.Run()

    print("Total Time: " + str(datetime.now() - startTime))  # get the time
    return dsm_process


class Dsm:

    def __init__(self, real_pc, ras_path, ras_res, window, epsg, bbox):
        self.rpc = real_pc
        self.res = ras_res
        self.path = ras_path
        self.wind = window
        self.bounds = bbox
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

        print("starting pipeline")
        if self.bounds is not None:
            dtm_gen = {
                "pipeline": [
                    {
                        "type": self.reader,
                        "filename":  self.rpc,
                        "override_srs": self.epsg_code
                    },

                    {
                        "type": "writers.gdal",
                        "filename": self.path,  # output file name
                        "resolution": self.res,
                        "dimension": 'Z',  # raster resolution
                        "nodata": -999,
                        "bounds": str(self.bounds),
                        "output_type": "{0}, stdev".format(self.statval),
                        "window_size": self.wind  # changes search area around an empty cell - second stage of algorithm
                    },

                ]
            }
        else:
            dtm_gen = {
                "pipeline": [
                    {
                        "type": self.reader,
                        "filename": self.rpc,
                        "override_srs": self.epsg_code
                    },

                    {
                        "type": "writers.gdal",
                        "filename": self.path,  # output file name
                        "resolution": self.res,
                        "dimension": 'Z',  # raster resolution
                        "nodata": -999,
                        "output_type": "{0}, stdev".format(self.statval),
                        "window_size": self.wind

                    },

                ]
            }

        pipeline = pdal.Pipeline(json.dumps(dtm_gen)) # define the pdal pipeline
        pipeline.validate()  # validate the pipeline
        pipeline.execute()   #  run the pipeline

        if self.bounds is None:
            with rasterio.open(self.path) as src:
                self.bounds = ([src.bounds[0], src.bounds[2]], [src.bounds[1], src.bounds[3]])


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
