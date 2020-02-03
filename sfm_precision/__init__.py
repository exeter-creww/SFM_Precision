from __future__ import absolute_import

__version__ = '0.1'

from sfm_precision import precision_module

def run(num_iterations,**kwargs):
    """
    main function of sfm_precision package - runs the precision analysis monte carlo process.
    provide the number of camera optimisation iterations are required. Optional arguments to
    request shape-only precision to be calculated and to export a log file.
    """

    param_list = kwargs.get('params_list', None)
    shape_only_prec = kwargs.get('shape_only_Prec', False)
    export_log = kwargs.get('export_log', True)

    precision_module.main(num_iterations, param_list, shape_only_prec, export_log,)


