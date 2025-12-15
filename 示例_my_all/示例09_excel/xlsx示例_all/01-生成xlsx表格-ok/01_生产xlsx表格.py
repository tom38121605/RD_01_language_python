import pandas as pd

# from openpyxl import load_workbook
# from openpyxl.styles import Font, PatternFill, Border, Side

# 1. 准备原始成绩数据（模拟老师批完的分数）
raw_data = {
    "姓名": ["张三", "李四", "王五", "赵六", "孙七"],
    "语文": [85, 58, 94, 72, 88],
    "数学": [92, 76, 88, 69, 95],
    "英语": [78, 65, 91, 55, 82]
}
raw_df = pd.DataFrame(raw_data)

# 2. 生成原始Excel文件（即“班级成绩.xlsx”）
raw_df.to_excel("班级成绩.xlsx", sheet_name="原始成绩", index=False, engine="openpyxl")
print("已生成'班级成绩.xlsx'原始文件")