import os
import numpy as np
from PointCloudStat.dem_of_diff import dem_of_diff
import PointCloudStat.Plot as pcplot
import rasterio
from rasterio.plot import show_hist
from matplotlib import pyplot as plt

out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v1")

dsm1612 = os.path.join(out_ras_home, "dsm1.tif")
dsm1702 = os.path.join(out_ras_home, "dsm2.tif")
dsm1709 = os.path.join(out_ras_home, "dsm3.tif")
dsm1801 = os.path.join(out_ras_home, "dsm4.tif")
dsm1803 = os.path.join(out_ras_home, "dsm5.tif")
dsm1809 = os.path.join(out_ras_home, "dsm6.tif")

pcp1612 = os.path.join(out_ras_home, "pcc1.tif")
pcp1702 = os.path.join(out_ras_home, "pcc2.tif")
pcp1709 = os.path.join(out_ras_home, "pcc3.tif")
pcp1801 = os.path.join(out_ras_home, "pcc4.tif")
pcp1803 = os.path.join(out_ras_home, "pcc5.tif")
pcp1809 = os.path.join(out_ras_home, "pcc6.tif")

DoD_Dec16_Mar18 = os.path.join(out_ras_home, "DoD_Dec16_Mar18.tif")

DoD_Sep17_Sep18 = os.path.join(out_ras_home, "DoD_Sep17_Sep18.tif")

for i in [DoD_Dec16_Mar18, DoD_Sep17_Sep18]:
    if os.path.isfile(i):
        os.remove(i)

epsg_code = 27700
mask_shp = os.path.abspath('C:/HG_Projects/CWC_Drone_work/shp_files/CWC_AOI.shp')
def run_functions():

    # Start - Finish (WINTER)
    Dec16_Mar18 = dem_of_diff(raster_1=dsm1612, raster_2=dsm1803,
                              prec_point_cloud_1=pcp1612, prec_point_cloud_2=pcp1803,
                              out_ras=DoD_Dec16_Mar18, epsg=epsg_code)

    # pcplot.plot_dsm(dsm_path=dsm1612, dpi=200, save_path=os.path.join(out_ras_home, "test_dsm1.jpg"))

    pcplot.plot_dem_of_diff(Dec16_Mar18.ras_out_path, save_path=os.path.join(out_ras_home, "Dec16_Mar18_DOD.jpg"),
                            v_range=(-5, 5), title="Dec16 - Mar18 Elevation Change")
    pcplot.plot_lod(Dec16_Mar18.ras_out_path, save_path=os.path.join(out_ras_home, "Dec16_Mar18_LOD.jpg"))

    pcplot.hist_dem_of_diff(Dec16_Mar18.ras_out_path, range=(-2, 2), n_bins=50,
                            save_path=os.path.join(out_ras_home, "Dec16_Mar18_DOD_hist.jpg"))

    pcplot.hist_lod(Dec16_Mar18.ras_out_path, n_bins=50, save_path=os.path.join(out_ras_home, "Dec16_Mar18_LOD_hist.jpg"))

    # Start - Finish (SUMMER)
    Sep17_Sep18 = dem_of_diff(raster_1=dsm1709, raster_2=dsm1809,
                              prec_point_cloud_1=pcp1709, prec_point_cloud_2=pcp1809,
                              out_ras=DoD_Sep17_Sep18, epsg=epsg_code, mask=mask_shp)

    pcplot.plot_dem_of_diff(Sep17_Sep18.ras_out_path, save_path=os.path.join(out_ras_home, "Sep17_Sep18_DOD.jpg"),
                            v_range=(-5, 5), title="Sep17 - Sep18 Elevation Change")
    pcplot.plot_lod(Sep17_Sep18.ras_out_path, save_path=os.path.join(out_ras_home, "Sep17_Sep18_LOD.jpg"))



if __name__ == '__main__':
    run_functions()
