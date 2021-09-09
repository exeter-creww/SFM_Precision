# testing a new idea...


import os
import numpy as np
import glob
from plyfile import PlyData
from tqdm import tqdm

# data_dir = os.path.abspath("C:/HG_Projects/CWC_Drone_work/pia_plots/Monte_Carlo_output")
# data_dir = os.path.abspath("C:/HG_Projects/CWC_Drone_work/NEW_Prec_test_outs_v1/MC_Test_outs")
data_dir = os.path.abspath("C:/HG_Projects/CWC_Drone_work/HG_Retest_Pia/Monte_Carlo_output")
arr_list = []

for ply in tqdm(glob.glob(os.path.join(data_dir, "*.ply"))):
    plydata = PlyData.read(ply)
    ply_arr = np.vstack([plydata.elements[0].data['x'],
                         plydata.elements[0].data['y'],
                         plydata.elements[0].data['z']]).transpose()

    arr_list.append(ply_arr)

# for txt in tqdm(glob.glob(os.path.join(data_dir, "*.txt"))):
#     pcdata = np.loadtxt(txt, dtype={'names': ('x', 'y', 'z'), 'formats': ('f8', 'f8', 'f8')})
#     pc_arr = np.vstack([pcdata['x'],
#                         pcdata['y'],
#                         pcdata['z']]).transpose()
#
#     arr_list.append(pc_arr)

# print(pc_arr)

# These are the true arrays that we want...
mean_arr_np = np.mean(arr_list, axis=0)
std_arr = np.std(arr_list, axis=0)

print(np.mean(std_arr))



# For a new value newValue, compute the new count, new mean, the new M2.
# mean accumulates the mean of the entire dataset
# M2 aggregates the squared distance from the mean
# count aggregates the number of samples seen so far
def update(existingAggregate, newValue):
    (n, count, mean, M2) = existingAggregate
    n += 1
    count = count.__iadd__(1)
    delta = np.subtract(newValue, mean)
    mean = mean.__iadd__(np.divide(delta, count))
    # mean += np.divide(delta, count)
    delta2 = np.subtract(newValue, mean)
    M2 = M2.__iadd__(np.multiply(delta, delta2))
    # M2 += delta * delta2

    return (n, count, mean, M2)

# Retrieve the mean, variance and sample variance from an aggregate
def finalize(existingAggregate):
    (n, count, mean, M2) = existingAggregate
    (mean, variance, sampleVariance) = (mean, M2 / count, M2 / (count - 1))
    if n < 2:
        return float('nan')
    else:
        return (mean, variance, sampleVariance)

prec_val = 1000000000
dims = np.shape(arr_list[0])
start_arr = np.zeros(dims)

Agg = (0, start_arr, arr_list[0]*prec_val, arr_list[0]*prec_val)

for arr in tqdm(arr_list):
    check_dim = np.shape(arr)
    if check_dim != dims:
        print("size issue...")
        continue
    int_arr = np.asarray(arr*prec_val, dtype=np.float64)
    Agg = update(Agg, int_arr)


mean, variance, sampleVariance = finalize(Agg)

stdev_arr = np.sqrt(variance)/prec_val
mean_arr = mean/prec_val
# sv_std = np.sqrt(sampleVariance)
print(np.mean(stdev_arr))


out_cloud_path = os.path.abspath("C:/HG_Projects/CWC_Drone_work/HG_Retest_Pia/Roll_Outs/Roll_test_it100b.txt")

combined = np.concatenate((mean_arr, stdev_arr), axis=1)
nested_lst_of_tuples = [tuple(l) for l in combined]
comb_arr = np.array(nested_lst_of_tuples,
                    dtype=[('x', 'f8'), ('y', 'f8'),
                           ('z', 'f8'), ('xerr', 'f8'), ('yerr', 'f8'),
                           ('zerr', 'f8')])

np.savetxt(out_cloud_path, comb_arr, delimiter=" ",
           header="x y z xerr yerr zerr", comments='')

# print((np.mean(sv_std)/prec_val))

print("done")