# Issues: Trying to return something so that multiplots can be made with the value from these functions but I'm struggling...

import numpy as np
import rasterio
from matplotlib import pyplot as plt
from matplotlib import rc

def set_style():
    plt.style.use('bmh')
    font = {'family': 'Tahoma',
            'weight': 'ultralight',
            'size': 10}
    rc('font', **font)

def plot_raster(raster, band, cmap, save_path, dpi, v_range, title, obs):
    set_style()

    with rasterio.open(raster) as ras:

        arr = ras.read(band)

        arr[arr == -999] = np.nan

        if v_range is None:
            v_range = (np.nanmin(arr), np.nanmax(arr))

        sh = np.shape(arr)
        fig_w = round(8/(sh[0]/sh[1]))*1.5

        fig, ax = plt.subplots(figsize=(fig_w, 8))

        img = ax.imshow(arr, vmin=v_range[0], vmax=v_range[1], cmap=cmap,
                        extent=(ras.bounds[0], ras.bounds[2], ras.bounds[1], ras.bounds[3]))

        if ras.crs.linear_units == 'metre':
            units = 'm'
        elif ras.crs.linear_units == 'centimetre':
            units = 'cm'
        elif ras.crs.linear_units == 'kilometre':
            units = 'km'
        else:
            units = ras.crs.linear_units

        fig.colorbar(img, ax=ax, label='{0} ({1})'.format(obs, units))
        plt.title(title)

        ax.set_facecolor('0.8')

        # steps = (ras.bounds[2] - ras.bounds[0])/3.5
        # plt.xticks(np.arange(ras.bounds[0], ras.bounds[2], step=steps))
        plt.show()

        if save_path is not None:
            fig.savefig(fname=save_path, dpi=dpi, format='jpg')


def plot_hist(raster, band, v_range, n_bins, colour, density, title, xlabel, save_path, dpi):
    set_style()

    with rasterio.open(raster) as ras:
        arr = ras.read(band)

        arr[arr == -999] = np.nan

        if v_range is None:
            v_range = (np.nanmin(arr), np.nanmax(arr))

        fig, ax = plt.subplots(figsize=(8, 7))

        img = ax.hist(x=arr[~np.isnan(arr)].flatten(), bins=n_bins, color=colour, histtype='bar',
                range=v_range, density=density, edgecolor='black', linewidth=0.8)
        plt.title(title)

        if ras.crs.linear_units == 'metre':
            units = 'm'
        elif ras.crs.linear_units == 'centimetre':
            units = 'cm'
        elif ras.crs.linear_units == 'kilometre':
            units = 'km'
        else:
            units = ras.crs.linear_units

        plt.xlabel('{0} ({1})'.format(xlabel, units))

        if save_path is not None:
            plt.savefig(fname=save_path, dpi=dpi, format='jpg')

        plt.show()


def plot_dsm(dsm_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'BrBG')
    title = kwargs.get('title', 'Digital Surface Model')
    v_range = kwargs.get('v_range', None)
    colmap_label = kwargs.get('colmap_label', 'Elevation')

    plot_raster(raster=dsm_path, band=1, cmap=cmap, save_path=save_path, dpi=dpi, v_range=v_range, title=title,
                obs=colmap_label)


def plot_roughness(dsm_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'magma')
    title = kwargs.get('title', 'Rasterisation-Uncertainty Map')
    v_range = kwargs.get('v_range', None)
    colmap_label = kwargs.get('colmap_label', 'Rasterisation Uncertainty')

    plot_raster(raster=dsm_path, band=2, cmap=cmap, save_path=save_path, dpi=dpi, v_range=v_range, title=title,
                obs=colmap_label)

def plot_precision(prec_map_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'cividis')
    fill_gaps = kwargs.get('fill_gaps', True)
    title = kwargs.get('title', 'SFM Precision Map')
    v_range = kwargs.get('v_range', None)
    colmap_label = kwargs.get('colmap_label', 'SFM Precision')

    if fill_gaps is not True or False:
        raise InputError("fill_gaps must be a Boolean value. default is True")
    elif fill_gaps is True:
        rband = 1
    else:
        rband = 2

    plot_raster(raster=prec_map_path, band=rband, cmap=cmap, save_path=save_path, dpi=dpi, v_range=v_range, title=title,
                obs=colmap_label)


def plot_dem_of_diff(dem_o_diff_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'RdBu')
    title = kwargs.get('title', 'Elevation Change Map')
    v_range = kwargs.get('v_range', None)
    colmap_label = kwargs.get('colmap_label', 'Elevation Change')

    plot_raster(raster=dem_o_diff_path, band=1, cmap=cmap, save_path=save_path, dpi=dpi, v_range=v_range, title=title,
                obs=colmap_label)


def plot_lod(dem_o_diff_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'summer')
    title = kwargs.get('title', 'Limit of detection Map')
    v_range = kwargs.get('v_range', None)
    colmap_label = kwargs.get('colmap_label', 'Limit of Detection')

    plot_raster(raster=dem_o_diff_path, band=2, cmap=cmap, save_path=save_path, dpi=dpi, v_range=v_range, title=title,
                obs=colmap_label)


def hist_dsm(dsm_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    colour = kwargs.get('colour', 'green')
    n_bins = kwargs.get('n_bins', None)
    density = kwargs.get('density', False)
    title = kwargs.get('title', 'Digital Surface Model Histogram')
    xlabel = kwargs.get('x_label', 'Elevation')

    vrange = kwargs.get('range', None)

    plot_hist(raster=dsm_path, band=1, v_range=vrange, n_bins=n_bins, colour=colour,
              density=density, title=title, xlabel=xlabel, save_path=save_path, dpi=dpi)


def hist_roughness(dsm_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    colour = kwargs.get('colour', 'red')
    n_bins = kwargs.get('n_bins', None)
    density = kwargs.get('density', False)
    title = kwargs.get('title', 'Surface roughness Histogram')
    xlabel = kwargs.get('x_label', 'Rasterisation Uncertainty')

    vrange = kwargs.get('range', None)

    plot_hist(raster=dsm_path, band=2, v_range=vrange, n_bins=n_bins, colour=colour,
              density=density, title=title, xlabel=xlabel, save_path=save_path, dpi=dpi)


def hist_precision(ppc_path, **kwargs):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    colour = kwargs.get('colour', 'cyan')
    n_bins = kwargs.get('n_bins', None)
    density = kwargs.get('density', False)
    title = kwargs.get('title', 'SFM Precision Histogram')
    dimension = kwargs.get('dimension', 'z')
    xlabel = kwargs.get('x_label', '{0} Precision'.format(dimension))

    ppc_arr = np.loadtxt(fname=ppc_path, skiprows=1)
    if dimension == 'z':
        ppc_arr = ppc_arr[:, 5]
    elif dimension == 'x':
        ppc_arr = ppc_arr[:, 3]
    elif dimension == 'y':
        ppc_arr = ppc_arr[:, 4]
    elif dimension == 'xyz':
        ppc_arr = ppc_arr[:, 3:6]
        ppc_arr = ppc_arr[~np.isnan(ppc_arr)].flatten()
    else:
        raise(InputError("If dimension is provided it must be one of:\n"
                         "'x', 'y', 'z' or 'xyz'"))

    vrange = kwargs.get('range', (np.nanmin(ppc_arr), np.nanmax(ppc_arr)))

    fig, ax = plt.subplots(figsize=(8, 7))

    ax.hist(x=ppc_arr, bins=n_bins, color=colour, histtype='bar',
             range=vrange, density=density, edgecolor='black', linewidth=0.8)
    plt.title(title)
    plt.xlabel(xlabel)

    plt.show()

    if save_path is not None:
        plt.savefig(fname=save_path, dpi=dpi, format='jpg')



def hist_dem_of_diff(dem_o_diff_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    colour = kwargs.get('colour', 'magenta')
    n_bins = kwargs.get('n_bins', None)
    density = kwargs.get('density', False)
    title = kwargs.get('title', 'DEM of Difference Histogram')
    xlabel = kwargs.get('x_label', 'Elevation change')

    vrange = kwargs.get('range', None)

    plot_hist(raster=dem_o_diff_path, band=1, v_range=vrange, n_bins=n_bins, colour=colour,
              density=density, title=title, xlabel=xlabel, save_path=save_path, dpi=dpi)


def hist_lod(dem_o_diff_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    colour = kwargs.get('colour', 'blue')
    n_bins = kwargs.get('n_bins', None)
    density = kwargs.get('density', False)
    title = kwargs.get('title', 'Limit of Detection Histogram')
    xlabel = kwargs.get('x_label', 'Limit of Detection')

    vrange = kwargs.get('range', None)

    plot_hist(raster=dem_o_diff_path, band=2, v_range=vrange, n_bins=n_bins, colour=colour,
              density=density, title=title, xlabel=xlabel, save_path=save_path, dpi=dpi)


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message