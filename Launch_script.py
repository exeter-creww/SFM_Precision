# Placed outside of the module folder to make sure that metashape is running the version in the site packages
# directory and not the version here

import SFM_precision
import Metashape
import os

test_proj = os.path.abspath("C:/HG_Projects/CWC_Drone_work/PrecAnal_Testing/pia_plots/P3E1.psz")
# test_proj = os.path.abspath("C:/HG_Projects/CWC_Drone_work/16_12_18_Danes_Mill/16_12_18_DanesCroft_backup_copy.psx")
# root_dir = os.path.abspath("C:/HG_Projects/CWC_Drone_work")
#
# psx1 = os.path.join(root_dir, "16_12_18_Danes_Mill", "16_12_18_DanesCroft.psx")
# psx2 = os.path.join(root_dir, "17_02_15_Danes_Mill", "17_02_15_DanesCroft.psx")
# psx3 = os.path.join(root_dir, "17_09_07_Danes_Mill", "17_09_07_DanesCroft.psx")
# psx4 = os.path.join(root_dir, "18_01_23_Danes_Mill", "18_01_23_DanesCroft.psx")
# psx5 = os.path.join(root_dir, "18_03_27_Danes_Mill", "18_03_27_DanesCroft.psx")
# psx6 = os.path.join(root_dir, "18_09_25_Danes_Mill", "18_09_25_DanesCroft.psx")

# psx_list = [psx1, psx2, psx3, psx4, psx5, psx6]

def main():

    n_its = 3
    # params = ['fit_f', 'fit_cx']  # Choose from the following (include if True) -
                                # ['fit_f', 'fit_cx', 'fit_cy','fit_b1', 'fit_b2', 'fit_k1', 'fit_k2', 'fit_k3',
                                # 'fit_k4','fit_p1', 'fit_p2', 'fit_p3', 'fit_p4']
    # if all false pass empty list.
    # if no list is provided in args then defaults are used.
    doc = Metashape.app.document
    doc.open(test_proj, read_only=False)
    SFM_precision.Run(num_iterations=n_its)
    # for psx in psx_list:
    #     doc = Metashape.app.document
    #     doc.open(psx, read_only=False)
    #
    #     # SFM_precision_Module.Run(num_iterations=n_its, shape_only_Prec=False, export_log=True, params_list=params)  # full options
    #     # SFM_precision_Module.Run(num_iterations=n_its, params_list=params)  # just optimization params
    #     SFM_precision.Run(num_iterations=n_its)  # what we really need...
    #     # SFM_precision.Run
    #     doc.save()

    print("DONE!!!")


if __name__ == '__main__':
    main()
