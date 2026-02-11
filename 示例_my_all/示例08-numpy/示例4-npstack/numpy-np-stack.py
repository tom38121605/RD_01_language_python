
# np.stack((x,y,z), axis=1)对数组的拼接的就讲解：
#
# axis=1 → x/y/z 各占一列
# axis=0 → x/y/z 各占一行


import numpy as np
x = [1,2]
y = [3,4]
z = [5,6]

# axis=1 → x/y/z 各占一列
print(np.stack((x,y,z), axis=1))
# 输出：
# [[1 3 5]  # 第1行：x1,y1,z1
#  [2 4 6]]  # 第2行：x2,y2,z2

# axis=0 → x/y/z 各占一行
print(np.stack((x,y,z), axis=0))
# 输出：
# [[1 2]  # x行
#  [3 4]  # y行
#  [5 6]] # z行
