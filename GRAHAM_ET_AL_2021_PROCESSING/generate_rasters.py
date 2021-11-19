# This is hugh's CWC workflow and is a bit more specific to the use case...

import sfm_gridz
import sfm_gridz.plot_gridz as pcplot
import os
import sys

# --- INPUTS ---
dpc1_path = os.path.abspath("D:/CWC_Drone_Processing/16_12_18_Danes_Mill/16_12_18_Exports/"
                            "16_12_18_DanesCroft_dpc_export.laz")
dpc3_path = os.path.abspath("D:/CWC_Drone_Processing/17_09_07_Danes_Mill/17_09_07_Exports/"
                            "17_09_07_DanesCroft_dpc_export.laz")
dpc4_path = os.path.abspath("D:/CWC_Drone_Processing/18_01_23_Danes_Mill/18_01_23_Exports/"
                            "18_01_23_DanesCroft_dpc_export.laz")
dpc6_path = os.path.abspath("D:/CWC_Drone_Processing/18_09_25_Danes_Mill/18_09_25_Exports/"
                            "18_09_25_DanesCroft_dpc_export.laz")


pcp1_path = os.path.abspath("D:/CWC_Drone_Processing/16_12_18_Danes_Mill/"
                            "16_12_18_DanesCroft_SFM_PREC/16_12_18_DanesCroft_Prec_Cloud.txt")
pcp3_path = os.path.abspath("D:/CWC_Drone_Processing/17_09_07_Danes_Mill/"
                            "17_09_07_DanesCroft_SFM_PREC/17_09_07_DanesCroft_Prec_Cloud.txt")
pcp4_path = os.path.abspath("D:/CWC_Drone_Processing/18_01_23_Danes_Mill/"
                            "18_01_23_DanesCroft_SFM_PREC/18_01_23_DanesCroft_Prec_Cloud.txt")
pcp6_path = os.path.abspath("D:/CWC_Drone_Processing/18_09_25_Danes_Mill/"
                            "18_09_25_DanesCroft_SFM_PREC/18_09_25_DanesCroft_Prec_Cloud.txt")

dtm_path = os.path.abspath('C:/HG_Projects/CWC_Drone_work/DTM/Lidar_mosaic/CWC_Lidar_DTM.tif')

mask_shp = os.path.abspath('C:/HG_Projects/CWC_Drone_work/shp_files/CWC_AOI_V2.shp')

# --- CHECK INPUTS ARE CORRECT ---
for i in [dpc1_path, dpc3_path, dpc4_path, dpc6_path,
          pcp1_path, pcp3_path, pcp4_path, pcp6_path, dtm_path, mask_shp]:
    if os.path.isfile(i) is False:
        print(i)
        sys.exit("One of the paths is wrong - fix it...")

# --- SET AND CREATE OUT FOLDER ---
out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v6")
if os.path.isdir(out_ras_home) is False:
    os.mkdir(out_ras_home)

# --- DEFINE OUT PATH NAMES ---
dsm1_out = os.path.join(out_ras_home, "dsm1.tif")
dsm3_out = os.path.join(out_ras_home, "dsm3.tif")
dsm4_out = os.path.join(out_ras_home, "dsm4.tif")
dsm6_out = os.path.join(out_ras_home, "dsm6.tif")

chm1_out = os.path.join(out_ras_home, "chm1.tif")
chm3_out = os.path.join(out_ras_home, "chm3.tif")
chm4_out = os.path.join(out_ras_home, "chm4.tif")
chm6_out = os.path.join(out_ras_home, "chm6.tif")

pcp1_out = os.path.join(out_ras_home, "pcc1.tif")
pcp3_out = os.path.join(out_ras_home, "pcc3.tif")
pcp4_out = os.path.join(out_ras_home, "pcc4.tif")
pcp6_out = os.path.join(out_ras_home, "pcc6.tif")


DoD_Dec16_Jan18_Thresh = os.path.join(out_ras_home, "DoD_Dec16_Jan18_threshold.tif")
DoD_Dec16_Jan18_Weight = os.path.join(out_ras_home, "DoD_Dec16_Jan18_weight.tif")
DoD_Sep17_Sep18_Thresh = os.path.join(out_ras_home, "DoD_Sep17_Sep18_threshold.tif")
DoD_Sep17_Sep18_Weight = os.path.join(out_ras_home, "DoD_Sep17_Sep18_weight.tif")


# --- DEFINE CRS ---
epsg_code = 27700

# --- MAIN CODE BLOCK ---
def main():

    dsm1 = sfm_gridz.dsm(point_cloud=dpc1_path, out_raster=dsm1_out, resolution=0.5, window_size=10,
                         epsg=epsg_code, mask=mask_shp)
    dsm3 = sfm_gridz.dsm(point_cloud=dpc3_path, out_raster=dsm3_out, resolution=0.5, window_size=10,
                         epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    dsm4 = sfm_gridz.dsm(point_cloud=dpc4_path, out_raster=dsm4_out, resolution=0.5, window_size=10,
                         epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    dsm6 = sfm_gridz.dsm(point_cloud=dpc6_path, out_raster=dsm6_out, resolution=0.5, window_size=10,
                         epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)

    for x in [dsm1, dsm3, dsm4, dsm6]:
        pcplot.plot_dsm(dsm_path=x.path)
        pcplot.plot_roughness(dsm_path=x.path)

    chm1 = sfm_gridz.chm(dsm_file=dsm1.path, dtm_file=dtm_path, chm_save_name=chm1_out)
    chm3 = sfm_gridz.chm(dsm_file=dsm3.path, dtm_file=dtm_path, chm_save_name=chm3_out)
    chm4 = sfm_gridz.chm(dsm_file=dsm4.path, dtm_file=dtm_path, chm_save_name=chm4_out)
    chm6 = sfm_gridz.chm(dsm_file=dsm6.path, dtm_file=dtm_path, chm_save_name=chm6_out)

    for x in [chm1, chm3, chm4, chm6]:
        pcplot.plot_chm(chm_path=x.path)
        pcplot.plot_roughness(dsm_path=x.path)
        # pcplot.plot_dtm(chm_path=x.path)

    prras1 = sfm_gridz.precision(prec_point_cloud=pcp1_path, out_raster=pcp1_out, resolution=1,
                                 prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    prras3 = sfm_gridz.precision(prec_point_cloud=pcp3_path, out_raster=pcp3_out, resolution=1,
                                 prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    prras4 = sfm_gridz.precision(prec_point_cloud=pcp4_path, out_raster=pcp4_out, resolution=1,
                                 prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)
    prras6 = sfm_gridz.precision(prec_point_cloud=pcp6_path, out_raster=pcp6_out, resolution=1,
                                 prec_dimension='z', epsg=epsg_code, bounds=dsm1.bounds, mask=mask_shp)

    print(prras6.pr_dim)

    for x in [prras1, prras3, prras4, prras6]:
        pcplot.plot_precision(prec_map_path=x.path, fill_gaps=True)

    # generate DoDs
    #Summer
    Sep17_Sep18_thresh = sfm_gridz.difference(raster_1=chm1_out, raster_2=chm4_out,
                                       prec_point_cloud_1=pcp1_out, prec_point_cloud_2=pcp4_out,
                                       out_ras=DoD_Dec16_Jan18_Thresh, epsg=epsg_code, mask=mask_shp,
                                              lod_method='threshold')
    Sep17_Sep18_weight = sfm_gridz.difference(raster_1=chm1_out, raster_2=chm4_out,
                                       prec_point_cloud_1=pcp1_out, prec_point_cloud_2=pcp4_out,
                                       out_ras=DoD_Dec16_Jan18_Weight, epsg=epsg_code, mask=mask_shp,
                                              lod_method='weighted')

    # #winter
    Dec16_Jan18_thresh = sfm_gridz.difference(raster_1=chm3_out, raster_2=chm6_out,
                                       prec_point_cloud_1=pcp3_out, prec_point_cloud_2=pcp6_out,
                                       out_ras=DoD_Sep17_Sep18_Thresh, epsg=epsg_code, mask=mask_shp,
                                       lod_method='threshold')
    Dec16_Jan18_weight = sfm_gridz.difference(raster_1=chm3_out, raster_2=chm6_out,
                                       prec_point_cloud_1=pcp3_out, prec_point_cloud_2=pcp6_out,
                                       out_ras=DoD_Sep17_Sep18_Weight, epsg=epsg_code, mask=mask_shp,
                                       lod_method='weighted')

    for x in [Sep17_Sep18_thresh, Sep17_Sep18_weight, Dec16_Jan18_thresh, Dec16_Jan18_weight]:
        pcplot.plot_dem_of_diff(dem_o_diff_path=x.ras_out_path)


if __name__ == '__main__':
    main()
