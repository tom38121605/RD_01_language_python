
# 说明1： np.where取得的值并不是由np.array定义成一维还是二维决定的。np.where取得的值step2是2维数组。
#        np.array定义成1维数组只返回一个元素（行），np.array定义成2维数组就返回2个元素（列），np.array定义成2维数组就返回3个元素（高）
#        np.where返回的二维数组的元素个数，跟设备数量无关，但跟设备定义的维数有关
#        np.array定义成1维数组，只能1个设备；如果2个设备，最少也要定义成2维数组


import numpy as np


# # -------------test1--------- 输入：1维列表数组---1个设备 --输出： step2二维数组---1个列表元素列---ok-------------------
#
# #  t0_all是1维数组（列表转化而来）， 里面有的4个元素（只有第0行）
# #  返回的step2是一个2维的数组，里面每个元素是一个1维的列表数组 ，里面只有一个元素“列”
# #  本例中，step2相当于只在x坐标上，找出true的位置
#
# t0_all = np.array([100, 110, 100, 120], dtype=np.int64)   # t0_all是二维数组， 里面有一个1维列表
# print("t0all", t0_all)
#
# t0 = np.min(t0_all)  # 最小值：100
# print("t0=l", t0)
#
# # 逻辑表
# step1 = t0_all == t0  # step1是1维的布尔列表数组
# print("\nstep1", step1) #  [True, False, True, False]
#
# step2 = np.where(step1)  # step2是一个2维的数组， (array([0, 2]),)
#                          # 数组里面的每一个元素是一个1维的列表数组 [0, 2]
# print("step2", step2)
#
# t0_idx1 = step2[0]  # step2数组的一个元素： [0, 2]
# print("t0_idx1（列索引） =", t0_idx1)  # 输出：[0 2]  一维数组只有列索引，省略了行索引（可把不存在的行索引看作都是0行）


# # -------------test2--------输入：2维列表数组--- 1个设备 ----输出：step2二维数组--- 2个列表元素行列---ok------------------
#
# #  t0_all是2维数组， 里面有的元素是1维列表，只有一个元素
# #  step2是二维数组，有行列两个列表元素
# #  本例中，step2相当于在x，y坐标上，找出true的位置，而y坐标（行）固定为0
#
# t0_all = np.array([     # t0_all是3维数组， 里面有一个2维列表
#     [100, 110, 100, 120],
# ], dtype=np.int64)
# print("t0all", t0_all)
#
# t0 = np.min(t0_all)
# print("t0 =", t0)  # 输出：t0 = 100
#
# step1 = t0_all == t0      # step1是2维的布尔列表数组
# print("\nstep1=", step1)  #  [[ True False  True False]]
#
# step2 = np.where(step1)  # step2是一个2维的数组，元素是列表，有行列两个元素
# print("step2=", step2)   # (array([0, 0]), array([0, 2]))
#
# t0_idx0 = step2[0]
# t0_idx1 = step2[1]
#
# print("t0_idx0（行索引） =", t0_idx0)   #[0, 0]
# print("t0_idx1（列索引） =", t0_idx1)   #[0, 2]


#
# # ------------test3-------- 输入：2维数组--- 2个设备 ----输出： step2二维数组 ---2维列表元素行列--------ok-------------------
#
# #  t0_all是2维数组， 里面有的元素是1维列表，只有2个元素（2个设备）
# #  step2是二维数组，有行列两个列表元素
# #  本例中，step2相当于在x，y坐标上，找出true的位置
#
# t0_all = np.array([
#     [100, 110, 100, 120],
#     [100, 100, 110, 100]
# ], dtype=np.int64)
# print("t0all", t0_all)
#
# t0 = np.min(t0_all)
# print("t0 =", t0)  # 输出：t0 = 100
#
# step1 = t0_all == t0      # step1是2维的布尔列表数组
# print("\nstep1=", step1)  #  [  [ True False  True False]  [ True  True False False]  ]
#
# step2 = np.where(step1)  # step2是一个2维的数组，元素是列表，有行列两个元素
# print("step2=", step2)   # (array([0, 0, 1, 1, 1]), array([0, 2, 0, 1, 3]))
#
#
# t0_idx0 = step2[0]
# t0_idx1 = step2[1]
#
# print("t0_idx0（行索引） =", t0_idx0)   # [0 0 1 1 1]
# print("t0_idx1（列索引） =", t0_idx1)   # [0 2 0 1 3]
#
#
