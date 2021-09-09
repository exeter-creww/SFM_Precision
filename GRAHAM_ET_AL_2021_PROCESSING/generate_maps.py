import os
import numpy as np
import sfm_gridz
import sfm_gridz.plot_gridz as pcplot
import rasterio
from rasterio.plot import show_hist
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import geopandas as gpd

out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v5")

dsm1612 = os.path.join(out_ras_home, "dsm1.tif")
dsm1709 = os.path.join(out_ras_home, "dsm3.tif")
dsm1801 = os.path.join(out_ras_home, "dsm4.tif")
dsm1809 = os.path.join(out_ras_home, "dsm6.tif")

chm1612 = os.path.join(out_ras_home, "chm1.tif")
chm1709 = os.path.join(out_ras_home, "chm3.tif")
chm1801 = os.path.join(out_ras_home, "chm4.tif")
chm1809 = os.path.join(out_ras_home, "chm6.tif")

pcp1612 = os.path.join(out_ras_home, "pcc1.tif")
pcp1709 = os.path.join(out_ras_home, "pcc3.tif")
pcp1801 = os.path.join(out_ras_home, "pcc4.tif")
pcp1809 = os.path.join(out_ras_home, "pcc6.tif")

dod_winter_thresh = os.path.join(out_ras_home, "DoD_Dec16_Jan18_threshold.tif")
dod_winter_weight = os.path.join(out_ras_home, "DoD_Dec16_Jan18_weight.tif")
dod_summer_thresh = os.path.join(out_ras_home, "DoD_Sep17_Sep18_threshold.tif")
dod_summer_weight = os.path.join(out_ras_home, "DoD_Sep17_Sep18_weight.tif")

epsg_code = 27700

mask_shp = os.path.abspath('C:/HG_Projects/CWC_Drone_work/shp_files/CWC_AOI_V2.shp')

beaver_zones = os.path.abspath('C:/HG_Projects/CWC_Drone_work/CHM/Beaver_Zones20m.gpkg')

gdf = gpd.read_file(beaver_zones)
gdf['Beaver_Zone'] = ['Foraging Observed' if x == 1 else 'No Foraging' for x in gdf['signs_YN']]
def run_functions():


    # Combined DEM of Diff plots - Winter & summer
    pcplot.set_style()

    def dod_multiplot(dod1, dod2, save_path):
        beaver_z_cmap = LinearSegmentedColormap.from_list(
                'mycmap', [(0, '#000000'), (1, '#000000')])
        fig, axs = plt.subplots(1, 3, sharey=True, figsize=(9.5, 7))

        plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
        pcplot.plot_dem_of_diff(dod1, v_range=(-4, 4), title="No LoD",
                                mpl_fig=fig, mpl_ax=axs[0], legend=False, gpd_gdf=gdf, gdf_column='Beaver_Zone',
                                gdf_cmap=beaver_z_cmap, gdf_legend_kwds=({'loc': 'upper left'}), cmap='seismic_r',
                                method='basic', linestyle=['-', ':'])

        pcplot.plot_dem_of_diff(dod2, v_range=(-4, 4), title="Weighted LoD95",
                                mpl_fig=fig, mpl_ax=axs[1], legend=False, gpd_gdf=gdf, gdf_column='Beaver_Zone',
                                gdf_cmap=beaver_z_cmap, gdf_legend=False, cmap='seismic_r', linestyle=['-', ':'])

        pcplot.plot_dem_of_diff(dod1, v_range=(-4, 4), title="LoDmin threshold",
                                mpl_fig=fig, mpl_ax=axs[2], gpd_gdf=gdf, gdf_column='Beaver_Zone',
                                gdf_cmap=beaver_z_cmap, gdf_legend=False, cmap='seismic_r', linestyle=['-', ':'])

        plt.show()

        fig.savefig(fname=save_path, dpi=300, format='png')

    # winter DoD maps
    dod_multiplot(dod_winter_thresh, dod_winter_weight, 'C:/HG_Projects/CWC_Drone_work/maps/DEMofDiff_winter.png')

    # summer DoD maps
    dod_multiplot(dod_summer_thresh, dod_summer_weight, 'C:/HG_Projects/CWC_Drone_work/maps/DEMofDiff_summer.png')

    # LOD plots

    def gen_lod_map(lod_ras, save_path):
        fig, ax = plt.subplots(1, 1, sharey=True, sharex=True, figsize=(3.5, 7))
        plt.tight_layout(rect=[0.05, 0, 0.97, 1])

        pcplot.plot_lod(lod_ras, title=None, v_range=(0, 10),
                                mpl_fig=fig, mpl_ax=ax, cmap='Oranges')

        plt.show()

        fig.savefig(fname=save_path, dpi=300, format='png')

    # winter LoD
    gen_lod_map(dod_winter_thresh, 'C:/HG_Projects/CWC_Drone_work/maps/WinterLoD.png')
    gen_lod_map(dod_summer_thresh, 'C:/HG_Projects/CWC_Drone_work/maps/SummerLoD.png')


    # define lists for multiplots.

    ts_names_wint = ['Dec 16', 'Jan 18']
    ts_names_summ = ['Sep 17', 'Sep 18']
    dsm_list_wint = [dsm1612, dsm1801]
    dsm_list_summ = [dsm1709, dsm1809]
    chm_list_wint = [chm1612, chm1801]
    chm_list_summ = [chm1709, chm1809]
    pcp_list_wint = [pcp1612, pcp1801]
    pcp_list_summ = [pcp1709, pcp1809]

    def dem_panel(dem_list, ts_names, save_path, map_type):

        if map_type == 'dsm':
            cp = 'bone'
            scale_range = (75, 100)
            method = pcplot.plot_dsm
        else:
            cp = 'cubehelix_r'
            scale_range = (0, 20)
            method = pcplot.plot_chm

        fig, axs = plt.subplots(1, 2, sharey=True, sharex=True,  figsize=(7, 7))
        plt.tight_layout(rect=[0.02, 0.02, 0.96, 0.98])

        for idx, path, name in zip(range(0,2), dem_list, ts_names):
            if idx == 1:
                method(path, title=name, v_range=scale_range, mpl_fig=fig, mpl_ax=axs[1],
                                cmap=cp)
            else:
                method(path, title=name, legend=None, v_range=scale_range,
                                mpl_fig=fig, mpl_ax=axs[0], cmap=cp)

        plt.show()
        fig.savefig(fname=save_path, dpi=300, format='png')

        # winter dsm/chm

    dem_panel(dsm_list_wint, ts_names_wint, 'C:/HG_Projects/CWC_Drone_work/maps/DSM_winter.png', map_type='dsm')
    # summer dsm/chm
    dem_panel(dsm_list_summ, ts_names_summ, 'C:/HG_Projects/CWC_Drone_work/maps/DSM_summer.png', map_type='dsm')

    dem_panel(chm_list_wint, ts_names_wint, 'C:/HG_Projects/CWC_Drone_work/maps/CHM_winter.png', map_type='chm')
    # summer dsm/chm
    dem_panel(chm_list_summ, ts_names_summ, 'C:/HG_Projects/CWC_Drone_work/maps/CHM_summer.png', map_type='chm')




    def prec_rough_panel(pcp_list, dsm_list, ts_names, save_path):

        fig, axs = plt.subplots(2, 2, sharey=True, sharex=True, figsize=(5, 12))
        plt.tight_layout(rect=[0.09, 0.02, 1, 0.98])

        for idx, path, name in zip(range(0, 4), pcp_list, ts_names):

            if idx == 1:
                pcplot.plot_precision(prec_map_path=path, title=name, v_range=(0, 0.1),
                                 mpl_fig=fig, mpl_ax=axs[1, 0], cmap='viridis',
                                      leg_orient='horizontal',leg_pos='bottom', title_pos='left')
            else:
                pcplot.plot_precision(prec_map_path=path, title=name, legend=None, v_range=(0, 0.1),
                                mpl_fig=fig, mpl_ax=axs[0, 0], cmap='viridis', title_pos='left')

        for idx, path in enumerate(dsm_list):
            if idx == 1:
                pcplot.plot_roughness(dsm_path=path, title=None, v_range=(0, 10),
                                 mpl_fig=fig, mpl_ax=axs[1, 1], cmap='RdPu',
                                      leg_orient='horizontal', leg_pos='bottom')
            else:
                pcplot.plot_roughness(dsm_path=path, title=None, legend=None, v_range=(0, 10),
                                mpl_fig=fig, mpl_ax=axs[0, 1], cmap='RdPu')
        plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[])

        plt.show()

        fig.savefig(fname=save_path, dpi=300, format='png')

    # winter prec/rough panel
    prec_rough_panel(pcp_list_wint, dsm_list_wint, ts_names_wint,
                     'C:/HG_Projects/CWC_Drone_work/maps/PREC_ROUGH_winter.png')
    # summer prec/rough panel
    prec_rough_panel(pcp_list_summ, dsm_list_summ, ts_names_summ,
                     'C:/HG_Projects/CWC_Drone_work/maps/PREC_ROUGH_summer.png')

    # Plot Terrain Model
    fig, ax = plt.subplots(1, 1, sharey=True, sharex=True, figsize=(3.5, 7))
    plt.tight_layout(rect=[0.05, 0, 0.97, 1])
    pcplot.plot_dtm(chm_path=chm1809, title=None, save_path='C:/HG_Projects/CWC_Drone_work/maps/DTM.png',
                    mpl_fig=fig, mpl_ax=ax)
    plt.show()


if __name__ == '__main__':
    run_functions()
