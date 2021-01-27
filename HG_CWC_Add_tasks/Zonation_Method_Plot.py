import os
import geopandas as gpd
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import colors
import pandas as pd

def set_style():
    plt.style.use('bmh')
    font = {'family': 'Tahoma',
            'weight': 'ultralight',
            'size': 10}
    rc('font', **font)


def create_plot(BeaverZones_out, site_grid, feed_signs, figure_save):
    print('Generating zonation method plot...')

    BeaverZones_out = gpd.read_file(BeaverZones_out)
    BeaverZones_out['Name'] = ['Foraging Observed' if x == 1 else 'No Foraging' for
                                      x in BeaverZones_out['signs_YN']]
    BeaverZones_out = BeaverZones_out[['geometry', 'Name']]
    site_grid = gpd.read_file(site_grid)
    site_grid['Name'] = '20m Grid'
    feed_signs = gpd.read_file(feed_signs)
    feed_signs['Name'] = 'Feeding signs'
    feed_signs= feed_signs[['geometry', 'Name']]

    merge_gdf = pd.concat([BeaverZones_out, site_grid, feed_signs, ])

    # set matplotlib style...
    set_style()

    # build plot
    beaver_z_cmap = colors.ListedColormap(['none', '#C70039', '#60C84E', '#AC4EC8'])

    fig, ax = plt.subplots(1, 1, sharey=True, sharex=True, figsize=(4.5, 9))
    ax.grid(False)
    ax.set_facecolor('none')
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])

    merge_gdf.plot(ax=ax, cmap=beaver_z_cmap, column='Name', legend=True,
                   edgecolor='black')

    plt.show()

    fig.savefig(fname=figure_save, dpi=300, format='jpg')


if __name__ == '__main__':
    create_plot(BeaverZones_out=os.path.abspath('C:/HG_Projects/CWC_Drone_work/CHM/Beaver_Zones20m.gpkg'),
                site_grid=os.path.abspath('C:/HG_Projects/CWC_Drone_work/ZoneMethodPlot_data/'
                                          'grid_20m.gpkg'),
                feed_signs=os.path.abspath('C:/HG_Projects/CWC_Drone_work/shp_files/Feed_signs_All.gpkg'),
                figure_save=os.path.abspath('C:/HG_Projects/CWC_Drone_work/maps/Zone_method.jpg')
                )
