from PointCloudStat.precision_map import precision_map
from PointCloudStat.DSM import height_map
from PointCloudStat.dem_of_diff import dem_of_diff

import os
import rasterio
from rasterio.plot import show


dpc_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/17_02_15_Danes_Mill/17_02_15_Exports/"
                           "CWC_examplePC_clip.laz")

pcp_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                              "18_09_25_DanesCroft_SFM_PREC/18_09_25_DanesCroft_Prec_Cloud.txt")
out_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                          "18_09_25_DanesCroft_SFM_PREC/Testing_New_Module/test_raster.tif")
dsm_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/18_09_25_Danes_Mill/"
                          "18_09_25_DanesCroft_SFM_PREC/Testing_New_Module/test_dsm.tif")

def main():
    epsg_code = 27700
    prras = precision_map(prec_point_cloud=pcp_path, out_raster=out_path, resolution=1, prec_dimension='zerr')

    with rasterio.open(prras.path) as p_map:
        show(p_map, cmap='viridis')


    # finest_res = ras.min_res
    #     # print(finest_res)
    #     #
    #     # chosen_res = myround(finest_res)

    dsm = height_map(point_cloud=dpc_path, out_raster=dsm_path, resolution=0.5, window_size=10)

    with rasterio.open(dsm.path) as h_map:
        show(h_map, cmap='twilight_shifted')


    demod = dem_of_diff(raster_1=prras.path, raster_2=dsm.path, epsg=epsg_code)


def myround(x, base=0.05):
    return base * round(x/base)


if __name__ == '__main__':
    main()






print("done")