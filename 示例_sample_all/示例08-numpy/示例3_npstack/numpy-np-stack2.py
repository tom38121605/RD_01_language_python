
import numpy as np

a = np.array([[1], [2]])  # shape=(2,1)
b = np.array([[3], [4]])  # shape=(2,1)

print(a.shape)  # (2, 1)

c = np.stack([a, b], axis = 0)   # axis=0，表示a,b各变成一层
print(c.shape)  # (2, 2, 1)
print(c)        # [ [[1] [2]]  [[3] [4]] ]


c = np.stack([a, b], axis = 1)    # axis=1，先把a,b各变成一层，形成一个矩阵，再把矩阵顺时针旋转90度，从而列变成行形成新的矩阵
print(c.shape)  # (2, 2, 1)
print(c)        # [ [[1] [3]]  [[2] [4]] ]


c = np.stack([a, b], axis = 2)
print(c.shape)  # (2, 1, 2)
print(c)        # [ [[1 3]] [[2 4]] ]   # axis=2，表示a,b各变成一2列？

