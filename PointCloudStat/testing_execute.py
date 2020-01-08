from PointCloudStat.precision_map import precision_map
from PointCloudStat.DSM import height_map
from PointCloudStat.dem_of_diff import dem_of_diff

import os
import rasterio
from rasterio.plot import show

import numpy as np

dpc1_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_02_15_Danes_Mill/17_02_15_Exports/"
                           "17_02_15_DanesCroft_dpc_export.laz")

dpc2_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_03_27_Danes_Mill/18_03_27_Exports"
                           "18_03_27_DanesCroft_dpc_export.laz")


pcp1_path = os.path.abspath("C:/HG_Projects\CWC_Drone_work/17_02_15_Danes_Mill/"
                            "17_02_15_DanesCroft_SFM_PREC/17_02_15_DanesCroft_Prec_Cloud.txt")

pcp2_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_03_27_Danes_Mill/"
                            "18_03_27_DanesCroft_SFM_PREC/18_03_27_DanesCroft_Prec_Cloud.txt")

out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/PrecAnal_Testing/CWC_DODs_Testing/1702_18_03")

dsm1_out = os.path.join(out_ras_home, "dsm1.tif")
dsm2_out = os.path.join(out_ras_home, "dsm2.tif")

pcp1_out = os.path.join(out_ras_home, "pcc1.tif")
pcp2_out = os.path.join(out_ras_home, "pcc1.tif")

dod_out_path = os.path.join(out_ras_home, "dod.tif")

def main():
    epsg_code = 27700

    # ?????
    dsm1 = height_map(point_cloud=dpc1_path, out_raster=dsm1_out, resolution=0.5, window_size=10, epsg=epsg_code,
                      stat='mean')

    dsm2 = height_map(point_cloud=dpc2_path, out_raster=dsm2_out, resolution=0.5, window_size=10, epsg=epsg_code,
                      stat='mean', bounds=dsm1.bounds)

    # with rasterio.open(dsm.path) as h_map:
    #     for i in range(1, 3):
    #         arr = h_map.read(i)
    #         arr[arr == -999] = np.nan
    #         show(arr, cmap='viridis')
    #     # print("pause")

    prras1 = precision_map(prec_point_cloud=pcp1_path, out_raster=pcp1_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)

    prras2 = precision_map(prec_point_cloud=pcp1_path, out_raster=pcp1_out, resolution=1,
                           prec_dimension='zerr', epsg=epsg_code, bounds=dsm1.bounds)

    # with rasterio.open(prras.path) as p_map:
    #     for i in range(1, 3):
    #         arr = p_map.read(i)
    #         arr[arr == -999] = np.nan
    #         show(arr, cmap='viridis')
    #
    #     print(np.min(p_map.read(1)))
    #     print(np.max(p_map.read(1)))
    #     print(p_map.crs)
        # print('pause')


    # finest_res = ras.min_res
    #     # print(finest_res)
    #     #
    #     # chosen_res = myround(finest_res)



    # for now i'm just using several of the same raster - obviously you wouldn't do this for real...
    demod = dem_of_diff(raster_1=dsm1.path, raster_2=dsm2.path,
                        prec_point_cloud_1=prras1.path, prec_point_cloud_2=prras2.path,
                        out_ras=dod_out_path, epsg=epsg_code)

    with rasterio.open(demod.ras_out_path) as dod_map:
        # arr = p_map.read(1)
        # arr[arr == -999] = np.nan
        show(dod_map, cmap='viridis')

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