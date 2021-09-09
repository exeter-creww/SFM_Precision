import os
import sfm_gridz
import sfm_gridz.plot_gridz as pcplot
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import geopandas as gpd

# Define paths
# route folder
out_ras_home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v4")

# Winter CHMs
chm1612 = os.path.join(out_ras_home, "chm1.tif")
chm1801 = os.path.join(out_ras_home, "chm4.tif")

# Winter PMaps
pcp1612 = os.path.join(out_ras_home, "pcc1.tif")
pcp1801 = os.path.join(out_ras_home, "pcc4.tif")

# Late Summer CHMs
chm1709 = os.path.join(out_ras_home, "chm3.tif")
chm1809 = os.path.join(out_ras_home, "chm6.tif")

# Late Summer PMaps
pcp1709 = os.path.join(out_ras_home, "pcc3.tif")
pcp1809 = os.path.join(out_ras_home, "pcc6.tif")


#DoD out paths
DoD_Dec16_Jan18_NL = os.path.join(out_ras_home, "DoD_Dec16_Jan18_LoDweightb.tif")
DoD_Sep17_Sep18_NL = os.path.join(out_ras_home, "DoD_Sep17_Sep18_LoDweightb.tif")

epsg_code = 27700
mask_shp = os.path.abspath('C:/HG_Projects/CWC_Drone_work/shp_files/CWC_AOI_V2.shp')
beaver_zones = os.path.abspath('C:/HG_Projects/CWC_Drone_work/CHM/Beaver_Zones20m.gpkg')
gdf = gpd.read_file(beaver_zones)
gdf['Beaver_Zone'] = ['Foraging Observed' if x == 1 else 'No Foraging' for x in gdf['signs_YN']]

def dod_no_lod():
    print('run DoD with no LoD')

    # Start - Finish (SUMMER)
    Sep17_Sep18 = sfm_gridz.difference(raster_1=chm1709, raster_2=chm1809,
                                       prec_point_cloud_1=pcp1709, prec_point_cloud_2=pcp1809,
                                       out_ras=DoD_Sep17_Sep18_NL, epsg=epsg_code, mask=mask_shp)
    # Start - Finish (Winter)
    Dec16_Jan18 = sfm_gridz.difference(raster_1=chm1612, raster_2=chm1801,
                                       prec_point_cloud_1=pcp1612, prec_point_cloud_2=pcp1801,
                                       out_ras=DoD_Dec16_Jan18_NL, epsg=epsg_code, mask=mask_shp)

    pcplot.set_style()

    beaver_z_cmap = LinearSegmentedColormap.from_list(
            'mycmap', [(0, '#60C84E'), (1, '#AC4EC8')])
    fig, axs = plt.subplots(1, 2, sharey=True, figsize=(9, 9))

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    pcplot.plot_dem_of_diff(Dec16_Jan18.ras_out_path, v_range=(-5, 5), title="Dec 2016 - Jan 2018",
                            mpl_fig=fig, mpl_ax=axs[0], legend=False, gpd_gdf=gdf, gdf_column='Beaver_Zone',
                            gdf_cmap=beaver_z_cmap, gdf_legend_kwds=({'loc': 'upper left'}), cmap='bwr_r',
                            method='robust')

    pcplot.plot_dem_of_diff(Sep17_Sep18.ras_out_path, v_range=(-5, 5), title="Sep 2017 - Sep 2018",
                            mpl_fig=fig, mpl_ax=axs[1], gpd_gdf=gdf, gdf_column='Beaver_Zone',
                            gdf_cmap=beaver_z_cmap, gdf_legend=False, cmap='bwr_r', method='robust')

    plt.show()

    fig.savefig(fname='C:/HG_Projects/CWC_Drone_work/maps/DEMofDiff_LoDweight.jpg', dpi=300, format='jpg')


if __name__ == '__main__':
    dod_no_lod()
