import xlrd
import xlwt
from xlutils.copy import copy
import os

print("start")

# ===================== 第一步：生成基础成绩文件（班级成绩.xls） =====================
# def generate_base_score_file():

"""生成原始班级成绩文件（无格式、仅基础数据）"""
# 1. 创建工作簿
wb = xlwt.Workbook(encoding="utf-8")
ws = wb.add_sheet("成绩表", cell_overwrite_ok=True)

# 2. 写入表头和原始数据
headers = ["姓名", "语文", "数学", "英语"]
students = [
    ["张三", 85, 92, 88],
    ["李四", 90, 86, 95],
    ["王五", 78, 94, 82],
    ["赵六", 93, 89, 91],
    ["孙七", 88, 79, 85],
    ["周八", 91, 90, 87]
]

# 写入表头
for col, header in enumerate(headers):
    ws.write(0, col, header)

# 写入学生数据
for row, student in enumerate(students, start=1):
    for col, value in enumerate(student):
        ws.write(row, col, value)

# 3. 保存基础文件
base_file = "班级成绩.xls"

print("save...")

wb.save(base_file)
print(f"✅ 基础文件生成完成：{base_file}")
# return base_file