import matplotlib.pyplot as plt
import numpy as np

# 1. 准备数据
x = np.linspace(0, 20, 201)
y_sin = np.sin(x)
y_cos = np.cos(x)

# 2. 创建子图
#    plt.subplot(rows, columns, index)
#    index 从 1 开始
subpic1 = plt.subplot(1, 2, 1)  # 1行，2列，第1个子图
subpic2 = plt.subplot(1, 2, 2)  # 1行，2列，第2个子图

# 3. 在第一个子图 (subpic1) 上绘制和设置
subpic1.plot(x, y_sin, color='red', label='sin(x)')
subpic1.set_title('Sine Wave')  # 设置子图1的标题
subpic1.set_xlabel('X Axis')    # 设置子图1的X轴标签
subpic1.set_ylabel('Y Axis')    # 设置子图1的Y轴标签
subpic1.legend()                # 显示子图1的图例
subpic1.grid(True)              # 显示子图1的网格

# 4. 在第二个子图 (subpic2) 上绘制和设置
subpic2.plot(x, y_cos, color='green', label='cos(x)')
subpic2.set_title('Cosine Wave')# 设置子图2的标题
subpic2.set_xlabel('X Axis')    # 设置子图2的X轴标签
# 注意：这里可以不设置Y轴标签，因为和左边对齐
subpic2.legend()                # 显示子图2的图例
subpic2.grid(True)              # 显示子图2的网格

# 5. 调整子图间距，防止标签重叠（可选但推荐）
plt.tight_layout()

# 6. 统一显示所有子图
plt.show()

