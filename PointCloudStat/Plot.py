import numpy as np
import rasterio
from matplotlib import pyplot as plt


def plot_dsm(dsm_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'BrBG')

    with rasterio.open(dsm_path) as dod1:

        arr = dod1.read(1)

        arr[arr == -999] = np.nan

        v_range = kwargs.get('v_range', (np.nanmin(arr), np.nanmax(arr)))

        fig, ax = plt.subplots(figsize=(8, 8))

        img = ax.imshow(arr, vmin=v_range[0], vmax=v_range[1], cmap=cmap,
                        extent=(dod1.bounds[0], dod1.bounds[2], dod1.bounds[1], dod1.bounds[3]))


        fig.colorbar(img, ax=ax)

        plt.show()

        if save_path is not None:
            fig.savefig(fname=save_path, dpi=dpi, format='jpg')


def plot_roughness(dsm_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'magma')

    with rasterio.open(dsm_path) as dod1:

        arr = dod1.read(2)

        arr[arr == -999] = np.nan

        v_range = kwargs.get('v_range', (np.nanmin(arr), np.nanmax(arr)))

        fig, ax = plt.subplots(figsize=(8, 8))

        img = ax.imshow(arr, vmin=v_range[0], vmax=v_range[1], cmap=cmap,
                        extent=(dod1.bounds[0], dod1.bounds[2], dod1.bounds[1], dod1.bounds[3]))


        fig.colorbar(img, ax=ax)

        plt.show()

        if save_path is not None:
            fig.savefig(fname=save_path, dpi=dpi, format='jpg')

def plot_precision(prec_map_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'cividis')
    fill_gaps = kwargs.get('fill_gaps', True)


    print("plot DSM")

    with rasterio.open(prec_map_path) as dod1:

        if fill_gaps is True:
            arr = dod1.read(1)
        else:
            arr = dod1.read(2)

        arr[arr == -999] = np.nan

        v_range = kwargs.get('v_range', (np.nanmin(arr), np.nanmax(arr)))

        fig, ax = plt.subplots(figsize=(8, 8))

        img = ax.imshow(arr, vmin=v_range[0], vmax=v_range[1], cmap=cmap,
                        extent=(dod1.bounds[0], dod1.bounds[2], dod1.bounds[1], dod1.bounds[3]))

        fig.colorbar(img, ax=ax)

        plt.show()

        if save_path is not None:
            fig.savefig(fname=save_path, dpi=dpi, format='jpg')

def plot_dem_of_diff(dem_o_diff_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'RdBu')


    print("plot DSM")

    with rasterio.open(dem_o_diff_path) as dod1:

        arr = dod1.read(1)

        arr[arr == -999] = np.nan

        v_range = kwargs.get('v_range', (np.nanmin(arr), np.nanmax(arr)))

        fig, ax = plt.subplots(figsize=(8, 8))

        img = ax.imshow(arr, vmin=v_range[0], vmax=v_range[1], cmap=cmap,
                        extent=(dod1.bounds[0], dod1.bounds[2], dod1.bounds[1], dod1.bounds[3]))


        fig.colorbar(img, ax=ax)

        plt.show()

        if save_path is not None:
            fig.savefig(fname=save_path, dpi=dpi, format='jpg')


def plot_lod(dem_o_diff_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    cmap = kwargs.get('cmap', 'summer')

    print("plot DSM")

    with rasterio.open(dem_o_diff_path) as dod1:

        arr = dod1.read(2)

        arr[arr == -999] = np.nan

        v_range = kwargs.get('v_range', (np.nanmin(arr), np.nanmax(arr)))

        fig, ax = plt.subplots(figsize=(8, 8))

        img = ax.imshow(arr, vmin=v_range[0], vmax=v_range[1], cmap=cmap,
                        extent=(dod1.bounds[0], dod1.bounds[2], dod1.bounds[1], dod1.bounds[3]))


        fig.colorbar(img, ax=ax)

        plt.show()

        if save_path is not None:
            fig.savefig(fname=save_path, dpi=dpi, format='jpg')


def hist_dsm(dsm_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    colour = kwargs.get('colour', 'green')
    n_bins = kwargs.get('n_bins', None)
    density = kwargs.get('density', False)
    title = kwargs.get('title', 'Digital Surface Model Histogram')
    xlabel = kwargs.get('x_label', 'Elevation (m)')

    with rasterio.open(dsm_path) as dod1:

        arr = dod1.read(1)

        arr[arr == -999] = np.nan

        vrange = kwargs.get('range', (np.nanmin(arr), np.nanmax(arr)))

        plt.hist(x=arr[~np.isnan(arr)].flatten(), bins=n_bins, color=colour, histtype='bar',
                 range=vrange, density=density, edgecolor='black', linewidth=1.2)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.show()

        if save_path is not None:
            plt.savefig(fname=save_path, dpi=dpi, format='jpg')


def hist_roughness(dsm_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    colour = kwargs.get('colour', 'red')
    n_bins = kwargs.get('n_bins', None)
    density = kwargs.get('density', False)
    title = kwargs.get('title', 'Surface roughness Histogram')
    xlabel = kwargs.get('x_label', 'Standard deviation of point elevations per cell (m)')

    with rasterio.open(dsm_path) as ras:

        arr = ras.read(2)

        arr[arr == -999] = np.nan

        vrange = kwargs.get('range', (np.nanmin(arr), np.nanmax(arr)))

        plt.hist(x=arr[~np.isnan(arr)].flatten(), bins=n_bins, color=colour, histtype='bar',
                 range=vrange, density=density, edgecolor='black', linewidth=1.2)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.show()

        if save_path is not None:
            plt.savefig(fname=save_path, dpi=dpi, format='jpg')


def hist_precision(ppc_path, **kwargs):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    colour = kwargs.get('colour', 'cyan')
    n_bins = kwargs.get('n_bins', None)
    density = kwargs.get('density', False)
    title = kwargs.get('title', 'SFM Precision Histogram')
    dimension = kwargs.get('dimension', 'z')
    xlabel = kwargs.get('x_label', '{0} Precision (m)'.format(dimension))

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

    plt.hist(x=ppc_arr, bins=n_bins, color=colour, histtype='bar',
             range=vrange, density=density, edgecolor='black', linewidth=1.2)
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
    xlabel = kwargs.get('x_label', 'Elevation change (m)')


    with rasterio.open(dem_o_diff_path) as ras:

        arr = ras.read(1)

        arr[arr == -999] = np.nan

        vrange = kwargs.get('range', (np.nanmin(arr), np.nanmax(arr)))

        plt.hist(x=arr[~np.isnan(arr)].flatten(), bins=n_bins, color=colour, histtype='bar',
                 range=vrange, density=density, edgecolor='black', linewidth=1.2)
        plt.title(title)
        plt.xlabel(xlabel)

        plt.show()

        if save_path is not None:
            plt.savefig(fname=save_path, dpi=dpi, format='jpg')


def hist_lod(dem_o_diff_path, **kwargs ):
    save_path = kwargs.get('save_path', None)
    dpi = kwargs.get('dpi', 300)
    colour = kwargs.get('colour', 'blue')
    n_bins = kwargs.get('n_bins', None)
    density = kwargs.get('density', False)
    title = kwargs.get('title', 'Limit of Detection Histogram')
    xlabel = kwargs.get('x_label', 'Limit of Detection (m)')

    with rasterio.open(dem_o_diff_path) as ras:

        arr = ras.read(2)

        arr[arr == -999] = np.nan

        vrange = kwargs.get('range', (np.nanmin(arr), np.nanmax(arr)))

        plt.hist(x=arr[~np.isnan(arr)].flatten(), bins=n_bins, color=colour, histtype='bar',
                 range=vrange, density=density, edgecolor='black', linewidth=1.2)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.show()

        if save_path is not None:
            plt.savefig(fname=save_path, dpi=dpi, format='jpg')

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