from os.path import expanduser
import h5py
import os.path
import glob
import matplotlib.pyplot as plt
from tkinter import messagebox


# DATAFILE1 = "data0.hdf5"

DATAFILE1=""
if(DATAFILE1==""):
    dat_files = glob.glob("*.hdf5")
    file_num = len(dat_files)
    if file_num != 1:
        print("multi files, or no file")
        sys.exit()

    DATAFILE1=dat_files[0]

DATAFILE2=".\\data1.txt"
DATAFILE3=".\\data2.txt"
DATAFILE4=".\\data3.txt"

f1 = h5py.File(expanduser(DATAFILE1), 'r')

f2=open(DATAFILE2,"w")
f3=open(DATAFILE3,"w")
f4=open(DATAFILE4,"w")

x1points = []
y1points = []
z1points = []

idatanum2=0

def main():
    global idatanum2

    # dataset = f1['/Device_3528137102_0/Theta']
    dataset = f1['/Logging_Test_COM3_11763_ADC_Sampler_3ch/DeviceGroup_0/Device_0/IC_0/Sensor_0/Data']


    data = dataset[:]
    # print( data)

    for num_list in data:
        number0 = num_list[0]
        number1 = num_list[1]
        number2 = num_list[2]

        f2.write(f"{number0}\n")
        f3.write(f"{number1}\n")
        f4.write(f"{number2}\n")

        x1points.append(number0)
        y1points.append(number1)
        z1points.append(number2)

        idatanum2 += 1


    f1.close()
    f2.close()
    f3.close()
    f4.close()


    print(y1points)
    plt.plot(y1points, color='red')

    print("num =", idatanum2)
    # if (idatanum2 != 100000):
    #     messagebox.showinfo("num", idatanum2)

    plt.axis([0, 100000, 6820000, 6880000])  # 1KHz 10S SHORT

    plt.show()

if __name__ == "__main__":

    main()


