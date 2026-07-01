
# import sys
# import numpy as np
# import matplotlib.pyplot as plt
# import h5py
# from os.path import expanduser
# import os.path

from datetime import datetime, timedelta
import xlrd
import xlwt
from collections import defaultdict
import re



# ---------------------------------------------------------------


workbook = xlrd.open_workbook("230.xls")
total_sheet = workbook.nsheets

position_dict = {}

# for sheet_idx in range(total_sheet):
#     sheet = workbook.sheet_by_index(sheet_idx)
#     print(f"第{sheet_idx+1}个sheet，原名称：{sheet.name}，列数：{sheet.ncols}")

sheet = workbook.sheet_by_index(0)

for row_idx in range(1, sheet.nrows):
    code = sheet.cell_value(row_idx, 0)  # “代码” 列
    name = sheet.cell_value(row_idx, 1)  # “名称” 列
    far_up_val = sheet.cell_value(row_idx, 7)  # “远Z” 列
    far_down_val = sheet.cell_value(row_idx, 8)  # “远D” 列

    print(code,name,far_up_val,far_down_val)



