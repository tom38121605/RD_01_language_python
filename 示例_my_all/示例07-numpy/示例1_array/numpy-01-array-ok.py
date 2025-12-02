import numpy as np

# 1. 创建一个 NumPy 二维数组
np_array = np.array( [ [0, -1] ] )
print("NumPy 数组:", np_array)
print("类型:", type(np_array))  # <class 'numpy.ndarray'>
print("形状:", np_array.shape)  # (1, 2) -> 1 行，2 列
print("维度:", np_array.ndim)   # 2 -> 二维

print("-" * 50)

def func(): a=1; print(a);

def func2(): a=2; print(a)

func2()


