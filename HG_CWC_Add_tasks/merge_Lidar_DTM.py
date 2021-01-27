# Import Raw Lidar layers - merge and clip to extent. resample and align with Sep17 DSM.
# Create Canopy height model from DSM and DTM.
# Identify canopy >2m and classify
# create polygon of woodland area.

import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import os
from glob import glob

# --- Inputs ---
home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v3")
dsm_path = os.path.join(home, "dsm3.tif") # used to set correct extent

raw_dtm_folder = os.path.abspath('C:/HG_Projects/CWC_Drone_work/DTM/Download_1462811/england-dtm-2m_3439972/st')
dtm_out_path = os.path.abspath('C:/HG_Projects/CWC_Drone_work/DTM/Lidar_mosaic/CWC_Lidar_DTM.tif')

def main():

    asc_files = glob(os.path.join(raw_dtm_folder, '*.asc'))

    src_files_to_mosaic = []
    for asc in asc_files:
        src = rasterio.open(asc)
        src_files_to_mosaic.append(src)

    mosaic, out_trans = merge(src_files_to_mosaic)

    with rasterio.open(dsm_path) as src:
        loc_crs = src.crs
        # show(src.read(1, masked=True), cmap='terrain', transform=src.transform)

    with rasterio.open(dtm_out_path, 'w+', count=1, dtype='float32', driver='GTiff', transform=out_trans,
                      height=mosaic.shape[-2], width=mosaic.shape[-1]) as dataset:
        dataset.crs = loc_crs
        dataset.write(mosaic)

        show(dataset.read(1, masked=True), cmap='magma', transform=src.transform)


if __name__ == '__main__':
    main()
