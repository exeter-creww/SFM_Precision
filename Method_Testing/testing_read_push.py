import laspy
import os
import numpy as np
import glob
from plyfile import PlyData, PlyElement

dir_path = os.path.abspath('C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1')

outfolder = os.path.join(dir_path, "MonteCarlo_Export")

home = os.path.abspath("C:/HG_Projects/CWC_Drone_work/Prec_test_outs_v2/Monte_Carlo_output")
las_list = glob.glob(os.path.join(home, "*.ply"))

def readPLY(ply):
    plydata = PlyData.read(ply)
    ply_arr = np.vstack([plydata.elements[0].data['x'],
                         plydata.elements[0].data['y'],
                         plydata.elements[0].data['z']]).transpose()
    return ply_arr

def main():
    count = 0
    reqdim = readPLY(las_list[0])
    rs = RunningStats(reqdim.shape)

    for ply in las_list:
        count += 1
        # lf_r = laspy.file.File(las, mode="r")
        ply_arr = readPLY(ply)

        if count == 1 or count == 10:
            print(ply_arr)

        # push array to function
        rs.push(ply_arr)

    print("Monte Carlo iterations complete\n"
          "retrieve stats and convert to las...")
    mean_arr = rs.mean()
    stdev_arr = rs.standard_deviation()

    combined = np.concatenate((mean_arr, stdev_arr), axis=1)
    nested_lst_of_tuples = [tuple(l) for l in combined]
    comb_arr = np.array(nested_lst_of_tuples,
                        dtype=[('x', 'f8'), ('y', 'f8'),
                               ('z', 'f8'), ('xerr', 'f8'), ('yerr', 'f8'),
                               ('zerr', 'f8')])

    el = PlyElement.describe(comb_arr, 'some_name')

    ply_path = os.path.join(outfolder, "Prec_spc_test.ply")  # out naming add as input
    PlyData([el]).write(ply_path)



class RunningStats:

    def __init__(self, dims):
        self.zeroArr = np.zeros(dims)
        self.n = 0
        self.old_m = np.zeros(dims)
        self.new_m = np.zeros(dims)
        self.old_s = np.zeros(dims)
        self.new_s = np.zeros(dims)

    def clear(self):
        self.n = 0

    def push(self, x):
        self.n += 1

        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = self.zeroArr
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else self.zeroArr

    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else self.zeroArr

    def standard_deviation(self):
        return np.sqrt(self.variance())


if __name__ == '__main__':
        main()