# Based on http://www.johndcook.com/standard_deviation.html
# from https://github.com/liyanage/python-modules/blob/master/running_stats.py

import numpy as np



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


# function to create random list of numpy arrays between 0 and 0.1
def RandArray(x, y, n):
    array_list = []

    for j in range(n):
        arr = np.random.random_sample((x, y)) / 10  # Set at 0-0.1 for my purposes - any list off arrays will do
        array_list.append(arr)

    return array_list
# args for creating array list
x = 2
y = 2
n = 1000

#create array list
Arr_List = RandArray(x, y, n)

# Get array dimensions
dimen = Arr_List[0].shape

# provide dimensions for class
rs = RunningStats(dimen)

# push array to function
for i in Arr_List:
    rs.push(i, dimen)

# print and compare results with typical way.
print("continuous approach")
mean = rs.mean()
print("cont. mean:")
print(mean)
variance = rs.variance()
print("cont. var:")
print(variance)
stdev = rs.standard_deviation()
print("cont. std:")
print(stdev)

print("normal (numpy) approach")
tradmean = np.mean(Arr_List, axis=0)
print("normal mean:")
print(tradmean)
tradvar = np.var(Arr_List, axis=0)
print("normal var:")
print(tradvar)
tradstd = np.std(Arr_List, axis=0)
print("normal std:")
print(tradstd)


