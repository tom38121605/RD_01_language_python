
x1points = []

DATAFILE1=".\\01.dat"
DATAFILE2=".\\data02.txt"

f1=open(DATAFILE1,"rb")
f2=open(DATAFILE2,"w")

while True:

    received_data = f1.read(4)

    if not received_data:
        break

    # for byte in received_data:
    #     hex_str =  f"{byte:02X}"
    #     print("十六进制: ", hex_str)

    hex_list = []   #hex_list 只保存一行，打印后，在接收第二行前，会把第一行清空
    for byte in received_data:
        hex_byte = f"{byte:02X}"  # 单个字节转两位十六进制
        hex_list.append(hex_byte)  # 收集到列表：['AA', '42', '77', '48']

    # hex_str = ' '.join(hex_list)

    print("十六进制: ", hex_list)  # 输出： ['AA', '42', '77', '48']
    # print("十六进制: ", hex_str)  # 输出：十六进制:  AA 42 77 48

    if received_data[0] == 0xaa:
        print("x1 ", int.from_bytes(received_data[1:4], "big", signed="True"), file=f2)
        x1points.append(int.from_bytes(received_data[1:4], byteorder='big', signed="True"))

f1.close()
print(x1points)

