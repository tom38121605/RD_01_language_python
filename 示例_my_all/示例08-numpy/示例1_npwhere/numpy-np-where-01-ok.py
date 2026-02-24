
# 说明0：np.where输出的step2只能是二维数组 （并不是由np.array定义成一维还是二维决定的）

# 说明1：np.where输出的step2是二维数组，
#       一般情况下，如示例test2，test3中，step2有且只有2个元素(行,列),第一个元素为真值表的行坐标列表，第二个元素为列坐标列表
#       但示例test1是唯一的一个特例，输入的t0_all都是一维数组，输出的step2里面只有1个元素（列）

# 说明2： 下面的例子，test3，test2是最清晰的，先看test3，test2以便容易理解
#        test3和test2输入的t0_all都是二维数组， 二维数组自带行列，输出的step2的两个元素就明显是该行列的坐标。

   # ------test3：-----

       # t0_all = [                         //输入
       #     [100, 110, 100, 120],，
       #     [100, 100, 110, 100]
       # ]

       # step2 = (  array1(), array2()  )    //输出

    # -----test2：----

        # t0_all = [                        //输入
        #     [100, 110, 100, 120],
        # ]

        # step2 = (  array1(), array2()  )   //输出


# 说明3： test1输入的t0_all都是一维数组， 没有行列的坐标概念，只有一条直线的队列概念，输出的step2是各二维数组，但只有一个元素（列）

   # ------test1：-----

       # t0_all = [100 110 100 120]     //输入

       # step2 = (  array1(), )         //输出


# 说明4： test4输入的t0_all都是二维数组， 二维数组自带行列，输出的step2的两个元素就明显是该行列的坐标

   # ------test4：-----

       # t0_all = [                        //输入
       #     [120],
       #     [100],
       #     [110],
       #     [100],
       #     [100],
       # ]

       # step2 = (  array1(), array2()  )   //输出， 虽然取test4输出的第一个元素跟test3的第一个元素很类似，但却是不同的两种方法


# 说明5： 忽略下面横线注释中的“设备”及其数量，其逻辑无关  （已清除设备，忽略这里）


import numpy as np


# # -------------test1--------- 输入：1维列表数组 --输出： step2二维数组---1个列表元素列---ok-------------------
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
# print("\nstep1=", step1) #  [ True False  True False]
#
# step2 = np.where(step1)  # (array([0, 2]),)
#
# print("step2=", step2)
#
# t0_idx1 = step2[0]  # step2数组的第一个元素： [0, 2]
# print("t0_idx1（列索引） =", t0_idx1)  # 输出：[0 2]


# # -------------test2--------输入：2维列表数组----输出：step2二维数组--- 2个列表元素行列---ok------------------
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


# # ------------test3-------- 输入：2维数组----输出： step2二维数组 ---2维列表元素行列--------ok-------------------
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
# print("\nstep1=", step1)  # [  [ True False  True False]  [ True  True False False]  ]
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


# ------------test4-------- 输入：2维数组----输出： step2二维数组 ---2维列表元素行列--------ok-------------------

#  t0_all是2维数组， 里面有的元素是1维列表，只有2个元素（2个设备）
#  step2是二维数组，有行列两个列表元素
#  本例中，step2相当于在x，y坐标上，找出true的位置

t0_all = np.array([
    [120],
    [100],
    [110],
    [100],
    [100]
], dtype=np.int64)
print("t0all", t0_all)

t0 = np.min(t0_all)
print("t0 =", t0)  # 输出：t0 = 100

step1 = t0_all == t0      # step1是2维的布尔列表数组
print("\nstep1=", step1)  # [  [False] [True] [False] [True] [True]  ]

step2 = np.where(step1)  # step2是一个2维的数组，元素是列表，有行列两个元素
print("step2=", step2)   #  (array([1, 3, 4]), array([0, 0, 0]))


t0_idx0 = step2[0]
t0_idx1 = step2[1]

print("t0_idx0（行索引） =", t0_idx0)   # [1 3 4]
print("t0_idx1（列索引） =", t0_idx1)   # [0 0 0]