import numpy as np
delta = np.array([[10000, 20000], [100000, 80000]])  # 2行2列的二维数组
ts_event_idx = [0, 3]  # 要提取的元素索引（按一维展开的索引）

# 修正：先展平数组，再按一维索引取值
AAA = delta.flatten()[ts_event_idx]
print(AAA)  # 输出：[10000 80000]