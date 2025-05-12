
import time
import re
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal

x1points = []
y1points = []
z1points = []

DATAFILE1=".\\data01.dat"
DATAFILE2=".\\data02.txt"

f1=open(DATAFILE1,"rb")
f2=open(DATAFILE2,"w")

idatanum = 0
idatanum2 = 0

try:
    while True:
        if idatanum <= 10000:
            idatanum += 1
            received_data = f1.read(10)
            if not received_data:
                break
            print(received_data)
            # print(idatanum)

            # if received_data[:1] == b'\xaa':
            if received_data[0] == 0xaa:
               print("x1 ", int.from_bytes(received_data[1:4], "big", signed="True"), file=f2)

               x1points.append(int.from_bytes(received_data[1:4], byteorder='big', signed="True"))
               y1points.append(int.from_bytes(received_data[4:7], byteorder='big', signed="True"))
               z1points.append(int.from_bytes(received_data[7:10], byteorder='big', signed="True"))

               idatanum2 +=1
               # print(idatanum2)

        else:
            break

    f1.close()
    f2.close()

    plt.plot(x1points, color='red')
    plt.plot(y1points, color='green')
    plt.plot(z1points, color='blue')
    plt.axis([0,100,-350000, 60000])
    plt.show()
    
    # apply Walch power function to raw ADC data set  
    fft_len = 1024 * 8
    xF, spectrum = scipy.signal.welch(x1points, fs=500, nperseg=fft_len, noverlap=0)       
    freq_resp = 20*(np.log10(np.sqrt(spectrum)))


    ax = plt.subplot()
    plt.title('I3C Captured Data Spectral Plot')
    ax.plot(xF,freq_resp, color='black', linewidth=1) # plot raw spectral data
    #ax.plot(limited_freqs, n_floor, color='red', linewidth=1) # plot raw spectral data
    ax.set_xscale('log')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('X-Channel Output Data [dB]')
    plt.grid(visible=True, which='both', axis='both')
    plt.axis([1, 250, 0,120])
    plt.grid(which='major', color='black', linestyle='-', linewidth = 0.75)
    plt.grid(which='minor', color='black', linestyle='-', linewidth = 0.25)

    plt.show()   

except FileNotFoundError:
    print("Error: data01.dat file not found。")
except Exception as e:
    print(f"An unknown error occurred：{e}")
