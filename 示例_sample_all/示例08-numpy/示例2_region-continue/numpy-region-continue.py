import numpy as np

#功能：对真值表的连续个数的位置进行统计，并筛选掉连续个数太小的位置
# 参数：condition（真值表），1
def contiguous_regions(condition, min_len=0):
    d = np.diff(condition)  # np.diff是取得状态切换的真值表
    print("condition=", condition)
    print("d=", d)
    idx, = d.nonzero()   # 把不为0的真值的位置，生成一个新的数组 （注意是矩阵中“位置”,2维矩阵是行列坐标格式）
                         # 后面的逗号：等价于idx = d.nonzero()[0], 就是取出其中的第1个元素，即矩阵中“列”的位置列表
    print("idx=", idx)
    idx += 1  # 每个元素的位置值都+1, 用于首尾成双处理

    #如果首部为True，则首部凑成双
    if condition[0]:
        idx = np.r_[0, idx]  # 把 0 插到索引数组 idx 的最前面

    #如果尾部为True，则尾部部凑成双
    if condition[-1]:
        idx = np.r_[idx, condition.size]  # 把数组的总长度追加到索引数组 idx 末尾

    idx.shape = (-1, 2)  # 把idx从1维数组转换成2维数组，-1的意思是自动算出行数
    print("idx=", idx)

    aaa = np.subtract(idx[:, 1], idx[:, 0])  # 等价于 aaa = idx[:,1] - idx[:,0]， 每次连续True值的个数
    bbb = aaa > min_len   #根据门槛值min_len，生成一个同样维度矩阵的真值表
    idx = idx[bbb]       # numpy的特有功能，可以根据真值表中的True，筛选出新的idx列表 （去掉真值表中为False的对应元素）

    print("aaa=", aaa)
    print("bbb=", bbb)
    # print("idx new=", idx)

    return idx


# condition = np.array([False, True, True, False, True, False])
# print("idx new=",contiguous_regions(condition))
# # 输出：[[1 3], [4 5]]

condition = np.array([False, True, True, False, True, False])
print("idx new=", contiguous_regions(condition, 1))
# 输出：[[1 3]]
