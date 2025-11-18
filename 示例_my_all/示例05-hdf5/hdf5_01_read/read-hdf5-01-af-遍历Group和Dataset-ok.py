from os.path import expanduser
import h5py
import numpy as np
import matplotlib.pyplot as plt
import logging
import sys
import os.path
import math


# def main():
#
#     file_name = "data0.hdf5"
#     data_file = h5py.File(expanduser(file_name), 'r')
#     print("文件中的对象：", list(data_file.keys()))
#
#     dataset = data_file['/Device_3528137102_0/Theta']      #取得数集的dataset
#     data = dataset[:]  #取得数集的所有内容  # 推荐用 [:]，兼容所有 HDF5 版本
#
#     print("数据集内容：", data)               # 输出该数集的所有内容
#     print("数据集形状：", dataset.shape)      # 输出该数集的行列数和维度， (17704, 1)
#     print("数据集数据类型：", dataset.dtype)   # 输出该数集的内容，uint16
#
#     data_file.close()

def main():

    file_path = r"data0.hdf5"

    with h5py.File(file_path, 'r') as f:

        def get_dataset_name(name, obj):
            if isinstance(obj,h5py.Group):
                print(f"数据集完整路径：{name}")

            if isinstance(obj, h5py.Dataset): # and name.endswith("Theta"):
                print(f"数据集名称：{name.split('/')[-1]}")

        f.visititems(get_dataset_name)


if __name__ == "__main__":
    main()