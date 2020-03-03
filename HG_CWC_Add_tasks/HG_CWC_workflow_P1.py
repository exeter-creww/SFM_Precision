# This is hugh's CWC workflow and is a bit more specific to the use case...

import sfm_gridz
import sfm_gridz.plot_gridz as pcplot
import os
import sys

dpc1_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/16_12_18_Danes_Mill/16_12_18_Exports/"
                           "16_12_18_DanesCroft_dpc_export.laz")

dpc2_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_02_15_Danes_Mill/17_02_15_Exports/"
                           "17_02_15_DanesCroft_dpc_export.laz")

dpc3_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_09_07_Danes_Mill/17_09_07_Exports/"
                           "17_09_07_DanesCroft_dpc_export.laz")

dpc4_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_01_23_Danes_Mill/18_01_23_Exports/"
                           "18_01_23_DanesCroft_dpc_export.laz")

dpc5_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_03_27_Danes_Mill/18_03_27_Exports/"
                           "18_03_27_DanesCroft_dpc_export.laz")

dpc6_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/18_09_25_Exports/"
                           "18_09_25_DanesCroft_dpc_export.laz")


pcp1_path = os.path.abspath("C:/HG_Projects\CWC_Drone_work/16_12_18_Danes_Mill/"
                            "16_12_18_DanesCroft_SFM_PREC/16_12_18_DanesCroft_Prec_Cloud.txt")

pcp2_path = os.path.abspath("C:/HG_Projects\CWC_Drone_work/17_02_15_Danes_Mill/"
                            "17_02_15_DanesCroft_SFM_PREC/17_02_15_DanesCroft_Prec_Cloud.txt")

pcp3_path = os.path.abspath("C:/HG_Projects\CWC_Drone_work/17_09_07_Danes_Mill/"
                            "17_09_07_DanesCroft_SFM_PREC/17_09_07_DanesCroft_Prec_Cloud.txt")

pcp4_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_01_23_Danes_Mill/"
                            "18_01_23_DanesCroft_SFM_PREC/18_01_23_DanesCroft_Prec_Cloud.txt")

pcp5_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_03_27_Danes_Mill/"
                            "18_03_27_DanesCroft_SFM_PREC/18_03_27_DanesCroft_Prec_Cloud.txt")

pcp6_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                            "18_09_25_DanesCroft_SFM_PREC/18_09_25_DanesCroft_Prec_Cloud.txt")

dtm_path = os.path.abspath('C:/HG_Projects/CWC_Drone_work/DTM/Lidar_mosaic/CWC_Lidar_DTM.tif')

for i in [dpc1_path, dpc2_path, dpc3_path, dpc4_path, dpc5_path, dpc6_path,
          pcp1_path, pcp2_path, pcp3_path, pcp4_path, pcp5_path, pcp6_path, dtm_path]:
    if os.path.isfile(i) is False:
        print(i)
        sys.exit("One of the paths is wrong - fix it...")


out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v4")
if os.path.isdir(out_ras_home) is False:
    os.mkdir(out_ras_home)

dsm1_out = os.path.join(out_ras_home, "dsm1.tif")
dsm2_out = os.path.join(out_ras_home, "dsm2.tif")
dsm3_out = os.path.join(out_ras_home, "dsm3.tif")
dsm4_out = os.path.join(out_ras_home, "dsm4.tif")
dsm5_out = os.path.join(out_ras_home, "dsm5.tif")
dsm6_out = os.path.join(out_ras_home, "dsm6.tif")

chm1_out = os.path.join(out_ras_home, "chm1.tif")
chm2_out = os.path.join(out_ras_home, "chm2.tif")
chm3_out = os.path.join(out_ras_home, "chm3.tif")
chm4_out = os.path.join(out_ras_home, "chm4.tif")
chm5_out = os.path.join(out_ras_home, "chm5.tif")
chm6_out = os.path.join(out_ras_home, "chm6.tif")

pcp1_out = os.path.join(out_ras_home, "pcc1.tif")
pcp2_out = os.path.join(out_ras_home, "pcc2.tif")
pcp3_out = os.path.join(out_ras_home, "pcc3.tif")
pcp4_out = os.path.join(out_ras_home, "pcc4.tif")
pcp5_out = os.path.join(out_ras_home, "pcc5.tif")
pcp6_out = os.path.join(out_ras_home, "pcc6.tif")

mask_shp = os.path.abspath('C:/HG_Projects/CWC_Drone_work/shp_files/CWC_AOI_V2.shp')
epsg_code = 27700

def main():

    dsm1 = sfm_gridz.dsm(point_cloud=dpc1_path, out_raster=dsm1_out, resolution=0.5, window_size=10,
                         epsg=epsg_code, mask=mask_shp)
    dsm2 = sfm_gridz.dsm(point_cloud=dpc2_path, out_raster=dsm2_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    dsm3 = sfm_gridz.dsm(point_cloud=dpc3_path, out_raster=dsm3_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    dsm4 = sfm_gridz.dsm(point_cloud=dpc4_path, out_raster=dsm4_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    dsm5 = sfm_gridz.dsm(point_cloud=dpc5_path, out_raster=dsm5_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    dsm6 = sfm_gridz.dsm(point_cloud=dpc6_path, out_raster=dsm6_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)

    for i in [dsm1, dsm2, dsm3, dsm4, dsm5, dsm6]:

        pcplot.plot_dsm(dsm_path=i.path)
        pcplot.plot_roughness(dsm_path=i.path)

    chm1 = sfm_gridz.chm(dsm_file=dsm1_out, dtm_file=dtm_path, chm_save_name=chm1_out)
    chm2 = sfm_gridz.chm(dsm_file=dsm2_out, dtm_file=dtm_path, chm_save_name=chm2_out)
    chm3 = sfm_gridz.chm(dsm_file=dsm3_out, dtm_file=dtm_path, chm_save_name=chm3_out)
    chm4 = sfm_gridz.chm(dsm_file=dsm4_out, dtm_file=dtm_path, chm_save_name=chm4_out)
    chm5 = sfm_gridz.chm(dsm_file=dsm5_out, dtm_file=dtm_path, chm_save_name=chm5_out)
    chm6 = sfm_gridz.chm(dsm_file=dsm6_out, dtm_file=dtm_path, chm_save_name=chm6_out)

    for i in [chm1, chm2, chm3, chm4, chm5, chm6]:
        pcplot.plot_chm(chm_path=i.path)
        pcplot.plot_roughness(dsm_path=i.path)
        pcplot.plot_dtm(chm_path=i.path)

    prras1 = sfm_gridz.precision(prec_point_cloud=pcp1_path, out_raster=pcp1_out, resolution=1,
                           prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    prras2 = sfm_gridz.precision(prec_point_cloud=pcp2_path, out_raster=pcp2_out, resolution=1,
                           prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    prras3 = sfm_gridz.precision(prec_point_cloud=pcp3_path, out_raster=pcp3_out, resolution=1,
                           prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    prras4 = sfm_gridz.precision(prec_point_cloud=pcp4_path, out_raster=pcp4_out, resolution=1,
                           prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    prras5 = sfm_gridz.precision(prec_point_cloud=pcp5_path, out_raster=pcp5_out, resolution=1,
                           prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    prras6 = sfm_gridz.precision(prec_point_cloud=pcp6_path, out_raster=pcp6_out, resolution=1,
                           prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)

    print(prras6.pr_dim)


    for i in [prras1, prras2, prras3, prras4, prras5, prras6]:

        pcplot.plot_precision(prec_map_path=i.path, fill_gaps=True)


    print("done")


if __name__ == '__main__':
    main()
