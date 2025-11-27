
import os.path


file_name = "d:\\data0.hdf5"
txt_file_name = (file_name[:file_name.rindex('\\')] + "\\" +            #取得文件路径 "d:"
                 'log_' + file_name[file_name.rindex('\\') + 1:-5]      #取得单独文件名 "data0"
                 + '.txt')

print(file_name)      # d:\data0.hdf5
print(txt_file_name)  # d:\log_data0.txt


file_name = r"d:\data0.hdf5"              # r是原始字符串的意思
file_path = os.path.dirname(file_name)    # 取得路径 "d:\"
basename = os.path.basename(file_name)    # 取得文件名（含扩展名） data0.hdf5
file_base = os.path.splitext(basename)[0]  # 取得单独文件名  data0

# 连接路径和文件名，下面有4种方法
# txt_file_name = file_path + "log_" + file_base + ".txt"
# txt_file_name = file_path + f"log_{file_base}.txt"
# txt_file_name = f"{file_path}log_{file_base}.txt"
txt_file_name = os.path.join(file_path, f"log_{file_base}.txt")

print(file_name)     # d:\data0.hdf5

print(file_path)     # d:\
print(basename)      # data0.hdf5
print(file_base)     # data0

print(txt_file_name)  # d:\log_data0.txt

