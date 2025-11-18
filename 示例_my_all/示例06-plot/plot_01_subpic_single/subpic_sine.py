
import matplotlib.pyplot as plt
import numpy as np

# 创建子图并赋值给 subpic
subpic = plt.subplot()

# 通过 subpic 画图和设置属性
x = np.linspace(0, 20, 201)  # 0到10的101个点

subpic.plot(x, np.sin(x), label='sin(x)', color='red')  # 画正弦曲线
subpic.plot(x, np.cos(x), label='cos(x)', color='green')  # 画余弦曲线

subpic.set_xlabel('X')  # 设X轴标签
subpic.set_ylabel('Y')  # 设Y轴标签
subpic.set_title('Sine Cosine Graph')  # 设标题
# subpic.legend()  # 显示图例
subpic.legend(loc='lower left')  # 把线条的标签显示在左下角

plt.show()  # 显示图形





