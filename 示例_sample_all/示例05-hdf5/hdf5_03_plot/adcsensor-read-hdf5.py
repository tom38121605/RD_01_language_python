from os.path import expanduser
import h5py
import os.path
import glob
import sys
import numpy as np

import matplotlib.pyplot as plt
from tkinter import messagebox


VREF = 3000   #mv
GAINX = 47
GAINY = 0.82
RESX = 10
SAMPLERATE = 3676


# DATAFILE0 = "data0.hdf5"

DATAFILE0=""
if(DATAFILE0==""):
    dat_files = glob.glob("*.hdf5")
    file_num = len(dat_files)
    if file_num != 1:
        print("multi files, or no file")
        sys.exit()

    DATAFILE0=dat_files[0]

DATAFILE1=".\\data1.txt"
DATAFILE2=".\\data2.txt"
DATAFILE3=".\\data3.txt"

DATAFILE9=".\\xxC.txt"

PIC_DIR = "pic/"
DATASETNAME = "Data"


f0 = h5py.File(expanduser(DATAFILE0), 'r')

# f1=open(DATAFILE1,"w")
# f2=open(DATAFILE2"w")
# f3=open(DATAFILE3,"w")

f9=open(DATAFILE9,"w")

x1points = []
y1points = []
z1points = []

idatanum2=0

# ----------------------get path ------------------------------------------
def getpath():
    path1=""

    file_path = DATAFILE0
    with h5py.File(file_path, 'r') as f:

        last_dataset = None
        data=[]

        # 内部函数：遇到 Data 就停止
        def get_dataset_name(name, obj):
            nonlocal last_dataset
            nonlocal data
            nonlocal path1

            if isinstance(obj, h5py.Group):
                path1 = name
                # print(f"Group路径：----- {name} -----")
                print(f"Group路径：----- {path1} -----")

            elif isinstance(obj, h5py.Dataset):
                dataset_name = os.path.basename(name)
                print(f"数据集名称：{dataset_name}")

                last_dataset = dataset_name
                data = obj[:2]  # 读取全部数据 （你要[:2]也可以）

                # ====================== 关键 ======================
                # 如果名字是 Data → 保存数据 + 直接停止遍历
                # if dataset_name == "Data":
                if dataset_name == DATASETNAME:

                # 停止遍历！！！
                    raise StopIteration(f"找到 dataset，停止遍历")


        # ====================== 执行遍历 ======================
        try:
            f.visititems(get_dataset_name)
        except StopIteration:
            # 遇到 Data 正常停止
            pass

        # ====================== 输出结果 ======================
        if last_dataset:
            print("\n===== 找到目标数据集 =====")
            print("数据集名称：", last_dataset)
            print("数据集内容：", data)

    return path1


# sys.exit()
# ----------------------get path "-----end----------------------------------"

path_dataset = getpath()
print("path=", path_dataset)

# sys.exit()

# dataset = f0['/Logging_Test_COM3_11763_ADC_Sampler_3ch/DeviceGroup_0/Device_0/IC_0/Sensor_0/Data']
dataset = f0[f'/{path_dataset}/{DATASETNAME}']

data = dataset[:]
# print( data)

for num_list in data:
    number0 = num_list[0]
    number1 = num_list[1]
    number2 = num_list[2]

    # f1.write(f"{number0}\n")
    # f2.write(f"{number1}\n")
    # f3.write(f"{number2}\n")

    f9.write(f"{number0}	{number1}	{number2}\n")

    x1points.append(number0)
    y1points.append(number1)
    z1points.append(number2)

    idatanum2 += 1

# f0.close()

# f1.close()
# f2.close()
# f3.close()

f9.close()


print("num =", idatanum2)
# if (idatanum2 != 100000):
#     messagebox.showinfo("num", idatanum2)



# ================================== print pic start=======================================

#----------------------- x channel ----10R------------------

print(x1points)

#---show x data
plt.plot(x1points, color='blue')
plt.ylabel('datax -- xchannel 10R', fontsize=12)
plt.axis([0, idatanum2, -1000000 , 6000000])  # 1KHz 10S SHORT
plt.show()


# #---show x I (mA)
x1points = np.array(x1points, dtype=np.float64)
KKK = VREF /8388608 / 47 /10
x1points2 = (x1points * KKK).astype(float)

t = [i / SAMPLERATE for i in range(len(x1points))]
plt.plot(t, x1points2, color='blue')
plt.xlabel('time (s)', fontsize=12)
plt.ylabel('I -- xchannel 10R(mA)', fontsize=12)
plt.axis([0, idatanum2/SAMPLERATE, -1000000 * KKK , 6000000 * KKK ])  # 1KHz 10S SHORT

plt.savefig(PIC_DIR  + "10R_I.png")
plt.show()



#----------------------- y channel -----Bridge-----------------

print(y1points)

# ---show y data
plt.ylabel('datay -- ychannel  bridge', fontsize=12)
plt.plot(y1points, color='red')
plt.axis([0, idatanum2, -1000000, 7000000])  # 1KHz 10S SHORT
plt.show()


#---show y vol (mv)
y1points = np.array(y1points, dtype=np.float64)
KKK = VREF/1000 /8388608/ 0.82
y1points2 = (y1points * KKK).astype(float)

t = [i / SAMPLERATE for i in range(len(y1points))]
plt.plot(t, y1points2, color='red')
plt.xlabel('time (s)', fontsize=12)
plt.ylabel('V -- ychannel  bridge(v)', fontsize=12)
plt.axis([0, len(y1points2)/SAMPLERATE, -1000000 * KKK, 7000000 * KKK])

plt.savefig(PIC_DIR  + "bridge_v.png")
plt.show()


#---show y Res (R)
y1points3 = y1points2/x1points2 *1000
print(y1points)

t = [i / SAMPLERATE for i in range(len(y1points))]

plt.plot(t, y1points3, color='red')
plt.xlabel('time (s)', fontsize=12)
plt.ylabel('R -- ychannel bridge (Ω)', fontsize=12)
plt.axis([0, len(y1points3)/SAMPLERATE, -10000,10000 ])

plt.savefig(PIC_DIR  + "bridge_R.png")
plt.show()


