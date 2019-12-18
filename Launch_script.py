import SFM_precision_analysis
import Metashape
import os

def main():
    filename = os.path.abspath("C:/HG_Projects/CWC_Drone_work/PrecAnal_Testing/pia_plots/P3E1.psz")

    n_its = 10
    params = ['fit_f', 'fit_cx'] # Choose from the following (include if True) -
                                 # ['fit_f', 'fit_cx', 'fit_cy','fit_b1', 'fit_b2', 'fit_k1', 'fit_k2', 'fit_k3',
                                 # 'fit_k4','fit_p1', 'fit_p2', 'fit_p3', 'fit_p4']
                                 # if all false pass empty list.
                                 # if no list is provided in args then defaults are used

    doc = Metashape.app.document
    doc.open(filename, read_only=False)

    # SFM_precision_analysis.Run(num_iterations=n_its, shape_only_Prec=True, params_list=params) # full options
    SFM_precision_analysis.Run(num_iterations=n_its)  # what we really need...

    doc.save()

    print("DONE!!!")


if __name__ == '__main__':
    main()

