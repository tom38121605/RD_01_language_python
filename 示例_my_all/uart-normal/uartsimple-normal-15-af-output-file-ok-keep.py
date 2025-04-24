import serial
import time
import serial.tools.list_ports
import threading
import re
import matplotlib.pyplot as plt

# text = "aa,bb;123"
# pattern = r"[;, ]"
# result = re.split(pattern, text)
# print("splited:", result)

ports=serial.tools.list_ports.comports()
for port, desc, hwid in sorted(ports):
    # print(f"{port}: {desc} ({hwid})")
    print(f"{port}: {desc} ")

x1points = []
y1points = []
z1points = []

f1=open(".\\data.txt","w")

try:
    ser = serial.Serial('COM17', 1000000, timeout=1)
    print(f"Successfully connected: {ser.name}")

    start_time = time.time()

    while True:

        if ser.in_waiting > 0:
            received_data = ser.read(ser.in_waiting)
            print(f"received data: {received_data}")

            if len(received_data) >= 3 and received_data[:2] == b'\xaa\x0c':
                print("x1 ", int.from_bytes(received_data[2:5], "big", signed="True"), file=f1)

                x1points.append(int.from_bytes(received_data[2:5], byteorder='big',signed="True"))
                y1points.append(int.from_bytes(received_data[5:8], byteorder='big',signed="True"))
                z1points.append(int.from_bytes(received_data[8:11], byteorder='big',signed="True"))

            ser.write(received_data)

        if time.time() - start_time >= 5:
            break

    # if x1points:
    plt.plot(x1points)
    plt.plot(y1points)
    plt.plot(z1points)
    # plt.title('Received Data Plot')
    # plt.xlabel('Data Index')
    # plt.ylabel('Data Value')
    plt.show()

except serial.SerialException as e:
    print(f"uart connect err: {e}")
except KeyboardInterrupt:
    print("The program was interrupted by the user。")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("uart connection closed")

