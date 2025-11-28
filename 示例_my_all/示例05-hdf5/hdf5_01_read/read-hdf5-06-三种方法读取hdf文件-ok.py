from os.path import expanduser
import h5py
import os.path


#遍历打印出所有的group及其里面的dataset
def main():

    file_path = r"data0.hdf5"
    with h5py.File(file_path, 'r') as f:

        last_dataset = None
        data=[]

        def get_dataset_name(name, obj):
            nonlocal last_dataset
            nonlocal data

            if isinstance(obj,h5py.Group):
                print(f"Group路径：----- {name} -----")
            elif isinstance(obj, h5py.Dataset): # and name.endswith("Theta"):
                # print(f"数据集名称：{name.split('/')[-1]}")
                print(f"数据集名称：{os.path.basename(name)}")
                last_dataset = os.path.basename(name)
                data = obj[:]

        f.visititems(get_dataset_name)  #把hdf5中每个对象的name和obj传给函数get_dataset_name

        if last_dataset:
           print("数据集名称2：", last_dataset)
           print("数据集内容：", data)

#打印出所有的group，再打印数集Device_3528137102_0/Theta的内容，形状，数据类型
def main2():

    file_name = "data0.hdf5"
    data_file = h5py.File(expanduser(file_name), 'r')
    print("文件中的group：", data_file.keys())


    dataset = data_file['/Device_3528137102_0/Theta']      #取得数集的dataset
    data = dataset[:]  #取得数集的所有内容  # 推荐用 [:]，兼容所有 HDF5 版本

    print("数据集内容：", data)               # 输出该数集的所有内容
    print("数据集形状：", dataset.shape)      # 输出该数集的行列数和维度， (17704, 1)
    print("数据集数据类型：", dataset.dtype)   # 输出该数集的内容，uint16

    data_file.close()


# 打印出所有含有数集Position的group ，再根据该group取得 里面的Timestamp数集，打印出Timestamp中的所有数据
def main3():

    file_name = "data0.hdf5"
    data_file = h5py.File(expanduser(file_name), 'r')

    # print("keys=" + f'{data_file.keys()}')  # keys返回 对象的字符串名称
    print("文件中的group：", data_file.keys())

    for device in data_file.values():  # device是group或dataset
        if "Position" in device:
            print(f' device:{device.name}')
            timestamp_full = device['Timestamp']
            print(timestamp_full)
            print(timestamp_full[:])


if __name__ == "__main__":
    # main()
    # main2()
    main3()

