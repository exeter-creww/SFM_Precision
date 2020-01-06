from PointCloudStat.precision_map import precision_map
from PointCloudStat.DSM import height_map
from PointCloudStat.dem_of_diff import dem_of_diff

import os
import rasterio
from rasterio.plot import show

import numpy as np

dpc_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_02_15_Danes_Mill/17_02_15_Exports/"
                           "CWC_examplePC_clip.laz")

pcp_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                              "18_09_25_DanesCroft_SFM_PREC/18_09_25_DanesCroft_Prec_Cloud.txt")
out_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                          "18_09_25_DanesCroft_SFM_PREC/Testing_New_Module/test_raster.tif")
dsm_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                          "18_09_25_DanesCroft_SFM_PREC/Testing_New_Module/test_dsm.tif")

dod_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                          "18_09_25_DanesCroft_SFM_PREC/Testing_New_Module/test_dod.tif")

def main():
    epsg_code = 27700

    dsm = height_map(point_cloud=dpc_path, out_raster=dsm_path, resolution=0.5, window_size=10, epsg=epsg_code)

    # with rasterio.open(dsm.path) as h_map:
    #     for i in range(1, 3):
    #         arr = h_map.read(i)
    #         arr[arr == -999] = np.nan
    #         show(arr, cmap='viridis')
    #     # print("pause")


    prras = precision_map(prec_point_cloud=pcp_path, out_raster=out_path, resolution=1,
                          prec_dimension='zerr', epsg=epsg_code, bounds=dsm.bounds)

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
    demod = dem_of_diff(raster_1=dsm.path, raster_2=dsm.path,
                        prec_point_cloud_1=prras.path, prec_point_cloud_2=prras.path,
                        out_ras=dod_path, epsg=epsg_code)

    with rasterio.open(demod.ras_out_path) as dod_map:
        # arr = p_map.read(1)
        # arr[arr == -999] = np.nan
        show(dod_map, cmap='viridis')




if __name__ == '__main__':
    main()






print("done")

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