import xlrd
import xlwt
from xlwt import easyxf
from collections import defaultdict

# ---------------------- 1. 定义股票策略字典 ----------------------
strategy_dict = {
    "605368": "分红股",
    "501018": "套利基金",
    "002496": "业绩反转",
    "601916": "分红股",
    "127033": "可转债",
    "601169": "分红股",
    "160723": "套利基金",
    "161129": "套利基金",
    "180102": "reit",
    "512290": "超跌基金",
    "600256": "分红股",
    "600016": "分红股",
    "600759": "业绩反转",
    "511880": "",
    "002385": "热点发展",
    "512010": "超跌基金",
    "603801": "分红股",
    "159329": "海外基金",
    "002570": "热点发展",
    "515710": "超跌基金",
    "515300": "分红基金",
    "300891": "小盘猛牛",
    "002630": "业绩反转",
    "600681": "分红股",
    "000516": "热点发展",
    "600985": "分红股",
    "111024": "可转债",
    "508056": "reit",
    "002807": "分红股",
    "000001": "分红股",
    "002122": "业绩反转",
    "510880": "分红基金",
    "605058": "配债策略",
    "510720": "分红基金",
    "600188": "分红股",
    "110081": "可转债",
    "600169": "业绩反转",
    "605162": "小盘猛牛",
    "002154": "涨停回调",
    "404003": "可转债",
    "600735": "业绩反转",
    "515450": "分红基金",
    "600219": "分红股",
    "300044": "业绩反转",
    "520870": "海外基金",
    "404002": "可转债",
    "161226": "套利基金",
    "501300": "套利基金",
    "161128": "套利基金",
    "127015": "可转债",
    "002267": "分红股"
}


# ========== 策略名称替换函数 ==========
def shorten_strategy_name(name):
    """将策略名称中的“基金”替换为“基”"""
    return name.replace("基金", "基")


# =====================================

# ---------------------- 2. 通用样式定义 ----------------------
def create_styles():
    styles = {}
    # 基础样式（字号9）
    base_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 9 * 20
    base_style.font = font
    styles["base"] = base_style

    # 表头样式：居中+字号9
    header_center = xlwt.XFStyle()
    header_center.font = font
    align_header = xlwt.Alignment()
    align_header.horz = xlwt.Alignment.HORZ_CENTER
    align_header.vert = xlwt.Alignment.VERT_CENTER
    header_center.alignment = align_header
    styles["header"] = header_center

    # 仓位百分比样式：靠右+字号9
    percent_right = xlwt.XFStyle()
    percent_right.font = font
    align_percent = xlwt.Alignment()
    align_percent.horz = xlwt.Alignment.HORZ_RIGHT
    percent_right.alignment = align_percent
    styles["percent"] = percent_right

    # 策略列样式：靠右+字号9
    strategy_right = xlwt.XFStyle()
    strategy_right.font = font
    align_strategy = xlwt.Alignment()
    align_strategy.horz = xlwt.Alignment.HORZ_RIGHT
    strategy_right.alignment = align_strategy
    styles["strategy"] = strategy_right

    # 第10行背景样式：淡黄色+字号9
    yellow_bg = xlwt.XFStyle()
    yellow_bg.font = font
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 34
    yellow_bg.pattern = pattern
    styles["yellow"] = yellow_bg

    # 第10行仓位百分比样式：淡黄色+靠右+字号9
    yellow_percent = xlwt.XFStyle()
    yellow_percent.font = font
    yellow_percent.alignment = align_percent
    yellow_percent.pattern = pattern
    styles["yellow_percent"] = yellow_percent

    # 第10行策略样式：淡黄色+靠右+字号9
    yellow_strategy = xlwt.XFStyle()
    yellow_strategy.font = font
    yellow_strategy.alignment = align_strategy
    yellow_strategy.pattern = pattern
    styles["yellow_strategy"] = yellow_strategy

    # 汇总行样式（居中+字号9）
    summary_style = xlwt.XFStyle()
    summary_style.font = font
    align_summary = xlwt.Alignment()
    align_summary.horz = xlwt.Alignment.HORZ_CENTER
    align_summary.vert = xlwt.Alignment.VERT_CENTER
    summary_style.alignment = align_summary
    styles["summary"] = summary_style

    # 总累积仓位%列样式（靠右+字号9）
    total_percent_right = xlwt.XFStyle()
    total_percent_right.font = font
    align_total_percent = xlwt.Alignment()
    align_total_percent.horz = xlwt.Alignment.HORZ_RIGHT
    total_percent_right.alignment = align_total_percent
    styles["total_percent"] = total_percent_right

    # 第10行总累积仓位%样式（淡黄色+靠右）
    yellow_total_percent = xlwt.XFStyle()
    yellow_total_percent.font = font
    yellow_total_percent.alignment = align_total_percent
    yellow_total_percent.pattern = pattern
    styles["yellow_total_percent"] = yellow_total_percent

    return styles


# ---------------------- 3. 通用表格写入函数 ----------------------
def write_sheet_data(sheet, data_list, styles, row_height=11 * 20, is_strategy_sheet=False, summary_data=None,
                     summary_percent=None, total_capital=500000):
    # 调整列宽配置：新增总累积仓位%列
    col_widths = {
        0: 8, 1: 13, 2: 8, 3: 8,
        4: 10, 5: 9, 6: 6, 7: 12,
        8: 10, 9: 12  # 8=总累积仓位%，9=策略（原8列后移）
    }

    # 扩展列宽配置（适配汇总行多列显示）
    max_col = len(summary_data) if (summary_data and not is_strategy_sheet) else 9
    for col_idx in range(10, max_col):
        sheet.col(col_idx).width = 10 * 256  # 汇总列统一宽度10

    for col_idx, width in col_widths.items():
        sheet.col(col_idx).width = width * 256

    # 调整表头：新增“总累积仓位%”列
    headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额", "总累积仓位%",
               "策略"]
    sheet.row(0).height = row_height
    for col_idx, header in enumerate(headers):
        sheet.write(0, col_idx, header, styles["header"])

    # 策略sheet重新计算累积金额和排名
    if is_strategy_sheet and data_list:
        sorted_strategy_data = sorted(data_list, key=lambda x: x[1]["金额"], reverse=True)
        strategy_cumulative = 0
        strategy_rank = 1
        processed_data = []
        # 拆包时匹配6个元素
        for item in sorted_strategy_data:
            code, info, strategy, _, _, _ = item
            strategy_cumulative += info["金额"]
            # 计算总累积仓位%
            total_cumulative_percent = round((strategy_cumulative / total_capital) * 100, 1)
            # 新增total_cumulative_percent，保持6个元素
            processed_data.append((code, info, shorten_strategy_name(strategy), strategy_rank, strategy_cumulative,
                                   total_cumulative_percent))
            strategy_rank += 1
        data_list = processed_data

    # 写入数据
    row_idx = 1
    # 遍历拆包时匹配6个元素
    for item in data_list:
        code, info, strategy, rank, cumulative, total_cumulative_percent = item
        sheet.row(row_idx).height = row_height

        if rank == 10:
            sheet.write(row_idx, 0, code, styles["yellow"])
            sheet.write(row_idx, 1, info["名称"], styles["yellow"])
            sheet.write(row_idx, 2, info["总数量"], styles["yellow"])
            sheet.write(row_idx, 3, info["当前价"], styles["yellow"])
            sheet.write(row_idx, 4, info["金额"], styles["yellow"])
            sheet.write(row_idx, 5, info["仓位百分比"], styles["yellow_percent"])
            sheet.write(row_idx, 6, rank, styles["yellow"])
            sheet.write(row_idx, 7, cumulative, styles["yellow"])
            # 写入第10行总累积仓位%
            sheet.write(row_idx, 8, f"{total_cumulative_percent}%", styles["yellow_total_percent"])
            sheet.write(row_idx, 9, strategy, styles["yellow_strategy"])  # 策略列后移到第9列
        else:
            sheet.write(row_idx, 0, code, styles["base"])
            sheet.write(row_idx, 1, info["名称"], styles["base"])
            sheet.write(row_idx, 2, info["总数量"], styles["base"])
            sheet.write(row_idx, 3, info["当前价"], styles["base"])
            sheet.write(row_idx, 4, info["金额"], styles["base"])
            sheet.write(row_idx, 5, info["仓位百分比"], styles["percent"])
            sheet.write(row_idx, 6, rank, styles["base"])
            sheet.write(row_idx, 7, cumulative, styles["base"])
            # 写入普通行总累积仓位%
            sheet.write(row_idx, 8, f"{total_cumulative_percent}%", styles["total_percent"])
            sheet.write(row_idx, 9, strategy, styles["strategy"])  # 策略列后移到第9列

        row_idx += 1

    # 三行汇总布局（名称→金额→仓位%）
    if not is_strategy_sheet and summary_data and summary_percent:
        # 空行分隔（空1行）
        row_idx += 1
        sheet.row(row_idx).height = row_height

        # 第一行：策略名称（横向排列）
        name_row = row_idx + 1
        sheet.row(name_row).height = row_height
        col_idx = 0
        for strategy_name in summary_data.keys():
            sheet.write(name_row, col_idx, strategy_name, styles["summary"])
            col_idx += 1

        # 第二行：对应总金额（名称正下方）
        amount_row = name_row + 1
        sheet.row(amount_row).height = row_height
        col_idx = 0
        for total_amount in summary_data.values():
            sheet.write(amount_row, col_idx, total_amount, styles["summary"])
            col_idx += 1

        # 第三行：对应累积仓位%（金额正下方）
        percent_row = amount_row + 1
        sheet.row(percent_row).height = row_height
        col_idx = 0
        for percent in summary_percent.values():
            sheet.write(percent_row, col_idx, f"{percent}%", styles["summary"])
            col_idx += 1


# ---------------------- 4. 读取原始数据并预处理 ----------------------
# 读取旧表格数据
old_workbook = xlrd.open_workbook("1234.xls")
position_dict = {}

for sheet_name in ["01", "02", "03", "04"]:
    sheet = old_workbook.sheet_by_name(sheet_name)
    for row_idx in range(1, sheet.nrows):
        code = sheet.cell_value(row_idx, 0)
        name = sheet.cell_value(row_idx, 1)
        count_val = sheet.cell_value(row_idx, 2)
        price_val = sheet.cell_value(row_idx, 3)

        # ========== 核心修改：过滤银华日利 ==========
        if "银华日利" in name:
            continue  # 完全忽略银华日利，不加入任何统计
        # ==========================================

        try:
            count = float(count_val)
        except ValueError:
            count = 0.0

        try:
            price = float(price_val)
        except ValueError:
            price = 0.0

        # 证券代码补0至6位
        try:
            code_str = str(int(float(code)))
        except ValueError:
            code_str = str(code)
        if code_str.isdigit():
            code = code_str.zfill(6)
        else:
            code = code_str

        if code in position_dict:
            position_dict[code]["总数量"] += count
        else:
            position_dict[code] = {
                "名称": name,
                "总数量": count,
                "当前价": price
            }

# 计算金额、仓位百分比
total_capital = 500000
for code, info in position_dict.items():
    info["金额"] = int(info["总数量"] * info["当前价"])
    percentage = (info["金额"] / total_capital) * 100
    info["仓位百分比"] = f"{round(percentage, 1)}%"

# 按金额降序排序
sorted_positions = sorted(
    position_dict.items(),
    key=lambda x: x[1]["金额"],
    reverse=True
)

# 预处理完整数据：新增总累积仓位%计算
full_data = []
cumulative_amount = 0
rank = 1
for code, info in sorted_positions:
    cumulative_amount += info["金额"]
    # 计算总累积仓位% = 累计金额 / 总本金 * 100（保留1位小数）
    total_cumulative_percent = round((cumulative_amount / total_capital) * 100, 1)
    raw_strategy = strategy_dict.get(code, "")
    strategy = "空策略" if not raw_strategy else raw_strategy
    # 数据项新增total_cumulative_percent（6个元素）
    full_data.append((code, info, shorten_strategy_name(strategy), rank, cumulative_amount, total_cumulative_percent))
    rank += 1

# 按策略分组（使用替换后的策略名称）
strategy_groups = defaultdict(list)
for item in full_data:
    strategy_name = item[2]
    strategy_groups[strategy_name].append(item)

# 计算每个策略的总规模和对应仓位%
strategy_total_amount = {}
strategy_total_percent = {}  # 存储策略仓位%
for strategy_name, group_data in strategy_groups.items():
    total = sum([item[1]["金额"] for item in group_data])
    strategy_total_amount[strategy_name] = total
    # 计算策略仓位% = 策略总金额 / 总本金 * 100（保留1位小数）
    strategy_total_percent[strategy_name] = round((total / total_capital) * 100, 1)

# 按策略总规模降序排序策略名称
sorted_strategy_names = sorted(
    strategy_total_amount.keys(),
    key=lambda x: strategy_total_amount[x],
    reverse=True
)

# 整理汇总数据（按排序后的名称）
summary_data = {name: strategy_total_amount[name] for name in sorted_strategy_names}
summary_percent = {name: strategy_total_percent[name] for name in sorted_strategy_names}

# 计算策略总数并拼接总仓位sheet名称
strategy_count = len(sorted_strategy_names)
main_sheet_name = f"总仓位{strategy_count}"

# ---------------------- 5. 生成最终Excel文件（多sheet） ----------------------
final_workbook = xlwt.Workbook(encoding="utf-8")
styles = create_styles()
row_height = 11 * 20

# 生成总仓位sheet（传入summary_percent用于汇总显示）
main_sheet = final_workbook.add_sheet(main_sheet_name)
write_sheet_data(main_sheet, full_data, styles, row_height, is_strategy_sheet=False,
                 summary_data=summary_data, summary_percent=summary_percent, total_capital=total_capital)

# 按策略总规模降序生成策略sheet
for strategy_name in sorted_strategy_names:
    group_data = strategy_groups[strategy_name]
    safe_sheet_name = strategy_name.replace("/", "").replace("\\", "").replace(":", "")[:31]
    strategy_sheet = final_workbook.add_sheet(safe_sheet_name)
    # 传入total_capital用于计算策略内的总累积仓位%
    write_sheet_data(strategy_sheet, group_data, styles, row_height, is_strategy_sheet=True,
                     total_capital=total_capital)

# 保存文件
final_workbook.save("__00_总仓位.xls")

# 输出日志
print(f"✅ 多sheet表格生成完成！")
print(f"   - 总仓位sheet名称：{main_sheet_name}（包含{strategy_count}个策略）")
print(f"   - 已过滤“银华日利”，不参与任何统计与汇总")
print(f"   - 新增列：总累积仓位%（累积总金额右侧）")
print(f"   - 汇总布局：策略名称→总金额→累积仓位%（三行横向对齐）")
print(f"   - 策略排序（总规模从高到低）：")
for idx, name in enumerate(sorted_strategy_names, 1):
    print(f"     {idx}. {name} - 总规模：{strategy_total_amount[name]}元（仓位占比：{strategy_total_percent[name]}%）")