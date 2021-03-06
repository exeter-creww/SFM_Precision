from __future__ import absolute_import

__version__ = '0.1'

from sfm_gridz import DSM
from sfm_gridz import precision_map
from sfm_gridz import dem_of_diff
from sfm_gridz import plot_gridz
from sfm_gridz import CHM

def dsm(point_cloud, out_raster, resolution, **kwargs):
    """ Function to run the height map module"""

    window_size = kwargs.get('window_size', 0)
    epsg = kwargs.get('epsg', None)
    bounds = kwargs.get('bounds', None)
    mask = kwargs.get('mask', None)

    dsm_class = DSM.height_map(point_cloud, out_raster, resolution, window_size, epsg, bounds, mask)

    return dsm_class


def precision(prec_point_cloud, out_raster, resolution, **kwargs):
    """ Function to run the preicsion map module"""

    prec_dimension = kwargs.get('prec_dimension', 'z')
    epsg = kwargs.get('epsg', None)
    bounds = kwargs.get('bounds', None)
    mask = kwargs.get('mask', None)

    prec_class = precision_map.precision_map(prec_point_cloud, out_raster, resolution,
                                             prec_dimension, epsg, bounds, mask)

    return prec_class


def difference(raster_1, raster_2,prec_point_cloud_1, prec_point_cloud_2, out_ras, **kwargs):
    """ Function to run the dem of difference module"""

    epsg_code = kwargs.get('epsg', None)
    reg_error = kwargs.get('reg_error', 0)
    t_value = kwargs.get('t_value', 1)
    handle_gaps = kwargs.get('handle_gaps', True)
    mask = kwargs.get('mask', None)
    lod_method = kwargs.get('lod_method', 'threshold')

    demod_class = dem_of_diff.dem_of_diff(raster_1, raster_2, prec_point_cloud_1, prec_point_cloud_2, out_ras,
                                          epsg_code, reg_error, t_value, handle_gaps, mask, lod_method)

    return demod_class


def chm(dsm_file, dtm_file, chm_save_name):
    """ Function to run Canopy height map module"""

    chm_class = CHM.canopy_height(dsm_file,dtm_file, chm_save_name)

    return(chm_class)