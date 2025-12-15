import xlrd
import xlwt
from xlutils.copy import copy
import os

print("start")

base_file = "班级成绩.xls"

"""读取基础文件，计算总分、按总分降序排序，生成待美化文件"""
# 1. 读取基础文件数据
old_wb = xlrd.open_workbook(base_file, formatting_info=True)
old_ws = old_wb.sheet_by_index(0)

# 2. 提取数据并计算总分
score_data = []
# 读取表头（追加"总分"列）
headers = old_ws.row_values(0) + ["总分"]

# 读取学生数据并计算总分
for row in range(1, old_ws.nrows):
    name, chinese, math, english = old_ws.row_values(row)
    total = chinese + math + english  # 计算总分
    score_data.append([name, chinese, math, english, total])

# 3. 按总分降序排序（总分相同按语文降序）
score_data.sort(key=lambda x: (-x[4], -x[1]))

# 4. 生成待美化文件（仅排序+总分，无格式）
new_wb = xlwt.Workbook(encoding="utf-8")
new_ws = new_wb.add_sheet("成绩表（排序后）", cell_overwrite_ok=True)

# 写入新表头
for col, header in enumerate(headers):
    new_ws.write(0, col, header)

# 写入排序后的数据
for row, student in enumerate(score_data, start=1):
    for col, value in enumerate(student):
        new_ws.write(row, col, value)

# 5. 保存待美化文件
to_be_beautiful_file = "班级成绩_已排序.xls"
new_wb.save(to_be_beautiful_file)
print(f"✅ 数据处理完成（求和+排序），待美化文件生成：{to_be_beautiful_file}")


