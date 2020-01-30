# This script is not part of the package it is an example workflow of how the package can be used to
# derive a DEM of difference.

import os
from PointCloudStat.precision_map import precision_map
from PointCloudStat.DSM import height_map
from PointCloudStat.dem_of_diff import dem_of_diff
import PointCloudStat.Plot as PcPlot

dpc1_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_09_07_Danes_Mill/17_09_07_Exports/"
                           "17_09_07_DanesCroft_dpc_export.laz")

dpc2_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/18_09_25_Exports/"
                           "18_09_25_DanesCroft_dpc_export.laz")

pcp1_path = os.path.abspath("C:/HG_Projects\CWC_Drone_work/17_09_07_Danes_Mill/"
                            "17_09_07_DanesCroft_SFM_PREC/17_09_07_DanesCroft_Prec_Cloud.txt")

pcp2_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                            "18_09_25_DanesCroft_SFM_PREC/18_09_25_DanesCroft_Prec_Cloud.txt")

out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Demo_v1")

dsm1_out = os.path.join(out_ras_home, "dsm1.tif")
dsm2_out = os.path.join(out_ras_home, "dsm2.tif")

pcp1_out = os.path.join(out_ras_home, "pcc1.tif")
pcp2_out = os.path.join(out_ras_home, "pcc2.tif")

dod_out_path = os.path.join(out_ras_home, "dod.tif")

def main():
    epsg_code = 27700

    # Create and plot Digital Surface Models (DSM)
    dsm1 = height_map(point_cloud=dpc1_path, out_raster=dsm1_out, resolution=0.5, window_size=10, epsg=epsg_code)

    dsm2 = height_map(point_cloud=dpc2_path, out_raster=dsm2_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds)

    for i in [dsm1, dsm2]:
        PcPlot.plot_dsm(dsm_path=i.path)
        PcPlot.plot_roughness(dsm_path=i.path)

    # Create and plot Precision Maps
    prras1 = precision_map(prec_point_cloud=pcp1_path, out_raster=pcp1_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)

    prras2 = precision_map(prec_point_cloud=pcp2_path, out_raster=pcp2_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)

    for i in [prras1, prras2]:

        PcPlot.plot_precision(prec_map_path=i.path, fill_gaps=True)

    # Calculate a DEM of Difference Raster
    demod = dem_of_diff(raster_1=dsm1.path, raster_2=dsm2.path,
                              prec_point_cloud_1=prras1.path, prec_point_cloud_2=prras2.path,
                              out_ras=dod_out_path, epsg=epsg_code)

    PcPlot.plot_dem_of_diff(demod.ras_out_path, v_range=(-5, 5))
    PcPlot.plot_lod(demod.ras_out_path)

    PcPlot.hist_dsm(dsm1.path)
    PcPlot.hist_roughness(dsm1.path)
    PcPlot.hist_precision(pcp2_path, n_bins=50)
    PcPlot.hist_lod(demod.ras_out_path)
    PcPlot.hist_dem_of_diff(demod.ras_out_path)


if __name__ == '__main__':
    main()
