import xlrd
import xlwt
from xlutils.copy import copy
import os

base_file = "班级成绩.xls"


# ===================== 第二步：读取数据+计算总分+排序，生成待美化文件 =====================
def process_score_data(base_file):
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
    print(f"✅ 数据处理完成（求和+排序），已排序文件生成：{to_be_beautiful_file}")

    # 返回排序后的数据（供后续美化使用）
    return to_be_beautiful_file, headers, score_data


# ===================== 第三步：美化格式，生成正式版文件 =====================
def beautify_score_file(to_be_beautiful_file, headers, score_data):
    """美化待美化文件（设置字体、颜色、对齐、边框），生成正式版"""

    # 1. 定义美化样式
    def create_style(font_bold=False, font_size=11, bg_color=None, align_center=True):
        """封装样式创建函数"""
        style = xlwt.XFStyle()

        # 字体设置
        font = xlwt.Font()
        font.name = "微软雅黑"
        font.bold = font_bold
        font.size = font_size * 20  # xlwt中字体大小单位是1/20磅
        style.font = font

        # 对齐设置
        alignment = xlwt.Alignment()
        if align_center:
            alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平居中
            alignment.vert = xlwt.Alignment.VERT_CENTER  # 垂直居中
        style.alignment = alignment

        # 背景色设置
        if bg_color:
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN
            pattern.pattern_fore_colour = bg_color  # 颜色值（xlwt内置常量）
            style.pattern = pattern

        # 边框设置
        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        style.borders = borders

        return style

    # 预定义样式
    header_style = create_style(font_bold=True, font_size=12, bg_color=36)  # 表头样式（灰色背景+加粗）
    normal_style = create_style()  # 普通单元格样式
    high_score_style = create_style(bg_color=10)  # 总分前3名背景色（浅绿色）
    low_score_style = create_style(bg_color=2)  # 单科低于80分背景色（浅红色）

    # 2. 打开待美化文件并复制为可写工作簿
    old_wb = xlrd.open_workbook(to_be_beautiful_file, formatting_info=True)
    new_wb = copy(old_wb)
    new_ws = new_wb.get_sheet(0)

    # 3. 设置列宽（优化显示）
    col_widths = [200, 150, 150, 150, 150]  # 列宽（单位：1/20字符）
    for col, width in enumerate(col_widths):
        new_ws.col(col).width = width * 20

    # 4. 美化表头
    for col, header in enumerate(headers):
        new_ws.write(0, col, header, header_style)

    # 5. 美化数据行（区分高分、低分）
    for row, student in enumerate(score_data, start=1):
        name, chinese, math, english, total = student

        # 写入姓名（普通样式）
        new_ws.write(row, 0, name, normal_style)

        # 写入单科成绩（低于80分标红）
        subjects = [chinese, math, english]
        for col, score in enumerate(subjects, start=1):
            if score < 80:
                new_ws.write(row, col, score, low_score_style)
            else:
                new_ws.write(row, col, score, normal_style)

        # 写入总分（前3名标绿）
        if row <= 3:
            new_ws.write(row, 4, total, high_score_style)
        else:
            new_ws.write(row, 4, total, normal_style)

    # 6. 保存正式版文件
    final_file = "班级成绩_正式版.xls"
    new_wb.save(final_file)
    print(f"✅ 格式美化完成，正式版文件生成：{final_file}")

    # 输出统计信息
    total_avg = sum([s[4] for s in score_data]) / len(score_data)
    max_total = max([s[4] for s in score_data])
    min_total = min([s[4] for s in score_data])
    print(f"\n📊 成绩统计：")
    print(f"平均分：{total_avg:.1f} | 最高分：{max_total} | 最低分：{min_total}")


# ===================== 主执行流程 =====================
if __name__ == "__main__":

    # 2. 处理数据（求和+排序），生成待美化文件
    to_be_beautiful_file, headers, score_data = process_score_data(base_file)

    # 3. 美化格式，生成正式版
    beautify_score_file(to_be_beautiful_file, headers, score_data)

    # 验证文件是否全部生成
    all_files = ["班级成绩.xls", "班级成绩_待美化.xls", "班级成绩_正式版.xls"]
    existing_files = [f for f in all_files if os.path.exists(f)]
    print(f"\n📁 最终生成文件列表：{existing_files}")
    # print("🎉 所有流程执行完成！")