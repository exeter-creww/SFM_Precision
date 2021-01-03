import os
import numpy as np
import sfm_gridz
import sfm_gridz.plot_gridz as pcplot
import rasterio
from rasterio.plot import show_hist
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v4")

dsm1612 = os.path.join(out_ras_home, "dsm1.tif")
dsm1702 = os.path.join(out_ras_home, "dsm2.tif")
dsm1709 = os.path.join(out_ras_home, "dsm3.tif")
dsm1801 = os.path.join(out_ras_home, "dsm4.tif")
dsm1803 = os.path.join(out_ras_home, "dsm5.tif")
dsm1809 = os.path.join(out_ras_home, "dsm6.tif")

chm1612 = os.path.join(out_ras_home, "chm1.tif")
chm1702 = os.path.join(out_ras_home, "chm2.tif")
chm1709 = os.path.join(out_ras_home, "chm3.tif")
chm1801 = os.path.join(out_ras_home, "chm4.tif")
chm1803 = os.path.join(out_ras_home, "chm5.tif")
chm1809 = os.path.join(out_ras_home, "chm6.tif")

pcp1612 = os.path.join(out_ras_home, "pcc1.tif")
pcp1702 = os.path.join(out_ras_home, "pcc2.tif")
pcp1709 = os.path.join(out_ras_home, "pcc3.tif")
pcp1801 = os.path.join(out_ras_home, "pcc4.tif")
pcp1803 = os.path.join(out_ras_home, "pcc5.tif")
pcp1809 = os.path.join(out_ras_home, "pcc6.tif")

# Outputs
DOD_Dec16_Feb17 = os.path.join(out_ras_home, "DOD_Dec16_Feb17.tif")
DoD_Dec16_Jan18 = os.path.join(out_ras_home, "DoD_Dec16_Jan18.tif")
DoD_Dec16_Mar18 = os.path.join(out_ras_home, "DoD_Dec16_Mar18.tif")

DOD_Feb17_Jan18 = os.path.join(out_ras_home, "DOD_Feb17_Jan18.tif")
DOD_Feb17_March18 = os.path.join(out_ras_home, "DOD_Feb17_March18.tif")

DOD_Jan18_March18 = os.path.join(out_ras_home, "DOD_Jan18_March18.tif")

DoD_Sep17_Sep18 = os.path.join(out_ras_home, "DoD_Sep17_Sep18.tif")


for i in [DoD_Dec16_Mar18, DoD_Sep17_Sep18]:
    if os.path.isfile(i):
        os.remove(i)

epsg_code = 27700
mask_shp = os.path.abspath('C:/HG_Projects/CWC_Drone_work/shp_files/CWC_AOI_V2.shp')
beaver_zones = os.path.abspath('C:/HG_Projects/CWC_Drone_work/CHM/Beaver_Zones20m.gpkg')
import geopandas as gpd
gdf = gpd.read_file(beaver_zones)
gdf['Beaver_Zone'] = ['Foraging Observed' if x == 1 else 'No Foraging' for x in gdf['signs_YN']]
def run_functions():
    # Start - Finish (SUMMER)
    Sep17_Sep18 = sfm_gridz.difference(raster_1=chm1709, raster_2=chm1809,
                                       prec_point_cloud_1=pcp1709, prec_point_cloud_2=pcp1809,
                                       out_ras=DoD_Sep17_Sep18, epsg=epsg_code, mask=mask_shp)
    # Start - Finish (Winter)
    Dec16_Jan18 = sfm_gridz.difference(raster_1=chm1612, raster_2=chm1801,
                                       prec_point_cloud_1=pcp1612, prec_point_cloud_2=pcp1801,
                                       out_ras=DoD_Dec16_Jan18, epsg=epsg_code, mask=mask_shp)


    # Combined DEM of Diff plots - Winter & summer
    pcplot.set_style()

    beaver_z_cmap = LinearSegmentedColormap.from_list(
            'mycmap', [(0, '#60C84E'), (1, '#AC4EC8')])
    fig, axs = plt.subplots(1, 2, sharey=True, figsize=(9, 9))

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    pcplot.plot_dem_of_diff(Dec16_Jan18.ras_out_path, v_range=(-5, 5), title="Dec 2016 - Jan 2018",
                            mpl_fig=fig, mpl_ax=axs[0], legend=False, gpd_gdf=gdf, gdf_column='Beaver_Zone',
                            gdf_cmap=beaver_z_cmap, gdf_legend_kwds=({'loc': 'upper left'}), cmap='coolwarm_r')

    pcplot.plot_dem_of_diff(Sep17_Sep18.ras_out_path, v_range=(-5, 5), title="Sep 2017 - Sep 2018",
                            mpl_fig=fig, mpl_ax=axs[1], gpd_gdf=gdf, gdf_column='Beaver_Zone',
                            gdf_cmap=beaver_z_cmap, gdf_legend=False, cmap='coolwarm_r')


    plt.show()

    fig.savefig(fname='C:/HG_Projects/CWC_Drone_work/maps/DEMofDiff.jpg', dpi=300, format='jpg')


    # LOD plots

    fig, axs = plt.subplots(1, 2, sharey=True, figsize=(9, 9))
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])

    pcplot.plot_lod(Dec16_Jan18.ras_out_path, title="Dec 2016 - Jan 2018", v_range=(0, 15),
                            mpl_fig=fig, mpl_ax=axs[0], legend=False)
    pcplot.plot_lod(Sep17_Sep18.ras_out_path, title="Sep 2017 - Sep 2018", v_range=(0, 15),
                            mpl_fig=fig, mpl_ax=axs[1])


    plt.show()

    fig.savefig(fname='C:/HG_Projects/CWC_Drone_work/maps/LoD.jpg', dpi=300, format='jpg')

    fig, axs = plt.subplots(2, 4, sharey=True, sharex=True, figsize=(13, 13))
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])

    ts_names = ['Dec 16', 'Jan 18', 'Sep 17', 'Sep 18']
    dsm_list = [dsm1612, dsm1801, dsm1709, dsm1809]
    chm_list = [chm1612, chm1801, chm1709, chm1809]
    pcp_list = [pcp1612, pcp1801, pcp1709, pcp1809]

    for idx, path, name in zip(range(0,4), dsm_list, ts_names):
        if idx == 3:
            pcplot.plot_dsm(dsm_path=path, title=name, v_range=(75, 110), mpl_fig=fig, mpl_ax=axs[0, idx])
        else:
            pcplot.plot_dsm(dsm_path=path, title=name, legend=None, v_range=(75, 110),
                            mpl_fig=fig, mpl_ax=axs[0, idx])

    for idx, path in enumerate(chm_list):
        if idx == 3:
            pcplot.plot_chm(chm_path=path, title=None, v_range=(0, 25),
                             mpl_fig=fig, mpl_ax=axs[1, idx])
        else:
            pcplot.plot_chm(chm_path=path, title=None, legend=None,v_range=(0, 25),
                            mpl_fig=fig, mpl_ax=axs[1, idx])

    plt.show()
    fig.savefig(fname='C:/HG_Projects/CWC_Drone_work/maps/DSM_CHM.jpg', dpi=300, format='jpg')

    fig, axs = plt.subplots(2, 4, sharey=True, sharex=True, figsize=(13, 13))
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])


    for idx, path in enumerate(pcp_list):
        if idx == 3:
            pcplot.plot_precision(prec_map_path=path, title=None, v_range=(0, 0.1),
                             mpl_fig=fig, mpl_ax=axs[0, idx])
        else:
            pcplot.plot_precision(prec_map_path=path, title=None, legend=None, v_range=(0, 0.1),
                            mpl_fig=fig, mpl_ax=axs[0, idx])

    for idx, path in enumerate(dsm_list):
        if idx == 3:
            pcplot.plot_roughness(dsm_path=path, title=None, v_range=(0, 10),
                             mpl_fig=fig, mpl_ax=axs[1, idx])
        else:
            pcplot.plot_roughness(dsm_path=path, title=None, legend=None, v_range=(0, 10),
                            mpl_fig=fig, mpl_ax=axs[1, idx])

    plt.show()

    fig.savefig(fname='C:/HG_Projects/CWC_Drone_work/maps/PREC_ROUGH.jpg', dpi=300, format='jpg')

    # Plot Terrain Model
    fig, ax = plt.subplots(1, 1, sharey=True, sharex=True, figsize=(4.5, 9))
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    pcplot.plot_dtm(chm_path=chm1809, title=None, save_path='C:/HG_Projects/CWC_Drone_work/maps/DTM.jpg',
                    mpl_fig=fig, mpl_ax=ax)
    plt.show()


if __name__ == '__main__':
    run_functions()
