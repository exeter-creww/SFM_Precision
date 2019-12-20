from PointCloudStat.precision_map import precision_map
import os
import rasterio
from rasterio.plot import show
from matplotlib import pyplot as plt

dpc_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_02_15_Danes_Mill/17_02_15_Exports/"
                           "CWC_examplePC_clip.laz")

pcp_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                              "18_09_25_DanesCroft_SFM_PREC/18_09_25_DanesCroft_Prec_Cloud.txt")
out_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                          "18_09_25_DanesCroft_SFM_PREC/Testing_New_Module/test_raster.tif")



ras = precision_map(prec_point_cloud=pcp_path, out_raster=out_path, resolution=1, prec_dimension='zerr')

data = rasterio.open(ras.path)


fig = plt.gcf()
show(data, cmap='twilight_shifted')

print("done")