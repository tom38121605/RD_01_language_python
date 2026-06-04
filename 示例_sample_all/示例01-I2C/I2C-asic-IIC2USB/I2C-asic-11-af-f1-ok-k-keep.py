#-*- coding: utf-8 -*-
# sudo apt-get install -y python3-bitarray
import ctypes
import time
import matplotlib.pyplot as plt
from datetime import datetime

#IIC速率
IIC_Rate_100K=						6   #130KHz
IIC_Rate_200K=						7   #204KHz
IIC_Rate_400K=						8   #555KHz

#IIC 寻址模式
IIC_ADDRMOD_7BIT=					0
IIC_ADDRMOD_10BIT=					1

UsbIndex=0
Dir_USB2UARTSPIIICDLL = ".\\USB2UARTSPIIICDLL.dll"
libtest = ctypes.CDLL(Dir_USB2UARTSPIIICDLL)

FIFO= bytes(100)

def debug(*strings):
    if(0):
        for string in strings:
            print(string,end='')
        print("")

def I2C_Write_v2(static_addr,*data):
    debug("********** I2C write")
    temp=[]
    for datum in data:
        temp.append(datum)
    SendBuffer=bytes(temp)
    Result = Is_Send = libtest.IICDirectSend(0,static_addr,SendBuffer,len(SendBuffer),0);
    debug("I2C Write ",''.join('{:02x} '.format(a) for a in SendBuffer))

def I2C_Read_v2 (static_addr,length):
    Buffer=bytes(length)
    Result = libtest.IICDirectRead(0,static_addr,Buffer,length,0);
    debug("I2C Read ",''.join('{:02x} '.format(a) for a in Buffer))
    return Buffer

Is_Open = libtest.OpenUsb(ctypes.c_uint(0))
if (Is_Open<0):
    print("usb fail")
    libtest.CloseUsb(ctypes.c_uint(0))
    exit(1)
    debug("usb open")
else:
    debug("usb open")

Is_True =libtest.ConfigIICParam(IIC_Rate_400K,10000,0)

# f=open(".\\X_data.csv","w")
f1=open(".\\data.txt","w")

I2C_Addr=0x63
print("Set Registers")
I2C_Write_v2(I2C_Addr,0x01,0x01)    # Soft RESET
# I2C_Write_v2(I2C_Addr,0x20,0x85)    # 7/VREF_EN[7],6-5/ctrl_pga_power[1:0],4-2/ctrl_pga_gain[2:0],1/0,0/ctrl_pga_en
# I2C_Write_v2(I2C_Addr,0x20,0x81)    #--set pga  gain to 4x
# I2C_Write_v2(I2C_Addr,0x20,0x85)    #--set pga  gain to 8x
# I2C_Write_v2(I2C_Addr,0x20,0x89)    #--set pga  gain to 16x
I2C_Write_v2(I2C_Addr,0x20,0x91)    #--set pga  gain to 32x
# I2C_Write_v2(I2C_Addr,0x20,0x95)    #--set pga  gain to 64x

I2C_Write_v2(I2C_Addr,0x23,0x00)    # 7/Vref_ctl,5/ctrl_en_test_iadc,4/ctrl_en_opamp_lp2_iadc,3/ctrl_en_opamp_lp1_iadc,2/ctrl_en_bias_lp_iadc,1/ctrl_en_offset_cal_iadc,0/ctrl_en_chop_sdm
# I2C_Write_v2(I2C_Addr,0x23,0x80)    # set vref to 2.5v

# I2C_Write_v2(I2C_Addr,0x2a,0x83)    # 7/DTEST_EN,2/Sel2p5m,1/SCL_PU,0/SDA_PU#
I2C_Write_v2(I2C_Addr,0x2a,0x87)    # set adc clock div by 10

I2C_Write_v2(I2C_Addr,0x24,0xFF)    # 7-4/SEL2_Y,3-0/SEL1_X
I2C_Write_v2(I2C_Addr,0x25,0x0F)    # 3-0/SEL3_Z
I2C_Write_v2(I2C_Addr,0x26,0x01)    # 3-0/RUN_NUM_CONVERTER[11:8]
I2C_Write_v2(I2C_Addr,0x27,0x00)    # 7-0/RUM_NUM_CONVERTER[7:0], 5-3/ClkDiv[2:0]
I2C_Write_v2(I2C_Addr,0x28,0x28)    # 5-0/REG_NUM_SET[6:0]
I2C_Write_v2(I2C_Addr,0x29,0x20)    # 5-0/REG_NUM_INIT[5:0]

# I2C_Write_v2(I2C_Addr,0x1e,0x0)     # DTESTO probe control
I2C_Write_v2(I2C_Addr,0x1e,0x02)     # set DTESTO pin to show adc clock

# Dump the register content
for reg in range(0x20,0x31):
    I2C_Write_v2(I2C_Addr,reg)
    print("REG{:x} value 0x{:x}".format(reg,I2C_Read_v2(I2C_Addr,1)[0]))

input ("Hit return to start")

Display_ADC_Data=0
start = time.time()
measure=0.0
Temp_degree=[1]
x1points=[]
y1points=[]
z1points=[]

trial=0
while(1):
    command=0b0000_0011
#    command=0b0000_0001  # Read Temp Only
    I2C_Write_v2(I2C_Addr,0x00,command) # Trigger measure
    myobj = datetime.now()
    trial=trial+1
    time.sleep(0.01)
    Sample_count=[((command &0x1) +((command >>1 ) & 0x1)*3),(((command &0x1) +((command >>1 ) & 0x1)*3)*2)] [(command>>6)==0b11]
    FIFO=I2C_Read_v2(I2C_Addr,Sample_count*3)
    
# Display the ADC return result, comment it out to disable the extra I2C command for easy probing
    if(Display_ADC_Data):
        print("I2C Read ",''.join('{:02x} '.format(a) for a in FIFO),end='')
        if (Sample_count==1):
            print("T1:",int.from_bytes(FIFO[0:3],"big",signed="True"))
        elif (Sample_count==2):
            print("T1:",int.from_bytes(FIFO[0:3],"big",signed="True")\
                ,"T2:",int.from_bytes(FIFO[3:6],"big",signed="True"))
        elif (Sample_count==3):
            print("X1:",int.from_bytes(FIFO[0:3],"big",signed="True")\
                ,"Y1:",int.from_bytes(FIFO[3:6],"big",signed="True")\
                ,"Z1:",int.from_bytes(FIFO[6:9],"big",signed="True"))
        elif (Sample_count==4):
            print("X1:",int.from_bytes(FIFO[0:3],"big",signed="True")\
                ,"Y1:",int.from_bytes(FIFO[3:6],"big",signed="True")\
                ,"Z1:",int.from_bytes(FIFO[6:9],"big",signed="True")\
                ,"T1:",int.from_bytes(FIFO[9:12],"big",signed="True"))
        elif (Sample_count==6):
            print("X1:",int.from_bytes(FIFO[0:3],"big",signed="True")\
                ,"Y1:",int.from_bytes(FIFO[3:6],"big",signed="True")\
                ,"Z1:",int.from_bytes(FIFO[6:9],"big",signed="True")\
                ,"X2:",int.from_bytes(FIFO[9:12],"big",signed="True")\
                ,"Y2:",int.from_bytes(FIFO[12:15],"big",signed="True")\
                ,"Z2:",int.from_bytes(FIFO[15:18],"big",signed="True"))    
        elif (Sample_count==8):
            print("X1:",int.from_bytes(FIFO[0:3],"big",signed="True")\
                ,"Y1:",int.from_bytes(FIFO[3:6],"big",signed="True")\
                ,"Z1:",int.from_bytes(FIFO[6:9],"big",signed="True")\
                ,"T1:",int.from_bytes(FIFO[9:12],"big",signed="True")\
                ,"X2:",int.from_bytes(FIFO[12:15],"big",signed="True")\
                ,"Y2:",int.from_bytes(FIFO[15:18],"big",signed="True")\
                ,"Z2:",int.from_bytes(FIFO[18:21],"big",signed="True")\
                ,"T2:",int.from_bytes(FIFO[21:24],"big",signed="True")\
                ,(int.from_bytes(FIFO[0:3],"big",signed="True")+int.from_bytes(FIFO[12:15],"big",signed="True"))/2\
                ,(int.from_bytes(FIFO[3:6],"big",signed="True")+int.from_bytes(FIFO[15:18],"big",signed="True"))/2)    
    else:
            print(".",end='')
    
    if (Sample_count==1):
        print("{0:0>4d}-{1:0>2d}-{2:0>2d}_{3:0>2d}:{4:0>2d}:{5:0>2d}.{6:0>3d},{7},{8:.2f},{9:.2f}".format(myobj.year,myobj.month,myobj.day,int(myobj.strftime("%H")),myobj.minute,myobj.second,int(myobj.microsecond/1000),int.from_bytes(FIFO[0:3],"big",signed="True"),measure,int.from_bytes(Temp_degree,"big")),file=f1)
    elif (Sample_count==3):
        print("X1:",int.from_bytes(FIFO[0:3],"big",signed="True")\
            ,"Y1:",int.from_bytes(FIFO[3:6],"big",signed="True")\
            ,"Z1:",int.from_bytes(FIFO[6:9],"big",signed="True")\
            ,file=f1)
    elif (Sample_count==4):
        print("", int.from_bytes(FIFO[0:3], "big", signed="True"), file=f1)
        # print("", int.from_bytes(FIFO[3:6], "big", signed="True"), file=f1)
        # print("", int.from_bytes(FIFO[6:9], "big", signed="True"), file=f1)

        # print("X1:",int.from_bytes(FIFO[0:3],"big",signed="True")\
        #     ,"Y1:",int.from_bytes(FIFO[3:6],"big",signed="True")\
        #     ,"Z1:",int.from_bytes(FIFO[6:9],"big",signed="True")\
        #     ,"T1:",int.from_bytes(FIFO[9:12],"big",signed="True")\
        #     ,file=f1)
        x1points.append(int.from_bytes(FIFO[0:3],"big",signed="True"))
        y1points.append(int.from_bytes(FIFO[3:6],"big",signed="True"))
        z1points.append(int.from_bytes(FIFO[6:9],"big",signed="True"))

    elif (Sample_count==8):
            print("X1:",int.from_bytes(FIFO[0:3],"big",signed="True")\
            ,"Y1:",int.from_bytes(FIFO[3:6],"big",signed="True")\
            ,"Z1:",int.from_bytes(FIFO[6:9],"big",signed="True")\
            ,"T1:",int.from_bytes(FIFO[9:12],"big",signed="True")\
            ,"X2:",int.from_bytes(FIFO[12:15],"big",signed="True")\
            ,"Y2:",int.from_bytes(FIFO[15:18],"big",signed="True")\
            ,"Z2:",int.from_bytes(FIFO[18:21],"big",signed="True")\
            ,"T2:",int.from_bytes(FIFO[21:24],"big",signed="True"),file=f1)
    end = time.time()
    length = end - start
    if (length > 5):
        pass
        f1.close()
        break

plt.plot(x1points)
plt.show()
libtest.CloseUsb(ctypes.c_uint(0))
