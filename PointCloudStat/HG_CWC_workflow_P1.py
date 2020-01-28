# This is hugh's CWC workflow and is a bit more specific to the use case...

from PointCloudStat.precision_map import precision_map
from PointCloudStat.DSM import height_map
from PointCloudStat.dem_of_diff import dem_of_diff

import os
import sys
import rasterio
from rasterio.plot import show
from matplotlib import pyplot as plt

import numpy as np
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

for i in [dpc1_path, dpc2_path, dpc3_path, dpc4_path, dpc5_path, dpc6_path,
          pcp1_path, pcp2_path, pcp3_path, pcp4_path, pcp5_path, pcp6_path]:
    if os.path.isfile(i) is False:
        print(i)
        sys.exit("One of the paths is wrong - fix it...")


out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v1")

dsm1_out = os.path.join(out_ras_home, "dsm1.tif")
dsm2_out = os.path.join(out_ras_home, "dsm2.tif")
dsm3_out = os.path.join(out_ras_home, "dsm3.tif")
dsm4_out = os.path.join(out_ras_home, "dsm4.tif")
dsm5_out = os.path.join(out_ras_home, "dsm5.tif")
dsm6_out = os.path.join(out_ras_home, "dsm6.tif")

pcp1_out = os.path.join(out_ras_home, "pcc1.tif")
pcp2_out = os.path.join(out_ras_home, "pcc2.tif")
pcp3_out = os.path.join(out_ras_home, "pcc3.tif")
pcp4_out = os.path.join(out_ras_home, "pcc4.tif")
pcp5_out = os.path.join(out_ras_home, "pcc5.tif")
pcp6_out = os.path.join(out_ras_home, "pcc6.tif")

dod_out_path = os.path.join(out_ras_home, "dod.tif")

def main():
    epsg_code = 27700

    dsm1 = height_map(point_cloud=dpc1_path, out_raster=dsm1_out, resolution=0.5, window_size=10, epsg=epsg_code)

    dsm2 = height_map(point_cloud=dpc2_path, out_raster=dsm2_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds)
    dsm3 = height_map(point_cloud=dpc3_path, out_raster=dsm3_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds)
    dsm4 = height_map(point_cloud=dpc4_path, out_raster=dsm4_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds)
    dsm5 = height_map(point_cloud=dpc5_path, out_raster=dsm5_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds)
    dsm6 = height_map(point_cloud=dpc6_path, out_raster=dsm6_out, resolution=0.5, window_size=10,
                      epsg=epsg_code, bounds=dsm1.bounds)

    for i in [dsm1, dsm2, dsm3, dsm4, dsm5, dsm6]:

        with rasterio.open(i.path) as h_map:
            for i in range(1, 3):
                arr = h_map.read(i)
                arr[arr == -999] = np.nan
                show(arr, cmap='viridis')

    prras1 = precision_map(prec_point_cloud=pcp1_path, out_raster=pcp1_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)
    prras2 = precision_map(prec_point_cloud=pcp2_path, out_raster=pcp2_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)
    prras3 = precision_map(prec_point_cloud=pcp3_path, out_raster=pcp3_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)
    prras4 = precision_map(prec_point_cloud=pcp4_path, out_raster=pcp4_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)
    prras5 = precision_map(prec_point_cloud=pcp5_path, out_raster=pcp5_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)
    prras6 = precision_map(prec_point_cloud=pcp6_path, out_raster=pcp6_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)



    for i in [prras1, prras2, prras3, prras4, prras5, prras6]:

        with rasterio.open(i.path) as p_map:
            for i in range(1, 3):
                arr = p_map.read(i)
                arr[arr == -999] = np.nan
                show(arr, cmap='viridis')


    # finest_res = ras.min_res
    #     # print(finest_res)
    #     #
    #     # chosen_res = myround(finest_res)



    # for now i'm just using several of the same raster - obviously you wouldn't do this for real...
    # demod = dem_of_diff(raster_1=dsm1.path, raster_2=dsm2.path,
    #                     prec_point_cloud_1=prras1.path, prec_point_cloud_2=prras2.path,
    #                     out_ras=dod_out_path, epsg=epsg_code)

    # demod = dem_of_diff(raster_1=dsm1_out, raster_2=dsm2_out,
    #                     prec_point_cloud_1=pcp1_out, prec_point_cloud_2=pcp2_out,
    #                     out_ras=dod_out_path, epsg=epsg_code)



    # with rasterio.open(demod.ras_out_path) as dod_map:
    #     arr = dod_map.read(1)
    #     print(np.mean(arr))
    #     print(np.max(arr))
    #     print(np.min(arr[arr!=-999]))
    #
    #     # trans = rasterio.plot.plotting_extent(dod_map)
    #     trans = dod_map.bounds[:2]
    #
    #     show((dod_map,1), cmap='twilight_shifted_r', title='Height Change Map', vmin=-5, vmax=5)  # plot with rasterio
    #
    #     # plot with matplotlib
    #
    #     fig, ax = plt.subplots(figsize=(8, 8))
    #     img = ax.imshow(arr, cmap='twilight_shifted_r', vmin=-5, vmax=5)
    #     fig.colorbar(img, ax=ax)
    # from matplotlib import ticker
    # # ax.set_ylim(ax.get_ylim()[1], ax.get_ylim()[0])
    # ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=-trans[0],useMathText=False))
    # ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=-(trans[1]+ax.get_ylim()[0]), useMathText=False))
    # ax.set_axis_off()

    # plt.ylim(102800, 106025)
    # plt.xlim(307500, 308100)

    # fig.savefig(fname= os.path.join(out_ras_home, "dod_example.png"), dpi=300, format='png')

    print("done")


if __name__ == '__main__':
    main()








# from matplotlib import pyplot as plt
# for i in range(1,3):
#     a = src.read(i)
#     a[a==-999] = np.nan
#
#     fig, ax = plt.subplots(figsize=(8, 8))
#     img = ax.imshow(a, cmap='viridis')
#     fig.colorbar(img, ax=ax)
#     ax.set_axis_off()
#     plt.show()

# from matplotlib import pyplot as plt
# fig, ax = plt.subplots(figsize=(8, 8))
# img = ax.imshow(lod, cmap='viridis')
# fig.colorbar(img, ax=ax)
# ax.set_axis_off()
# plt.show()