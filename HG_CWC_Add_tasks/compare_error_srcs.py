
import rasterio
import os
import numpy as np
ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v5")
pcp1709 = os.path.join(ras_home, "pcc3.tif")
pcp1809 = os.path.join(ras_home, "pcc6.tif")

dsm1709 = os.path.join(ras_home, "dsm3.tif")
dsm1809 = os.path.join(ras_home, "dsm6.tif")

def run_functions():
    print('read files')
    pcp1709_ras = rasterio.open(pcp1709)
    pcp1809_ras = rasterio.open(pcp1809)
    dsm1709_ras = rasterio.open(dsm1709)
    dsm1809_ras = rasterio.open(dsm1809)

    pcp1709_arr = pcp1709_ras.read()[pcp1709_ras.read() != -999]
    dsm1709_arr = dsm1709_ras.read(2)[dsm1709_ras.read(2) != -999]

    print(np.mean(pcp1709_arr))
    print(np.mean(dsm1709_arr))
    print(np.std(pcp1709_arr))
    print(np.std(dsm1709_arr))

    pcp1809_arr = pcp1809_ras.read()[pcp1809_ras.read() != -999]
    dsm1809_arr = dsm1809_ras.read(2)[dsm1809_ras.read(2) != -999]

    print(np.round((np.mean(pcp1809_arr) + np.mean(pcp1709_arr))/2, 3))
    print(np.round((np.std(pcp1809_arr) + np.std(pcp1709_arr))/2, 3))

    print(np.round((np.mean(dsm1809_arr) + np.mean(dsm1709_arr))/2, 3))
    print(np.round((np.std(dsm1809_arr) + np.std(dsm1709_arr))/2, 3))

    #n times larger?
    print(np.round((np.mean(dsm1809_arr) + np.mean(dsm1709_arr)) / 2, 3) /
          np.round((np.mean(pcp1809_arr) + np.mean(pcp1709_arr))/2, 3))


if __name__ == '__main__':
    run_functions()

