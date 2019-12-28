###  Script to convert the Precision point cloud from MS_Prec_Estim.py into a Raster and visualise results.

import pdal
import rasterio
from rasterio.plot import show
import json
from datetime import datetime
import numpy as np
import math
import os
from matplotlib import pyplot as plt
import geopandas as gpd
import fiona
# import pandas as pd # Pandas section is currently commented out.


startTime = datetime.now()

def readPLY_xyerr(ply):
    plydata = np.loadtxt(ply, delimiter=' ', skiprows=1,
                         dtype={'names': ('x', 'y', 'z', 'xerr', 'yerr', 'zerr'),
                                'formats': ('f8', 'f8', 'f8', 'f8', 'f8', 'f8')})

    mean_err = max([np.mean(plydata['xerr']),
                    np.mean(plydata['yerr'])])
    std_err = max([np.std(plydata['xerr']),
                    np.std(plydata['yerr'])])
    # mean_add_std = math.ceil((mean_err + std_err)*10)/10
    mean_add_std = math.ceil((mean_err + std_err) * 10000) / 10000  # Why is this * & / 10000 needed?
    # print(max_err)
    print(mean_add_std)
    print(np.mean(plydata['zerr']))

    return mean_add_std

home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1/Rasters") # provide project directory
# export_loc = home + "/exports"   # export folder (needs to be created before script run)

# pc_filename = "C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1/MonteCarlo_Export/MonteCarloResult_v6.ply" # point cloud file
# pc_filename = "C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1/MonteCarlo_Export/MonteCarloResult_v5.ply"
# pc_filename = "C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1/MonteCarlo_Export_pia/MonteCarloResult_New_it_1000V2.txt"
# pc_filename = os.path.abspath("C:/HG_Projects/CWC_Drone_work/HG_Retest_CWC_10it/Monte_Carlo_output/Final_PointCloud.txt")
pc_filename = os.path.abspath("C:/HG_Projects/CWC_Drone_work/HG_Retest_Pia_1000_it/Monte_Carlo_output/Final_PointCloud.txt")
out_dem = os.path.join(home, "Prec_test_CWC.tif") #  name of output

img_path = os.path.join(home, "Prec_Pia_NEW1000it.png")

gcp_file = os.path.abspath("C:/HG_Projects/CWC_Drone_work/GCP_locs/shp_file/Danes_Croft_GCPsV2.shp")
print("starting pipeline")


res = readPLY_xyerr(pc_filename)

if res < 0.005:
    print("maimum xy error is < 1m, setting Raster resolution to 1m")
    res = 0.005
# if res < 1:
#     print("maimum xy error is < 1m, setting Raster resolution to 1m")
#     res = 1

# Points-to-Grid
sfm_prec_p2g = {
    "pipeline":[
        {
            "type": "readers.text",
            "filename":  pc_filename
        },

        {
            "type":"writers.gdal",
            "filename": sfm_prec_raster,  # output file name
            "resolution": res,
            "dimension": "zerr",  # raster resolution
            # "radius": res*2,  # radius in which to search for other points
            "output_type": "all",  # creates a multiband raster with: min, max, mean, idw, count, stdev
            # "output_type": "stdev",  # use this if you just want a single band output for e.g. stdev
            "window_size": 20 # changes the search area around an empty cell - second stage of algorithm
        },                       # may want this value to be a bit smaller than at present...

    ]
}

pipeline = pdal.Pipeline(json.dumps(sfm_prec_p2g)) # define the pdal pipeline
pipeline.validate()  # validate the pipeline
pipeline.execute()   #  run the pipeline


dataset = rasterio.open(sfm_prec_raster)

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


fig, ax = plt.subplots(figsize=(8, 8))
img = ax.imshow(plot_arr, cmap='twilight_shifted')
fig.colorbar(img, ax=ax)
ax.set_axis_off()
plt.show()
fig.savefig(fname = img_path, dpi = 300, format = 'png')



# gcps = gpd.read_file(gcp_file)
#
fig, ax = plt.subplots(figsize=(10,10))
rasterio.plot.show(dataset, ax=ax, cmap ='twilight_shifted')
# gcps.plot(ax=ax, column='type', cmap='gist_gray', markersize=50, legend=True)
plt.show()
# fig.savefig(fname = img_path, dpi = 300, format = 'png')
# # plt.imshow(dataset.read(1), cmap='magma')



print("Total Time: " + str(datetime.now() - startTime))  # get the time
