###  Script to convert the Precision point cloud from MS_Prec_Estim.py into a Raster.

import pdal
import rasterio
from rasterio.plot import show
import json
from datetime import datetime
import numpy as np
import math
import tempfile
import os
from matplotlib import pyplot as plt

def precision_map(prec_point_cloud, resolution):
    startTime = datetime.now()

    ppc_process = ppc(prec_point_cloud, resolution)
    ppc_process.readPC_xyerr()
    ppc_process.Run()

    print("Total Time: " + str(datetime.now() - startTime))  # get the time
    return ppc_process

class ppc:
    def __init__(self, prec_pc, ras_res):
        self.ppc = prec_pc
        self.res = ras_res
        self.things = None
        self.min_res = None
        self.pcdata = None

    def readPC_xyerr(self):
        pcdata = np.loadtxt(self.ppc, delimiter=' ', skiprows=1,
                             dtype={'names': ('x', 'y', 'z', 'xerr', 'yerr', 'zerr'),
                                    'formats': ('f8', 'f8', 'f8', 'f8', 'f8', 'f8')})

        min_res = max([np.mean(pcdata['xerr']) + np.std(pcdata['xerr']),
                        np.mean(pcdata['yerr'])+ np.std(pcdata['yerr'])])

        self.min_res = math.ceil(min_res * 10000) / 10000

    def Run(self):
        print(self.ppc)

        self.things = 'a whole new thing'

        startTime = datetime.now()
        print("Total Time: " + str(datetime.now() - startTime))  # get the time
        print("starting pipeline")
        #
        #

        #
        # if res < 0.005:
        #     print("maimum xy error is < 1m, setting Raster resolution to 1m")
        #     res = 0.005
        # # if res < 1:
        # #     print("maimum xy error is < 1m, setting Raster resolution to 1m")
        # #     res = 1

        # with tempfile.TemporaryFile() as tmp:
        #     # Do stuff with tmp
        #     tmp.write('stuff')

        # dtm_gen = {
        #     "pipeline":[
        #         {
        #             "type": "readers.text",
        #             "filename":  pc_filename
        #         },
        #
        #         {
        #             "type":"writers.gdal",
        #             "filename": out_dem,  # output file name
        #             "resolution": res,
        #             "dimension": "zerr",  # raster resolution
        #             # "radius": res*2,  # radius in which to search for other points
        #             "output_type": "all",  # creates a multiband raster with: min, max, mean, idw, count, stdev
        #             # "output_type": "stdev",  # use this if you just want a single band output for e.g. stdev
        #             "window_size": 20 # changes the search area around an empty cell - second stage of algorithm
        #
        #         },                       # may want this value to be a bit smaller than at present...
        #
        #     ]
        # }
        #
        # pipeline = pdal.Pipeline(json.dumps(dtm_gen)) # define the pdal pipeline
        # pipeline.validate()  # validate the pipeline
        # pipeline.execute()   #  run the pipeline
        #
        #
        # dataset = rasterio.open(out_dem)
        #
        # # fig = plt.gcf()
        # # show(dataset, cmap='magma')
        # # plt.legend(loc="lower left")
        # # plt.draw()
        # # fig.savefig(fname = img_path, dpi = 300, format = 'png')
        #
        # plot_arr = zero_to_nan(dataset.read(1))
        #
        # fig, ax = plt.subplots(figsize=(8, 8))
        # img = ax.imshow(plot_arr, cmap='twilight_shifted')
        # fig.colorbar(img, ax=ax)
        # ax.set_axis_off()
        # plt.show()
        # fig.savefig(fname=img_path, dpi=300, format='png')
        #
        # # gcps = gpd.read_file(gcp_file)
        # #
        # #
        # fig, ax = plt.subplots(figsize=(10, 10))
        # rasterio.plot.show(dataset, ax=ax, cmap='twilight_shifted')
        # # gcps.plot(ax=ax, column='type', cmap='gist_gray', markersize=50, legend=True)
        # plt.show()
        # # fig.savefig(fname = img_path, dpi = 300, format = 'png')
        # # # plt.imshow(dataset.read(1), cmap='magma')




    def zero_to_nan(self, arr):
        """Replace every -999 with 'nan' and return a copy."""
        arr[arr < 0] = np.nan
        return arr

# if __name__ == "__main__":