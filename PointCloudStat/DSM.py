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

    dsm_process = dsm(point_cloud, out_raster, resolution, window_size, epsg, bounds)
    # dsm_process.readPC_xyerr()
    dsm_process.Run()

    print("Total Time: " + str(datetime.now() - startTime))  # get the time
    return dsm_process


class dsm:

    def __init__(self, prec_pc, ras_path, ras_res, window, epsg, bbox):
        self.ppc = prec_pc
        self.res = ras_res
        self.path = ras_path
        self.wind = window
        self.bounds = bbox
        if epsg is None:
            self.epsg_code = []
        else:
            self.epsg_code = "EPSG:{0}".format(epsg)

    def Run(self):

        print("starting pipeline")
        if self.bounds is not None:
            dtm_gen = {
                "pipeline": [
                    {
                        "type": "readers.las",
                        "filename":  self.ppc,
                        "override_srs": self.epsg_code
                    },

                    {
                        "type":"writers.gdal",
                        "filename": self.path,  # output file name
                        "resolution": self.res,
                        "dimension": 'Z',  # raster resolution
                        "nodata": -999,
                        "bounds": str(self.bounds),
                        "output_type": "all",  # creates a multiband raster with: min, max, mean, idw, count, stdev
                        # "output_type": "stdev",  # use this if you just want a single band output for e.g. stdev
                        "window_size": self.wind  # changes the search area around an empty cell - second stage of algorithm

                    },                       # may want this value to be a bit smaller than at present...

                ]
            }
        else:
            dtm_gen = {
                "pipeline": [
                    {
                        "type": "readers.las",
                        "filename": self.ppc,
                        "override_srs": self.epsg_code
                    },

                    {
                        "type": "writers.gdal",
                        "filename": self.path,  # output file name
                        "resolution": self.res,
                        "dimension": 'Z',  # raster resolution
                        "nodata": -999,
                        "output_type": "all",  # creates a multiband raster with: min, max, mean, idw, count, stdev
                        # "output_type": "stdev",  # use this if you just want a single band output for e.g. stdev
                        "window_size": self.wind
                        # changes the search area around an empty cell - second stage of algorithm

                    },  # may want this value to be a bit smaller than at present...

                ]
            }

        pipeline = pdal.Pipeline(json.dumps(dtm_gen)) # define the pdal pipeline
        pipeline.validate()  # validate the pipeline
        pipeline.execute()   #  run the pipeline

        if self.bounds is None:
            with rasterio.open(self.path) as src:
                self.bounds = ([src.bounds[0], src.bounds[2]], [src.bounds[1], src.bounds[3]])




