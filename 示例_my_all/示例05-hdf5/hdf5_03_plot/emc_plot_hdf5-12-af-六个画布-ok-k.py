
import h5py
import numpy as np
import matplotlib.pyplot as plt
import sys
import os.path
import math

# file_name = r"d:\\data0-org.hdf5"
file_name = f"data0.hdf5"
data_file = h5py.File(file_name, 'r')
test_regions = np.array([[0,-1]])

print("file=" + data_file.filename)

pad_seconds = 5


# #------------------遍历group和数集---------------------------------------
# for device in data_file.values():  # device是group
#     print(f'group名：{device.name}')
#     for ds in device.values():  # ds是数集
#         print(f"数据集名：{os.path.basename(ds.name)}")
#         # print(f"{ds[:2]}")
# #------------------遍历group和数集---------end------------------------------

#功能：对x里面的值, 依次相邻两个相减得到对应的差值列表，结合x_max修正后,返回修正后的差值列表AAA
def rolling_bidirection_diff(x, x_max = 0 ):

    type = np.int64 if np.issubdtype(x.dtype, np.integer) else np.double
    x_ax = np.array(x, dtype=type)        # 把数集Device_3528137102_1/Timestamp，按int64 重新生成一新数集x_ax
    # print("数据集形状：", x_ax.shape)      # 输出该数集的行列数和维度， (17704, 1)
    # print("数据集数据类型：", x_ax.dtype)   # 输出该数集的内容，uint16
    # print( x_ax[:])

    diff = x_ax[1:] - x_ax[:-1]  # 相邻两个数相减，后数减去前数的所有差值，组成一个新的是数组 diff
    under = diff < (-x_max/2)   #把diff的每个元素和-2^16比较，得出一个全是 True/False 的数组存到under里 (1表示异常，需要后续修正)
    over = diff > x_max/2   # 把diff的每个元素和2^16比较，得出一个全是 True/False 的数组存到over里 (1表示异常，需要后续修正)

    AAA = diff + under * x_max - over * x_max  # 修正算法，负值超限则加2^32,正值超限则减2^32 (具体证明忽略跳过)

    return AAA
    # return diff

# 功能：对所有的列，即x，y，z取得滑动平均值，然后合并成一个新的二维数组
# 参数：position, 20
def moving_average_3d(data, window_size):
    # Ensure the input is a 2D NumPy array with 3 columns for 3D coordinates
    data = np.array(data, dtype=float)
    # print("\ndata=", data[:3])
    # print("data=", np.shape(data))  # (17704, 1, 3)  //17704层，1行，3列 easy

    AAA = np.ones(window_size) / window_size
    # Apply the moving average separately for each dimension (x, y, z)
    x_smooth = np.convolve(data[:, 0, 0], AAA, mode='valid')   # 后面的0表示x列，前面的:表示所有的x列  easy
    y_smooth = np.convolve(data[:, 0, 1], AAA, mode='valid')   # 后面的1表示y列，前面的:表示所有的y列  easy
    z_smooth = np.convolve(data[:, 0, 2], AAA, mode='valid')   # 后面的2表示z列，前面的:表示所有的z列  easy

    # Stack the smoothed x, y, z back into a 2D array again
    smoothed_data = np.stack((x_smooth, y_smooth, z_smooth), axis=-1) # 把三个独立的n行1列的数组，合并成一个 n行3列的二维数组                                                                     # -1是把所有的指列合并

    # print("\n smoothed_data=", smoothed_data[:3])
    # print("\n shapesmoothed_data=", np.shape(smoothed_data))  # (17685, 3)  //117685行，3列 easy

    return smoothed_data

# 功能：取压缩平均值
# 参数：smoothed_position，5000
def downsample_average(data, chunk_size=1000):
    # Ensure the input is a 2D NumPy array with 3 columns for 3D coordinates
    data = np.array(data, dtype=float)
    print("\ndata=", data[:3])
    print("\nshape-data=", np.shape(data))  # (17685, 3)  //117685行，3列 easy

    # Calculate the number of complete chunks
    num_chunks = len(data) // chunk_size

    # Reshape each dimension separately, apply averaging for complete chunks
    x_avg = np.mean(data[:num_chunks * chunk_size, 0].reshape(-1, chunk_size), axis=1)
    y_avg = np.mean(data[:num_chunks * chunk_size, 1].reshape(-1, chunk_size), axis=1)
    z_avg = np.mean(data[:num_chunks * chunk_size, 2].reshape(-1, chunk_size), axis=1)

    # Handle any remaining points (the last incomplete chunk)
    if len(data) % chunk_size != 0:
        remainder_mean = np.mean(data[num_chunks * chunk_size:], axis=0)
        x_avg = np.append(x_avg, remainder_mean[0])
        y_avg = np.append(y_avg, remainder_mean[1])
        z_avg = np.append(z_avg, remainder_mean[2])

    # Stack the averaged x, y, z back into a 2D array
    downsampled_data = np.stack((x_avg, y_avg, z_avg), axis=-1)

    return downsampled_data

#参数： device, t0, test_regions   //3222425134
def process_device(device, t0, time_array:np.ndarray):

    if(device.name != "/Device_3528137102_1"):
        return

    print("device=", device.name)
    print("time_array=", time_array)   #[[ 0 -1]]   //2维数组，只有1个列表元素

    if "Timestamp" in device:
       timestamp_full = device['Timestamp']    # 取得该 device中的 Timestamp数集
       print(timestamp_full.name)              # Device_3528137102_1/Timestamp
       print(timestamp_full[:2])
    else:
       print("no Timestamp")
       # sys.exit()
       return

    #功能：对timestamp_full里面的时间值, 相邻两个时间差，修正后,存入timestamp_delta中  //easy
    timestamp_delta = rolling_bidirection_diff(timestamp_full, 4294967296)   # 2^32
    print("\ntimestamp_delta=", timestamp_delta[:3] )

    #在timestamp_delta的前面，插入一个元素 timestamp_full[0, 0] - t0
    time_passed1 = np.insert(timestamp_delta, 0, (timestamp_full[0, 0] - t0))
    print( "passed1", time_passed1[:3] )   # [0 15984 15984 ...]

    # same length of original timestamp, starting from t0 across all devices
    time_passed2 = np.cumsum(time_passed1)
    print( "passed2", time_passed2[:3] )    # [0 15984 31968 ...]

    # print('start time={} end time={} samples={}'.format(time_passed2[0] / 16000000.0, time_passed2[-1] / 16000000.0,
    #       np.shape(timestamp_full)[0]))

    print( "start time=", time_passed2[0] / 16000000.0 )
    print( "end time=", time_passed2[-1] / 16000000.0 )
    print( "samples=", np.shape(timestamp_full)[0] )


    AAA = np.shape(time_array)  # [[ 0 -1]]  --> (1, 2)   //1行2列
    print("AAA=",AAA)    #(1, 2)

    BBB =range(AAA[0])  # range(1)  等价于 range(0,1) 或 range(0,1,1)
    print("BBB=",BBB)    # [0]

    for row in BBB:   # 0
        print(row)  # 0
        start_clock = max( (time_array[row,0] - pad_seconds) * 16000000.0, 0) # 0
        end_clock = time_passed2[-1]  # 288271440

        print("start_clock=", start_clock)
        print("end_clock=", end_clock)

        if time_array[row, 1] > 0 and time_array[row, 1] > time_array[row, 0]:  #no
            # print("yes")
            end_clock = min((time_array[row,1] + pad_seconds) * 16000000.0, time_passed2[-1])

        print("timepass2=",time_passed2)  # add

        step1 = time_passed2 >= start_clock
        print("step1=", step1)

        step2=np.where(step1)    # step2是二维数组，只有一个元素
        print("step2=", step2)

        start_idx = step2[0][0]
        end_idx = np.where(time_passed2 >= end_clock)[0][0] + 1
        print("start_idx=", start_idx)
        print("end_idx=", end_idx)

        delta_start_idx = max(start_idx - 1, 0)
        delta_end_idx = end_idx - 1
        print("delta_start_idx=", delta_start_idx)
        print("delta_end_idx=", delta_end_idx)

        timestamp = time_passed2[start_idx:end_idx,...]  #[20000:]   //相当于 timestamp = time_passed2[:]
        print("timestamp=", timestamp)

        theta = device['Theta'][start_idx:end_idx,...]  # 相当于 device['Theta'][0:17704, :, :]
        indicator = device['Indicator'][start_idx:end_idx,...] #[20000:]
        position = device['Position'][start_idx:end_idx,...] #[20000:]
        mag = device['Mag'][start_idx:end_idx,...] #[20000:]

        print("theta=", theta[:3])
        # print("indicator=", indicator[:3])
        print("position=", position[:3])
        # print("mag=", mag[:3])

        # print("shape-timestamp=", np.shape(timestamp) )    # (17704,)       //17704列  easy
        # print("shape-theta=", np.shape(theta) )            # (17704, 1)     //17704行， 1列  easy
        print("shape-position=", np.shape(position) )      # (17704, 1, 3)  //17704层， 1行，3列 easy
        # print("shape-mag=", np.shape(mag) )      # (17704, 3, 3)  //17704层， 3行，3列 easy

        # smooth position and splice it into chunks of 1000
        smoothed_position = moving_average_3d(position, 20)
        print("shape-smoothed_position=", np.shape(smoothed_position))  # (17685, 3)  //117685行，3列 easy

        downsampled_position = downsample_average(smoothed_position, 5000)  # 把5000个数取平均值变成一个数
        print("downsampled_position=", downsampled_position[:3])    # add
        print("shape-downsampled_position=", np.shape(downsampled_position))  # (4, 3)  //4行，3列 easy

        position_delta_vector = downsampled_position[-1]-downsampled_position[0]
        position_delta_magnitude = np.linalg.norm(downsampled_position[0]-downsampled_position[-1])  #直线距离 （勾股定理）
        print("position_delta_vector=", position_delta_vector[:])
        print("position_delta_magnitude=", position_delta_magnitude)

        # check timestamp
        delta = timestamp_delta[delta_start_idx:delta_end_idx,...]  # 相当于 timestamp_delta[0:17703, :, :]
        print("timestamp_delta=", timestamp_delta[:5])
        print("delta=", delta[:5])

        delta_values, delta_counts = np.unique(delta, return_counts=True)
        ts_events = np.logical_or(delta < 15980, delta > 10 * 15980)   # []
        # ts_events = np.logical_or(delta < 15980, delta > 6 * 15980)       # [11831 12827 14603]
        ts_event_idx = np.where(ts_events)[0]

        print("delta_values=", delta_values[:])
        print("delta_counts=", delta_counts[:])
        print("ts_events=", ts_events)
        print("ts_event_idx=", ts_event_idx)


        # don't add 1 to index, this gives us the timestamp at the beginning of the event
        # (next sample generates the event)

        try:
            ts_events_s = timestamp[ts_event_idx] / 16000000.0
            print(f'Timestamp events:{ts_events_s}')
            print(f'Timestamp events packets loss:{delta[ts_event_idx].flatten()/15984}')
        except Exception as e: print(e)

        fig, ax = plt.subplots(6, 1, figsize = (10, 8))  # 创建一个画布，6行1列六个子图，画布大小10x8
        fig.tight_layout(pad=3)   # 画布间距 3
        fig.suptitle('device={} time={}'.format(device.name, time_array[row]))  #  [0 -1], 所有时间范围
        ax[0].plot(delta, '.')  #在y坐标上，以x对应的delta值画"."
        ax[0].title.set_text("Timestamp Deltas"); ax[0].set_xlabel("Samples"); ax[0].set_ylabel("Delta B Timestamps")
        print(f' Timestamp deltas:{delta_values}\n counts:{delta_counts}')
        # plt.show()

        # 功能：对theta里面的角度值, 相邻两个角度差，修正后,存入delta中  //easy
        delta = rolling_bidirection_diff(theta, 3600)
        delta_values, delta_counts = np.unique(delta, return_counts=True)  # 取得唯一值的列表，及唯一值对应的重复次数列表
        print("delta_values=", delta_values)
        print("delta_counts=", delta_counts)

        theta_events = np.logical_or(delta < 0, delta > 800)  # 取得每个数据是否越界的真值表（True/False）
        theta_events_idx = np.where(theta_events)[0]   # 取得真值为True的所有矩阵中的位置，这里只有一行，只有列的位置
        # don't add 1 to index, this gives us the timestamp at the beginning of the event
        # (next sample generates the event)
        theta_events_s = timestamp[theta_events_idx] / 16000000.0
        print(f'theta events:{theta_events_s}')

        ax[1].plot(delta, '.')
        ax[1].title.set_text("theta Deltas"); ax[1].set_xlabel("Samples"); ax[1].set_ylabel("Delta Between theta Measurments")

        # plt.show()

        position_centered = position[:, 0, :] - position[0, 0, :]  # 所有层的第0行，减去第0层的第0行，降维得到层与列的二维数组
        downsampled_position_centered = downsampled_position - position[0, 0, :]
        print("position_centered=", position_centered)
        print("downsampled_position_centered=", downsampled_position_centered)

        ax[2].plot(position_centered, '.')
        ax[2].plot(np.linspace(0, len(position_centered) - 1, len(downsampled_position_centered)), downsampled_position_centered, linewidth=4)
        ax[2].title.set_text("Position Change"); ax[2].set_xlabel("Samples"); ax[2].set_ylabel("Position from origin (mm)"); ax[2].legend(['x', 'y', 'z', 'x filtered', 'y filtered', 'z filtered'], loc='right')
        # plt.show()

        ax[3].plot(position[:, 0, :], '.') # 分别把各层的"层"当画布上的x轴坐标，并把第0行的x，y，z维度当y轴坐标，进行画点
        ax[3].title.set_text("Absolute Position"); ax[3].set_xlabel("Samples"); ax[3].set_ylabel("Position from Base Station (mm)")
        # plt.show()

        ax[4].plot(indicator[:, 0, :], '.') # 分别把各层的"层"当画布上的x轴坐标，并把第0行的x，y，z维度当y轴坐标，进行画点
        ax[4].title.set_text("Indicator"); ax[4].set_xlabel("Samples"); ax[4].set_ylabel("Indicator value")
        # plt.show()

        if len(mag[:, 0, :]) > 500:   # 首先降维成2维(层变行，列原样)，然后len表示降维后的行数
            ccc = math.floor(len(mag[:, 0, :])/2) # 对len长度取整数（向下取整）
            aaa= range(ccc-250, ccc+250)
            bbb = mag[:, 0, :][ccc-250:ccc+250]  # 相当于写法mag[0:500,0,:] ，取其中500行（含所有列的数据）
            ax[5].plot(aaa, bbb, '.') # aaa 是一维，bbb 是二维（按列自动分组画点）

            ax[5].title.set_text("Mag"); ax[5].set_xlabel("Samples"); ax[5].set_ylabel("Mag value")
        plt.show()

#         # position_diff_abs = np.abs(position_centered[1:] - position_centered[:-1])
#         regions = contiguous_regions(np.any(np.abs(position_centered)>1, axis=1), 5)
#         print("start_position={}".format(position[0,0,:]))
#         logging.info(f' position over 2mm:{regions}')
#         num_regions = np.shape(regions)[0]
#         fig.savefig(file_name[:file_name.rindex('\\')] + "\\" + 'output_' + device.name[1:] +'_'+file_name[file_name.rindex('\\')+1:-5]+ '.png')
#         if num_regions > 0:
#             fig, ax = plt.subplots(num_regions + 1, 1, figsize = (10, 8))
#             fig.tight_layout(pad=3)
#             fig.suptitle('device={} time={} regions'.format(device.name, time_array[row]))
#             mask = np.ones(np.shape(position_centered)[0], dtype=bool)
#             for i in range(num_regions):
#                 region_end_idx = regions[i,1]
#                 if region_end_idx >= np.shape(position_centered)[0]:
#                     region_end_idx = np.shape(position_centered)[0]-1
#                 logging.info(f'Region start={timestamp[regions[i,0]] / 16000000.0} end={timestamp[region_end_idx] / 16000000.0}')
#                 mask[regions[i,0]:regions[i,1]] = False
#                 ax[i].plot(position_centered[regions[i,0]:regions[i,1]],'.')
#                 ax[i].title.set_text("Region of Deviation >2mm "+str(i)); ax[i].set_xlabel("Samples"); ax[i].set_ylabel("Deviation (mm)")
#             ax[num_regions].plot(position_centered[mask],'.')
#             ax[num_regions].title.set_text("Dataset with >2mm Deviations Removed"); ax[num_regions].set_xlabel("Samples"); ax[num_regions].set_ylabel("Deviation (mm)")
#             fig.savefig(file_name[:file_name.rindex('\\')] + "\\" + 'deviations_' + device.name[1:] +'_'+file_name[file_name.rindex('\\')+1:-5]+ '.png')
#         plt.show()


def main():

    #-------- 每个group的Timestamp的第0行0列值添加到t0_all，最小值给t0，最小值的坐标给t0_idx1 ----------

    t0_all = []
    for device in data_file.values():
        t0_all.append(device['Timestamp'][0, 0])  # 在每个group的Timestamp数集中，取得第0行0列的值，添加到t0_all中

    #t0_all这里是一维数组
    t0_all = np.array(t0_all, dtype=np.int64)  # [3222425134 3222425134 3222425134 3222425134]
    print("t0all ", t0_all)

    t0 = np.min(t0_all)     # 3222425134

    # step1 = t0_all == t0    # 1维数组
    # # print("step1", step1 )   # [ True  True  True  True]
    #
    # step2 = np.where(step1)  # 2维数组
    # # print("step2", step2)    # array([0, 1, 2, 3])
    #
    # t0_idx1 = step2[0]  # 输出：[0, 1, 2, 3]
    # # print('t0_device_idx=', t0_idx1 )

    #-------- 每个group的Timestamp的第0行0列值添加到t0_all，最小值给t0，最小值的坐标给t0_idx1 ---end-------


    for device in data_file.values():  # device是group
        if "Position" in device:
            process_device(device, t0, test_regions)


if __name__ == "__main__":
    main()



