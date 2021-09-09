# Compare the relative change of the different woodland zones.

import geopandas as gpd
import rasterio
from rasterio.mask import mask
import os
import json
import pandas as pd

# suppress warnings for now...
import warnings
warnings.filterwarnings("ignore")

home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_Anal_Exports/Rasters_v5") # where rasters have been stored.
shps_root = os.path.relpath("feed_data")
shrub_zones = os.path.relpath('int_files/Woodland_Zones20m.gpkg')

# Define DoD paths

DoD_Dec16_Jan18_Thresh = os.path.join(home, "DoD_Dec16_Jan18_threshold.tif")
DoD_Dec16_Jan18_Weight = os.path.join(home, "DoD_Dec16_Jan18_weight.tif")
DoD_Sep17_Sep18_Thresh = os.path.join(home, "DoD_Sep17_Sep18_threshold.tif")
DoD_Sep17_Sep18_Weight = os.path.join(home, "DoD_Sep17_Sep18_weight.tif")

# define CHM paths
chm1_Dec16 = os.path.join(home, "chm1.tif")
chm3_Sep17 = os.path.join(home, "chm3.tif")
chm4_Jan18 = os.path.join(home, "chm4.tif")
chm6_Sep18 = os.path.join(home, "chm6.tif")


# define feeding signs
feed_signs = os.path.join(shps_root, 'FS_1618.shp')

CWC_CanChange_df = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                "GRAHAM_ET_AL_2021_Analysis/data/CWC_can_change_df.csv")
CWC_CanHeight_df = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                "GRAHAM_ET_AL_2021_Analysis/data/CWC_can_height_df.csv")
# BeaverZones_out = os.path.abspath('C:/HG_Projects/CWC_Drone_work/CHM/Beaver_Zones20m.gpkg')

def main():
    print("running Zone-Compare pipeline")

    # Running for DODs
    Dec16Jan18_noLod = compare_zones(shrub_zones, DoD_Dec16_Jan18_Thresh, feed_signs,
                                     "Dec16 - Jan18", method='no lod', band=2)
    Dec16Jan18_thresh = compare_zones(shrub_zones, DoD_Dec16_Jan18_Thresh, feed_signs,
                                      "Dec16 - Jan18", method='threshold', band=0)
    Dec16Jan18_weight = compare_zones(shrub_zones, DoD_Dec16_Jan18_Weight, feed_signs,
                                      "Dec16 - Jan18", method='weighted', band=0)

    sep17sep18_noLod = compare_zones(shrub_zones, DoD_Sep17_Sep18_Thresh, feed_signs,
                                     "Sep17 - Sep18", method='no lod', band=2)
    sep17sep18_thresh = compare_zones(shrub_zones, DoD_Sep17_Sep18_Thresh, feed_signs,
                                      "Sep17 - Sep18", method='threshold', band=0)
    sep17sep18_weight = compare_zones(shrub_zones, DoD_Sep17_Sep18_Weight, feed_signs,
                                      "Sep17 - Sep18", method='weighted', band=0)

    dfconcat = pd.concat([Dec16Jan18_noLod, Dec16Jan18_thresh, Dec16Jan18_weight,
                          sep17sep18_noLod, sep17sep18_thresh, sep17sep18_weight])

    dfconcat.to_csv(CWC_CanChange_df, na_rep='NA', index=False)

    # and now for CHMs

    Dec16_CHM_df = compare_zones(shrub_zones, chm1_Dec16, feed_signs, "Dec16", method='canopy height', band=0,
                                 model_type='canopy_height')
    Sep17_CHM_df = compare_zones(shrub_zones, chm3_Sep17, feed_signs, "Sep17", method='canopy height', band=0,
                                 model_type='canopy_height')
    Jan18_CHM_df = compare_zones(shrub_zones, chm4_Jan18, feed_signs, "Jan18", method='canopy height', band=0,
                                 model_type='canopy_height')
    Sep18_CHM_df = compare_zones(shrub_zones, chm6_Sep18, feed_signs, "Sep18", method='canopy height', band=0,
                                 model_type='canopy_height')

    chmconcat = pd.concat([Dec16_CHM_df, Jan18_CHM_df, Sep17_CHM_df, Sep18_CHM_df])

    chmconcat.to_csv(CWC_CanHeight_df, na_rep='NA', index=False)


def compare_zones(zones, diff_ras, feed_signs, name, method, band, **kwargs):
    model_type = kwargs.get('model_type', 'canopy_change')

    z_gdf = gpd.read_file(zones)
    z_gdf['id'] = z_gdf.index
    z_gdf['area'] = z_gdf.area

    fs_gdf = gpd.read_file(feed_signs)
    fs_gdf_buff = fs_gdf.copy()
    fs_gdf_buff.geometry = fs_gdf.geometry.buffer(10)

    beav_zone = get_union(z_gdf, fs_gdf_buff)
    beav_zone['signs_YN'] = 1
    beav_zone = beav_zone.dissolve(by='signs_YN')
    beav_zone = beav_zone.reset_index()

    no_beav_zone = gpd.overlay(z_gdf, beav_zone, how='symmetric_difference')
    no_beav_zone['signs_YN'] = 0
    no_beav_zone = no_beav_zone.dissolve(by='signs_YN')
    no_beav_zone = no_beav_zone.reset_index()

    # zones_comb = pd.concat([beav_zone, no_beav_zone])
    # ax = zones_comb.plot(column='signs_YN', colormap='Dark2', edgecolor='None')
    # fs_gdf.plot(color='red', ax=ax, markersize=8, alpha=0.3)
    # plt.title(name + ' beaver and non beaver zones')
    # plt.show()
    # zones_comb.to_file(BeaverZones_out, driver='GPKG')


    beav_zone_df = mask_ras_get_df(beav_zone, diff_ras, band=band, model=model_type)
    beav_zone_df['signs_YN'] = 1
    beav_zone_df['signs_YNf'] = 'Foraging Observed'

    no_beav_zone_df = mask_ras_get_df(no_beav_zone, diff_ras, band=band, model=model_type)
    no_beav_zone_df['signs_YN'] = 0
    no_beav_zone_df['signs_YNf'] = 'No Foraging'

    cwc_df = pd.concat([beav_zone_df, no_beav_zone_df])


    cwc_df['signs_YNf'] = cwc_df['signs_YNf'].astype('category')
    cwc_df['signs_YNf'] = cwc_df['signs_YNf'].cat.reorder_categories(['No Foraging', 'Foraging Observed'])

    cwc_df['time_step'] = name
    cwc_df['LoD_method'] = method
    return cwc_df

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


def get_union(to_select, union_shp):
    """Alternative union function"""
    union = gpd.GeoDataFrame(
        gpd.GeoSeries([union_shp.unary_union]),
        columns=['geometry'],
        crs=union_shp.crs)

    clip_gdf = gpd.sjoin(to_select, union, op='intersects')
    clip_gdf = clip_gdf.drop(columns=['index_right'])

    return clip_gdf


def mask_ras_get_df(gdf, ras, band, model):

        geom = getFeatures(gdf)  # returns geometries for AOIs

        with rasterio.open(ras) as src:
            out_image, out_transform = rasterio.mask.mask(src, geom, crop=True)
            res = src.res[0] * src.res[1]

        out_image_1d = out_image[band].flatten()
        out_image_1d = out_image_1d[out_image_1d != -999]

        # print('mean: {0}'.format(np.nanmean(out_image_1d)))
        # print('min: {0}'.format(np.nanmin(out_image_1d)))
        # print('max: {0}'.format(np.nanmax(out_image_1d)))
        # print('stdev: {0}'.format(np.nanstd(out_image_1d)))

        out_df = pd.DataFrame(out_image_1d, columns=[model])
        return out_df

if __name__ == '__main__':
    main()
