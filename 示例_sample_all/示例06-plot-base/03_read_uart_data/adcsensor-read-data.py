
import time
import re
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal

#add .dat check
import glob
import sys

#add msgbox
import tkinter as tk
from tkinter import messagebox


DEFINES = \
{
    "MODE_X": True,
    "MODE_XYZ": False,
}

# DEFINES = \
# {
#     "MODE_X": False,
#     "MODE_XYZ": True,
# }

x1points = []
y1points = []
z1points = []

# DATAFILE1=".\\data01.dat"

DATAFILE1=""
if(DATAFILE1==""):
    dat_files = glob.glob("*.dat")
    file_num = len(dat_files)
    if file_num != 1:
        print("multi files, or no file")
        sys.exit()

    DATAFILE1=dat_files[0]

DATAFILE2=".\\data02.txt"

f1=open(DATAFILE1,"rb")
f2=open(DATAFILE2,"w")

idatanum = 0
idatanum2 = 0

def defined(macro_name):
    is_defined = macro_name in DEFINES
    is_enabled = DEFINES[macro_name]
    return is_defined and is_enabled   # 可优化成只有is_defined

try:

    # -------------------------------------- x -----------------------------------

    if defined("MODE_X"):

        while True:
            if idatanum <= 100000:   # 1KHz 10S GND
            # if idatanum <= 1000:      #normal data
                idatanum += 1
                received_data = f1.read(4)
                if not received_data:
                    break

                # print(received_data)
                hex_list = []
                for byte in received_data:
                    hex_byte = f"{byte:02X}"
                    hex_list.append(hex_byte)  # ['AA', '42', '77', '48']

                # print(hex_list)
                # print(idatanum)

                # if received_data[:1] == b'\xaa':
                # if received_data[0] == 0xaa:
                if received_data[0] in (0xaa, 0xbb):
                   print("", int.from_bytes(received_data[1:4], "big", signed="True"), file=f2)

                   x1points.append(int.from_bytes(received_data[1:4], byteorder='big', signed="True"))

                   idatanum2 +=1
                   # print(idatanum2)

            else:
                break

        f1.close()
        f2.close()

        print(x1points)
        print("num =", idatanum2)
        if(idatanum2!=100000):
           messagebox.showinfo("num", idatanum2)

        ax = plt.subplot()
        # ax.set_facecolor('darkseagreen')
        ax.plot(x1points, color='red')

        plt.axis([0,100000, -200000, 200000])  # 1KHz 10S SHORT
        # plt.axis([0,100,100000, 105000])   #lit SHORT
        # plt.axis([0,200,-10000000, 10000000])    #normal data  2.4v + 200mv

        plt.show()

    # -------------------------------------- x --- end -----------------------------

    # -------------------------------------- xyz ---------------------------------

    elif defined("MODE_XYZ"):

        while True:
            if idatanum <= 100000:  # 1KHz 10S GND
            # if idatanum <= 10000:      #normal data
                idatanum += 1
                received_data = f1.read(10)
                if not received_data:
                    break

                # print(received_data)
                hex_list = []
                for byte in received_data:
                    hex_byte = f"{byte:02X}"
                    hex_list.append(hex_byte)  # ['AA', '42', '77', '48']

                # print(hex_list)
                # print(idatanum)

                # if received_data[:1] == b'\xaa':
                # if received_data[0] == 0xaa:
                if received_data[0] in (0xaa, 0xbb):
                    print("", int.from_bytes(received_data[1:4], "big", signed="True"), file=f2)

                    x1points.append(int.from_bytes(received_data[1:4], byteorder='big', signed="True"))
                    y1points.append(int.from_bytes(received_data[4:7], byteorder='big', signed="True"))
                    z1points.append(int.from_bytes(received_data[7:10], byteorder='big', signed="True"))

                    idatanum2 += 1
                    # print(idatanum2)

            else:
                break

        f1.close()
        f2.close()

        print(x1points)
        plt.plot(x1points, color='red')
        plt.plot(y1points, color='green')
        plt.plot(z1points, color='blue')

        plt.title('x -- red,  y -- green,  z -- blue ')

        plt.axis([0, 100000, -8000000, 8000000])  # 1KHz 10S SHORT
        # plt.axis([0,5000,-2000, 2000])   #lit SHORT
        # plt.axis([0,200,-10000000, 10000000])    #normal data  2.4v + 200mv

        plt.show()

    # -------------------------------------- xyz ----end--------------------------

except FileNotFoundError:
    print("Error: data01.dat file not found。")
except Exception as e:
    print(f"An unknown error occurred：{e}")
