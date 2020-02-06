import os
import numpy as np
import sfm_gridz
import sfm_gridz.plot_gridz as pcplot
import rasterio
from rasterio.plot import show_hist
from matplotlib import pyplot as plt

out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v2")

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

DOD_Dec16_Feb17 = os.path.join(out_ras_home, "DOD_Dec16_Feb17.tif")
DOD_Feb17_Jan18 = os.path.join(out_ras_home, "DOD_Feb17_Jan18.tif")
DOD_Jan18_March18 = os.path.join(out_ras_home, "DOD_Jan18_March18.tif")

DoD_Dec16_Jan18 = os.path.join(out_ras_home, "DoD_Dec16_Jan18.tif")

for i in [DoD_Dec16_Mar18, DoD_Sep17_Sep18]:
    if os.path.isfile(i):
        os.remove(i)

epsg_code = 27700
mask_shp = os.path.abspath('C:/HG_Projects/CWC_Drone_work/shp_files/CWC_AOI.shp')
def run_functions():

    # Start - Finish (SUMMER)
    Sep17_Sep18 = sfm_gridz.difference(raster_1=dsm1709, raster_2=dsm1809,
                                       prec_point_cloud_1=pcp1709, prec_point_cloud_2=pcp1809,
                                       out_ras=DoD_Sep17_Sep18, epsg=epsg_code, mask=mask_shp)

    pcplot.plot_dem_of_diff(Sep17_Sep18.ras_out_path, save_path=os.path.join(out_ras_home, "DOD_example1.jpg"),
                            v_range=(-5, 5), title="Sep 2017 - Sep 2018")



    #WINTER TS3.
    Jan18_March18 = sfm_gridz.difference(raster_1=dsm1801, raster_2=dsm1803,
                                       prec_point_cloud_1=pcp1801, prec_point_cloud_2=pcp1803,
                                       out_ras=DOD_Jan18_March18, epsg=epsg_code, mask=mask_shp)
    pcplot.plot_dem_of_diff(Jan18_March18.ras_out_path, save_path=os.path.join(out_ras_home, "Jan18_March18_DOD.jpg"),
                            v_range=(-5, 5), title="Jan 2018 - Mar 2018")

    #WINTER TS2.
    Feb17_Jan18 = sfm_gridz.difference(raster_1=dsm1702, raster_2=dsm1801,
                                       prec_point_cloud_1=pcp1702, prec_point_cloud_2=pcp1801,
                                       out_ras=DOD_Feb17_Jan18, epsg=epsg_code, mask=mask_shp)
    pcplot.plot_dem_of_diff(Feb17_Jan18.ras_out_path, save_path=os.path.join(out_ras_home, "Feb17_Jan18_DOD.jpg"),
                            v_range=(-5, 5), title="Feb 2017 - Jan 2018")

    # WINTER TS1.
    Dec16_Feb17 = sfm_gridz.difference(raster_1=dsm1612, raster_2=dsm1702,
                                       prec_point_cloud_1=pcp1612, prec_point_cloud_2=pcp1702,
                                       out_ras=DOD_Dec16_Feb17, epsg=epsg_code, mask=mask_shp)
    pcplot.plot_dem_of_diff(Dec16_Feb17.ras_out_path, save_path=os.path.join(out_ras_home, "Dec16_Feb17_DOD.jpg"),
                            v_range=(-5, 5), title="Dec 2016 - Feb 2017")

    # WINTER 1-2.
    Dec16_Jan18 = sfm_gridz.difference(raster_1=dsm1612, raster_2=dsm1801,
                                       prec_point_cloud_1=pcp1612, prec_point_cloud_2=pcp1801,
                                       out_ras=DoD_Dec16_Jan18, epsg=epsg_code, mask=mask_shp)
    pcplot.plot_dem_of_diff(Dec16_Jan18.ras_out_path, save_path=os.path.join(out_ras_home, "Dec16_Jan18_DOD.jpg"),
                            v_range=(-5, 5), title="Dec 2016 - Jan2018")

    # Start - Finish (WINTER)
    Dec16_Mar18 = sfm_gridz.difference(raster_1=dsm1612, raster_2=dsm1803,
                                       prec_point_cloud_1=pcp1612, prec_point_cloud_2=pcp1803,
                                       out_ras=DoD_Dec16_Mar18, epsg=epsg_code, mask=mask_shp)

    pcplot.plot_dem_of_diff(Dec16_Mar18.ras_out_path, save_path=os.path.join(out_ras_home, "Dec16_Mar18_DOD.jpg"),
                            v_range=(-5, 5), title="Dec 2016 - Mar 2018")

    #
    pcplot.plot_dsm(dsm_path=dsm1809, dpi=300, save_path=os.path.join(out_ras_home, "test_dsm1.jpg"))

    pcplot.plot_precision(prec_map_path=pcp1809, dpi=300, save_path=os.path.join(out_ras_home, "test_precmap1.jpg"))

    pcplot.plot_roughness(dsm_path=dsm1809, dpi=300, save_path=os.path.join(out_ras_home, "test_roughness1.jpg"))

    # pcplot.plot_lod(Dec16_Mar18.ras_out_path, save_path=os.path.join(out_ras_home, "Dec16_Mar18_LOD.jpg"))
    #
    # pcplot.hist_dem_of_diff(Dec16_Mar18.ras_out_path, range=(-2, 2), n_bins=50,
    #                         save_path=os.path.join(out_ras_home, "Dec16_Mar18_DOD_hist.jpg"))
    #
    # pcplot.hist_lod(Dec16_Mar18.ras_out_path, n_bins=50, save_path=os.path.join(out_ras_home, "Dec16_Mar18_LOD_hist.jpg"))
    #
    # pcplot.plot_dem_of_diff(Sep17_Sep18.ras_out_path, save_path=os.path.join(out_ras_home, "DOD_example1.jpg"),
    #                         v_range=(-5, 5))
    # pcplot.plot_lod(Sep17_Sep18.ras_out_path, save_path=os.path.join(out_ras_home, "Sep17_Sep18_LOD.jpg"))


if __name__ == '__main__':
    run_functions()
