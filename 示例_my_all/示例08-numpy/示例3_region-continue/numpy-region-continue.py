import numpy as np

# 参数：condition，1
def contiguous_regions(condition, min_len=0):
    d = np.diff(condition)  # 依次取得相邻两个元素的差值，生成一个新的差值数组
    idx, = d.nonzero()  # 把不为0的差值的位置，生成一个新的数组 （注意是矩阵中“位置”）
    # 后面的逗号：等价于idx = d.nonzero()[0], 就是取出其中的第1个元素，即矩阵中“列”的位置列表
    idx += 1  # 每个元素的值都+1

    if condition[0]:
        idx = np.r_[0, idx]  # 把 0 插到索引数组 idx 的最前面

    if condition[-1]:
        idx = np.r_[idx, condition.size]  # 把数组的总长度追加到索引数组 idx 末尾

    idx.shape = (-1, 2)  # 把idx从1维数组转换成2维数组，-1的意思是自动算出行数

    aaa = np.subtract(idx[:, 1], idx[:, 0])  # 等价于 aaa = idx[:,1] - idx[:,0]， 每次连续True值的个数
    bbb = aaa > min_len
    idx = idx[bbb]

    return idx


condition = np.array([False, True, True, False, True, False])
print(contiguous_regions(condition))
# 输出：[[1 3], [4 5]]

condition = np.array([False, True, True, False, True, False])
print(contiguous_regions(condition, 1))
# 输出：[[1 3]
