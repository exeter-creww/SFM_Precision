###  Script to convert the Precision point cloud from MS_Prec_Estim.py into a Raster.

import pdal
import rasterio
from rasterio.plot import show
import json
from datetime import datetime
from plyfile import PlyData, PlyElement
import numpy as np
import math
import os
from matplotlib import pyplot as plt

startTime = datetime.now()

def readPLY_xyerr(ply):
    plydata = PlyData.read(ply)
    max_xerr = max(plydata.elements[0].data['xerr'])
    max_yerr = max(plydata.elements[0].data['yerr'])
    max_zerr = max(plydata.elements[0].data['zerr'])

    max_err = math.ceil(max([np.max(plydata.elements[0].data['xerr']), np.max(plydata.elements[0].data['yerr'])])*10000)/10000
    mean_err = max([np.mean(plydata.elements[0].data['xerr']), np.mean(plydata.elements[0].data['yerr'])])
    std_err = max([np.std(plydata.elements[0].data['xerr']), np.std(plydata.elements[0].data['yerr'])])
    mean_add_std = math.ceil((mean_err + std_err)*10000)/10000

    print(max_err)
    print(mean_add_std)

    return mean_add_std
# import pandas as pd # Pandas section is currently commented out.



home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1/Rasters") # provide project directory
# export_loc = home + "/exports"   # export folder (needs to be created before script run)

pc_filename = "C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1/MonteCarlo_Export/MonteCarloResult_v6.ply" # point cloud file
# pc_filename = "C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1/MonteCarlo_Export/MonteCarloResult_v5.ply"

out_dem = os.path.join(home, "Prec_test_CWC_V2.tif") #  name of output

img_path = os.path.join(home, "Height_CWC_V2.png")

print("starting pipeline")


res = readPLY_xyerr(pc_filename)

if res < 1:
    print("maimum xy error is < 1m, setting Raster resolution to 1m")
    res = 1


dtm_gen = {
    "pipeline":[
        {
            "type": "readers.ply",
            "filename":  pc_filename
        },

        {
            "type":"writers.gdal",
            "filename": out_dem,  # output file name
            "resolution": res,
            "dimension": "z",  # raster resolution
            # "radius": res,  # radius in which to search for other points
            "output_type": "all",  # creates a multiband raster with: min, max, mean, idw, count, stdev
            # "output_type": "stdev",  # use this if you just want a single band output for e.g. stdev
            "window_size": 20 # changes the search area around an empty cell - second stage of algorithm
        },                       # may want this value to be a bit smaller than at present...

    ]
}

pipeline = pdal.Pipeline(json.dumps(dtm_gen)) # define the pdal pipeline
pipeline.validate()  # validate the pipeline
pipeline.execute()   #  run the pipeline


dataset = rasterio.open(out_dem)



# fig = plt.gcf()
# show(dataset, cmap='magma')
# plt.legend(loc="lower left")
# plt.draw()
# fig.savefig(fname = img_path, dpi = 300, format = 'png')

def zero_to_nan(arr):
    """Replace every -999 with 'nan' and return a copy."""
    arr[arr < 0] = np.nan
    return arr

plot_arr = zero_to_nan(dataset.read(1))

fig, ax = plt.subplots()
img = ax.imshow(plot_arr, cmap='magma')
fig.colorbar(img, ax=ax)
ax.set_axis_off()
plt.show()
fig.savefig(fname = img_path, dpi = 300, format = 'png')


# plt.imshow(dataset.read(1), cmap='magma')

print("Total Time: " + str(datetime.now() - startTime))  # get the time