###  Script to convert the Precision point cloud from MS_Prec_Estim.py into a Raster.

import pdal
import json
from datetime import datetime
import numpy as np
import math
import rasterio
import tempfile
import os


def precision_map(prec_point_cloud, out_raster, resolution, prec_dimension):
    startTime = datetime.now()

    ppc_process = ppc(prec_point_cloud, out_raster, resolution, prec_dimension)
    ppc_process.readPC_xyerr()
    ppc_process.Run()

    print("Total Time: " + str(datetime.now() - startTime))  # get the time
    return ppc_process


class ppc:

    def __init__(self, prec_pc, ras_path, ras_res, prec_dim):
        self.ppc = prec_pc
        self.res = ras_res
        self.path = ras_path
        self.pr_dim = prec_dim
        self.min_res = None
        self.pcdata = None
        self.max_prec = None

    def readPC_xyerr(self):
        pcdata = np.loadtxt(self.ppc, delimiter=' ', skiprows=1,
                             dtype={'names': ('x', 'y', 'z', 'xerr', 'yerr', 'zerr'),
                                    'formats': ('f8', 'f8', 'f8', 'f8', 'f8', 'f8')})

        min_val = max([np.mean(pcdata['xerr']) + np.std(pcdata['xerr']),
                        np.mean(pcdata['yerr'])+ np.std(pcdata['yerr'])])

        self.min_res = math.ceil(min_val * 10000) / 10000

        self.max_prec = math.ceil(np.max(pcdata['zerr']) * 10000) / 10000


    def Run(self):
        print(self.ppc)

        self.things = 'a whole new thing'

        print("starting pipeline")

        if self.res < self.min_res:
            self.res = self.min_res

        tmp = tempfile.NamedTemporaryFile(suffix=".tif").name

        dtm_gen = {
            "pipeline": [
                {
                    "type": "readers.text",
                    "filename":  self.ppc
                },

                {
                    "type":"writers.gdal",
                    "filename": tmp,  # output file name
                    "resolution": self.res,
                    "dimension": self.pr_dim,  # raster resolution
                    "nodata": -999,
                    "output_type": "all",  # creates a multiband raster with: min, max, mean, idw, count, stdev
                    # "output_type": "stdev",  # use this if you just want a single band output for e.g. stdev
                    "window_size": 0  # changes the search area around an empty cell - second stage of algorithm

                },                       # may want this value to be a bit smaller than at present...

            ]
        }

        pipeline = pdal.Pipeline(json.dumps(dtm_gen)) # define the pdal pipeline
        pipeline.validate()  # validate the pipeline
        pipeline.execute()   #  run the pipeline

        with rasterio.open(tmp) as src:
            array = src.read(1)

        array[array == -999] = self.max_prec

        print(self.max_prec)

        with rasterio.open(self.path, "r+") as dataset:
            dataset.write_mask(True)
            dataset.write(array, 1)

        try:
            os.remove(tmp)
        except OSError as e:
            print(e)
            pass

