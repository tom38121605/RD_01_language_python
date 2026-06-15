#==============================================================================
# AFE noise measurement script for disposible ADC concept
#==============================================================================
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import csv
import numpy as np
import scipy.signal
import os


#-------------------- 设置常数 ----easy--------------------

Vref = 3.0   # 参考电压
Gv = 0.82     # Bridge
Gi = 47       # 10R
Rs = 10       # 10R
fs = 3676.5

#-------------------- 设置文件路径，文件名称 ----easy--------------------

t_path = "25C.txt"
plot_path1 = ('plots/25C_FR.png')


#-------------------- 读取txt文件中的数据 ----easy--------------------

t_data_x = []   # 10R
t_data_y = []   # Bridge

with open(t_path, 'r') as csvfile:
    datafile = csv.reader(csvfile, delimiter = '\t')
    for row in datafile:
        t_data_x.append(float(row[0]))    # 每行的第0列
        t_data_y.append(float(row[1]))    # 每行的第1列


#-------------------- 计算电压，电流，电阻 ----easy--------------------

# 根据参考电压，计算23位数据每格的电压
V_LSB = Vref/2**23    # 每格电压

# 计算 Bridge上的电压
data_v1 = np.array(t_data_y)
data_v = (data_v1 * V_LSB)/Gv      # Gv=0.82

# 计算 10上的电流
data_i1 = np.array(t_data_x)
data_i = ((data_i1 * V_LSB)/Gi)/Rs    # Gi=47  Rs=10

# 计算电阻
res = data_v / data_i


#-------------------- 计算每个频率的电压噪声密度 ----easy--------------------

# 计算每个频率电压平方的噪声密度
fft_len = 1024 * 16
xF, spectrumx = scipy.signal.welch(res, fs=fs, nperseg=fft_len, noverlap=0)  # xF -- 频率, stectrumx -- 密度

# print(len(xF))
# print(xF[:10])

# 计算每个频率电压的噪声密度
xfr = np.sqrt(spectrumx)   # 计算每个频率的电压


#==============================================================================
#process data for plotting
# limit BW to 1000 Hz
limited_freqs = [x for x in xF if x < fs/2]     # 取得比中位数低的一半频率， x轴  --  f
limited_dB_x = xfr[:len(limited_freqs)]         # 取前一半的噪声密度值，    y轴  --  噪声密度

limited_dB_x[0] = limited_dB_x[1]   # 最开始的1个数据误差大，用第2个数据替换它


#-------------------- 在子画布上画出频谱图 ----easy--------------------

plt.figure(figsize=(6,4), dpi=200, facecolor='white')   # 新建一张：大小 12x8、清晰度200、白底的画布
ax = plt.subplot()                                       # 建立一张子画布
ax.tick_params(axis='both', which='major', labelsize=12)            # 对xy轴上的大刻度，字体设为12
plt.title('Noise Density : 25C', fontsize=10)                   # 设置子画布标头

L1 = 'Line1'
ax.plot(limited_freqs, limited_dB_x, color='black', linewidth=1, label=L1)  # 画线 (连线所有的点)
ax.legend(loc='upper right', fontsize=12)   # 显示图例 Line1


#-------------------- 设置图片参数 ----easy--------------------

ax.set_xscale('log')     # X轴用对数坐标
ax.set_yscale('log')     # Y轴用对数坐标
plt.xlabel('Frequency [Hz]', fontsize=12)    # x轴标签
plt.ylabel('Noise Density [Ω/√Hz]', fontsize=12)  # y轴标签
plt.grid(visible=True, which='both', axis='both')  # 显示xy轴上的粗细网格
# plt.axis([1,1500,1e-5,1e-0])   # 设定 X 轴和 Y 轴的显示范围
plt.grid(which='major', color='black', linestyle='-', linewidth = 0.50)  # 主网格（粗一点）
plt.grid(which='minor', color='black', linestyle='-', linewidth = 0.10)  # 次网格（细一点）
plt.axis([1,1500,1e-5,1e-0])   # 设定 X 轴和 Y 轴的显示范围


plt.savefig(plot_path1)
plt.show()







