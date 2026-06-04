
import h5py
import numpy as np
import matplotlib.pyplot as plt
import sys
import os.path
import math

file_name = "d:\\data0.hdf5"
data_file = h5py.File(file_name, 'r')
test_regions = np.array([[0,-1]])

print("file=" + data_file.filename)

print("keys=" + f'{data_file.keys()}')  #keys返回 对象的字符串名称

print("values=" )
for device in data_file.values():      #values返回对象本身，如group或dataset
    print(device)