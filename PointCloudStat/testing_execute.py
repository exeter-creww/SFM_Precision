from PointCloudStat.precision_map import precision_map
import os
from rasterio.plot import show
from matplotlib import pyplot as plt

pc_filename = os.path.abspath("C:/HG_Projects/CWC_Drone_work/PrecAnal_Testing/HG_Retest_Pia_1000_it/"
                              "Monte_Carlo_output/Final_PointCloud.txt")

ras = precision_map(pc_filename, 0.01)

data = ras.raster

fig = plt.gcf()
show(data, cmap='twilight_shifted')

print("done")