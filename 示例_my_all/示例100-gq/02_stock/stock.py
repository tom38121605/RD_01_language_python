from datetime import datetime
import xlrd
import xlwt
from xlwt import easyxf
from collections import defaultdict
import re

# ---------------------- 1. 修正分红股基础信息（统一民生银行代码600016） ----------------------
dividend_stock_base_info = {
    "000001": {"名称": "平安银行", "数量": 300, "当前价": 11.54},
    "605368": {"名称": "蓝天燃气", "数量": 11300, "当前价": 7.78},
    "600895": {"名称": "淮北矿业", "数量": 400, "当前价": 11.25},
    "601916": {"名称": "浙商银行", "数量": 5500, "当前价": 3.05},
    "601169": {"名称": "北京银行", "数量": 2900, "当前价": 5.49},
    "002807": {"名称": "江阴银行", "数量": 600, "当前价": 4.65},
    "600188": {"名称": "兖矿能源", "数量": 200, "当前价": 13.43},
    "600016": {"名称": "民生银行", "数量": 3000, "当前价": 3.86},  # 修正：统一为600016，数据匹配表格
    "600881": {"名称": "百川能源", "数量": 800, "当前价": 4.11},
    "600256": {"名称": "广汇能源", "数量": 2200, "当前价": 4.96},
    "603801": {"名称": "志邦家居", "数量": 1000, "当前价": 9.23},
    "002267": {"名称": "陕天然气", "数量": 100, "当前价": 7.53},
}

# ---------------------- 2. 修正分红日期字典（删除601988，保留600016） ----------------------
dividend_date_dict = {
    "000001": ["待定", "预案公布日:2025-03-20"],
    "605368": ["2025年年报 2026/4/22", "预案公布日:2025-03-26"],
    "600895": ["2025年年报 2026/3/28", "预案公布日:2025-03-28"],
    "601916": ["2025年年报 2026/3/31", "预案公布日:2025-03-29"],
    "601169": ["2025年年报 2026-04-23", "预案公布日:2025-03-29"],
    "002807": ["待定", "预案公布日:2025-03-29"],
    "600188": ["2025年年报 2026/3/28", "预案公布日:2025-03-29"],
    "600016": ["2025年年报 2026-03-31", "预案公布日:2025-04-15"],  # 民生银行唯一代码
    "600881": ["2025年年报 2026-04-23", "预案公布日:2025-04-23"],
    "600256": ["2025年年报 2026-04-24", "预案公布日:2025-04-25"],
    "603801": ["2025年年报 2026-04-30", "预案公布日:2025-04-29"],
    "002267": ["待定", "预案公布日:2025-04-29"],
}

# ---------------------- 3. 修正策略字典（删除601988，保留600016） ----------------------
strategy_dict = {
    "000001": "分红股", "605368": "分红股", "600895": "分红股", "601916": "分红股",
    "601169": "分红股", "002807": "分红股", "600188": "分红股", "600016": "分红股",  # 民生银行唯一配置
    "600881": "分红股", "600256": "分红股", "603801": "分红股", "002267": "分红股",
    "501018": "套利基金", "002496": "业绩反转", "127033": "可转债", "160723": "套利基金",
    "161129": "套利基金", "180102": "reit", "512290": "超跌基金", "600759": "业绩反转",
    "511880": "", "002385": "热点发展", "512010": "超跌基金", "159329": "海外基金",
    "002570": "热点发展", "515710": "超跌基金", "515300": "分红基金", "300891": "小盘猛牛",
    "002630": "业绩反转", "000516": "热点发展", "111024": "可转债", "508056": "reit",
    "002122": "业绩反转", "510880": "分红基金", "605058": "配债策略", "510720": "分红基金",
    "110081": "可转债", "600169": "业绩反转", "605162": "小盘猛牛", "002154": "涨停回调",
    "404003": "可转债", "600735": "业绩反转", "515450": "分红基金", "300044": "业绩反转",
    "520870": "海外基金", "404002": "可转债", "161226": "套利基金", "501300": "套利基金",
    "161128": "套利基金", "127015": "可转债", "160216": "套利基", "160324": "套利基",
    "161032": "超跌基", "164701": "套利基", "161116": "套利基",
}


# ---------------------- 4. 其余代码（排序/样式/写入/数据读取）完全不变 ----------------------
def parse_next_dividend_date(date_str):
    if not date_str or "待定" in date_str:
        return datetime.max
    date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_str)
    if date_match:
        year, month, day = date_match.groups()
        return datetime(int(year), int(month), int(day))
    return datetime.max


def parse_last_dividend_date(date_str):
    if not date_str or "待定" in date_str:
        return datetime.max
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if date_match:
        year, month, day = date_match.groups()
        return datetime(int(year), int(month), int(day))
    return datetime.max


def get_dividend_sort_key(item):
    code = item[0]
    next_date_str = dividend_date_dict.get(code, ["", ""])[0]
    last_date_str = dividend_date_dict.get(code, ["", ""])[1]
    next_date = parse_next_dividend_date(next_date_str)
    last_date = parse_last_dividend_date(last_date_str)
    return (next_date, last_date)


def create_styles():
    styles = {}
    # 基础样式
    base_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 9 * 20
    base_style.font = font
    styles["base"] = base_style

    # 表头居中
    header_center = xlwt.XFStyle()
    header_center.font = font
    align_header = xlwt.Alignment()
    align_header.horz = xlwt.Alignment.HORZ_CENTER
    align_header.vert = xlwt.Alignment.VERT_CENTER
    header_center.alignment = align_header
    styles["header"] = header_center

    # 百分比靠右
    percent_right = xlwt.XFStyle()
    percent_right.font = font
    align_percent = xlwt.Alignment()
    align_percent.horz = xlwt.Alignment.HORZ_RIGHT
    percent_right.alignment = align_percent
    styles["percent"] = percent_right

    # 策略列靠右
    strategy_right = xlwt.XFStyle()
    strategy_right.font = font
    align_strategy = xlwt.Alignment()
    align_strategy.horz = xlwt.Alignment.HORZ_RIGHT
    strategy_right.alignment = align_strategy
    styles["strategy"] = strategy_right

    # 第10行黄色背景
    yellow_bg = xlwt.XFStyle()
    yellow_bg.font = font
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 34
    yellow_bg.pattern = pattern
    styles["yellow"] = yellow_bg

    yellow_percent = xlwt.XFStyle()
    yellow_percent.font = font
    yellow_percent.alignment = align_percent
    yellow_percent.pattern = pattern
    styles["yellow_percent"] = yellow_percent

    yellow_strategy = xlwt.XFStyle()
    yellow_strategy.font = font
    yellow_strategy.alignment = align_strategy
    yellow_strategy.pattern = pattern
    styles["yellow_strategy"] = yellow_strategy

    # 汇总行居中
    summary_style = xlwt.XFStyle()
    summary_style.font = font
    align_summary = xlwt.Alignment()
    align_summary.horz = xlwt.Alignment.HORZ_CENTER
    summary_style.alignment = align_summary
    styles["summary"] = summary_style

    # 总累积仓位%靠右
    total_percent_right = xlwt.XFStyle()
    total_percent_right.font = font
    align_total = xlwt.Alignment()
    align_total.horz = xlwt.Alignment.HORZ_RIGHT
    total_percent_right.alignment = align_total
    styles["total_percent"] = total_percent_right

    yellow_total_percent = xlwt.XFStyle()
    yellow_total_percent.font = font
    yellow_total_percent.alignment = align_total
    yellow_total_percent.pattern = pattern
    styles["yellow_total_percent"] = yellow_total_percent

    # 日期列靠右
    date_right = xlwt.XFStyle()
    date_right.font = font
    align_date = xlwt.Alignment()
    align_date.horz = xlwt.Alignment.HORZ_RIGHT
    date_right.alignment = align_date
    styles["date_right"] = date_right

    yellow_date_right = xlwt.XFStyle()
    yellow_date_right.font = font
    yellow_date_right.alignment = align_date
    yellow_date_right.pattern = pattern
    styles["yellow_date_right"] = yellow_date_right

    return styles


def write_sheet_data(sheet, data_list, styles, row_height=11 * 20, is_strategy_sheet=False,
                     summary_data=None, summary_percent=None, total_capital=500000, is_dividend_sheet=False):
    # 列宽配置
    col_widths = {
        0: 8, 1: 13, 2: 8, 3: 8, 4: 10, 5: 9, 6: 6, 7: 12,
        8: 10, 9: 12, 10: 18, 11: 22
    }
    for col_idx, width in col_widths.items():
        sheet.col(col_idx).width = width * 256

    # 表头
    if is_dividend_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新分红日期", "去年对应分红日期"]
    else:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略"]
    sheet.row(0).height = row_height
    for col_idx, header in enumerate(headers):
        sheet.write(0, col_idx, header, styles["header"])

    # 策略sheet数据处理
    if is_strategy_sheet and data_list:
        if is_dividend_sheet:
            sorted_strategy_data = sorted(data_list, key=get_dividend_sort_key)
        else:
            sorted_strategy_data = sorted(data_list, key=lambda x: x[1]["金额"], reverse=True)

        # 重新计算排名、累积金额
        strategy_cumulative = 0
        strategy_rank = 1
        processed_data = []
        for item in sorted_strategy_data:
            code, info, strategy, _, _, _ = item
            strategy_cumulative += info["金额"]
            total_cumulative_percent = round((strategy_cumulative / total_capital) * 100, 1)
            processed_data.append((code, info, strategy, strategy_rank, strategy_cumulative, total_cumulative_percent))
            strategy_rank += 1
        data_list = processed_data

    # 写入数据行
    row_idx = 1
    for item in data_list:
        code, info, strategy, rank, cumulative, total_cumulative_percent = item
        sheet.row(row_idx).height = row_height

        # 区分第10行（黄色背景）
        if rank == 10:
            sheet.write(row_idx, 0, code, styles["yellow"])
            sheet.write(row_idx, 1, info["名称"], styles["yellow"])
            sheet.write(row_idx, 2, info["总数量"], styles["yellow"])
            sheet.write(row_idx, 3, info["当前价"], styles["yellow"])
            sheet.write(row_idx, 4, info["金额"], styles["yellow"])
            sheet.write(row_idx, 5, info["仓位百分比"], styles["yellow_percent"])
            sheet.write(row_idx, 6, rank, styles["yellow"])
            sheet.write(row_idx, 7, cumulative, styles["yellow"])
            sheet.write(row_idx, 8, f"{total_cumulative_percent}%", styles["yellow_total_percent"])
            sheet.write(row_idx, 9, strategy, styles["yellow_strategy"])

            # 分红日期列（第10行）
            if is_dividend_sheet:
                dates = dividend_date_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])
        else:
            sheet.write(row_idx, 0, code, styles["base"])
            sheet.write(row_idx, 1, info["名称"], styles["base"])
            sheet.write(row_idx, 2, info["总数量"], styles["base"])
            sheet.write(row_idx, 3, info["当前价"], styles["base"])
            sheet.write(row_idx, 4, info["金额"], styles["base"])
            sheet.write(row_idx, 5, info["仓位百分比"], styles["percent"])
            sheet.write(row_idx, 6, rank, styles["base"])
            sheet.write(row_idx, 7, cumulative, styles["base"])
            sheet.write(row_idx, 8, f"{total_cumulative_percent}%", styles["total_percent"])
            sheet.write(row_idx, 9, strategy, styles["strategy"])

            # 分红日期列（普通行）
            if is_dividend_sheet:
                dates = dividend_date_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                sheet.write(row_idx, 11, dates[1], styles["date_right"])
        row_idx += 1

    # 汇总行（非策略sheet）
    if not is_strategy_sheet and summary_data and summary_percent:
        row_idx += 1
        # 策略名称行
        name_row = row_idx + 1
        sheet.row(name_row).height = row_height
        col_idx = 0
        for name in summary_data.keys():
            sheet.write(name_row, col_idx, name, styles["summary"])
            col_idx += 1
        # 金额行
        amount_row = name_row + 1
        sheet.row(amount_row).height = row_height
        col_idx = 0
        for amt in summary_data.values():
            sheet.write(amount_row, col_idx, amt, styles["summary"])
            col_idx += 1
        # 仓位%行
        percent_row = amount_row + 1
        sheet.row(percent_row).height = row_height
        col_idx = 0
        for pct in summary_percent.values():
            sheet.write(percent_row, col_idx, f"{pct}%", styles["summary"])
            col_idx += 1


# ---------------------- 数据读取+填充分红股基础信息 ----------------------
# 读取原始文件
old_workbook = xlrd.open_workbook("1234.xls")
position_dict = {}

for sheet_name in ["01", "02", "03", "04"]:
    sheet = old_workbook.sheet_by_name(sheet_name)
    for row_idx in range(1, sheet.nrows):
        code = sheet.cell_value(row_idx, 0)
        name = sheet.cell_value(row_idx, 1)
        count_val = sheet.cell_value(row_idx, 2)
        price_val = sheet.cell_value(row_idx, 3)

        if "银华日利" in name:
            continue

        # 数据类型转换
        count = float(count_val) if count_val else 0.0
        price = float(price_val) if price_val else 0.0

        # 代码补0至6位
        try:
            code_str = str(int(float(code)))
            code = code_str.zfill(6)
        except:
            code = str(code)

        # 累加数量
        if code in position_dict:
            position_dict[code]["总数量"] += count
        else:
            position_dict[code] = {"名称": name, "总数量": count, "当前价": price}

# ---------------------- 填充分红股基础信息 ----------------------
for code, strat in strategy_dict.items():
    if strat == "分红股":
        # 若原始文件无该标的，从基础信息字典填充
        if code not in position_dict:
            base_info = dividend_stock_base_info.get(code, {"名称": "", "数量": 0.0, "当前价": 0.0})
            position_dict[code] = {
                "名称": base_info["名称"],
                "总数量": base_info["数量"],
                "当前价": base_info["当前价"],
                "金额": 0,
                "仓位百分比": "0.0%"
            }
        # 排除600219
        elif code == "600219":
            del position_dict[code]

# 计算金额、仓位百分比
total_capital = 500000
for code, info in position_dict.items():
    info["金额"] = int(info["总数量"] * info["当前价"])
    pct = (info["金额"] / total_capital) * 100
    info["仓位百分比"] = f"{round(pct, 1)}%"

# 排序+预处理完整数据
sorted_positions = sorted(position_dict.items(), key=lambda x: x[1]["金额"], reverse=True)
full_data = []
cumulative_amount = 0
rank = 1
for code, info in sorted_positions:
    if code == "600219":
        continue
    cumulative_amount += info["金额"]
    total_cumulative_pct = round((cumulative_amount / total_capital) * 100, 1)
    strategy = strategy_dict.get(code, "空策略")
    full_data.append((code, info, strategy, rank, cumulative_amount, total_cumulative_pct))
    rank += 1

# 按策略分组
strategy_groups = defaultdict(list)
for item in full_data:
    strategy_groups[item[2]].append(item)

# 计算策略汇总
strategy_total_amount = {k: sum([i[1]["金额"] for i in v]) for k, v in strategy_groups.items()}
strategy_total_percent = {k: round((v / total_capital) * 100, 1) for k, v in strategy_total_amount.items()}
sorted_strategy_names = sorted(strategy_total_amount.keys(), key=lambda x: strategy_total_amount[x], reverse=True)
summary_data = {n: strategy_total_amount[n] for n in sorted_strategy_names}
summary_percent = {n: strategy_total_percent[n] for n in sorted_strategy_names}

# 生成Excel
final_workbook = xlwt.Workbook(encoding="utf-8")
styles = create_styles()
main_sheet_name = f"总仓位{len(sorted_strategy_names)}"
main_sheet = final_workbook.add_sheet(main_sheet_name)
write_sheet_data(main_sheet, full_data, styles, is_strategy_sheet=False,
                 summary_data=summary_data, summary_percent=summary_percent, total_capital=total_capital)

# 生成各策略sheet
for strategy_name in sorted_strategy_names:
    group_data = strategy_groups[strategy_name]
    safe_name = strategy_name.replace("/", "").replace("\\", "").replace(":", "")[:31]
    strategy_sheet = final_workbook.add_sheet(safe_name)
    is_dividend = (strategy_name == "分红股")
    write_sheet_data(strategy_sheet, group_data, styles, is_strategy_sheet=True,
                     total_capital=total_capital, is_dividend_sheet=is_dividend)

# 保存文件
final_workbook.save("__00_总仓位.xls")

# 输出日志
print("✅ 表格生成完成！")
print(f"   - 修正：民生银行仅保留代码600016，无重复行")
print(f"   - 分红股标的信息完整（名称/数量/当前价匹配表格）")
print(f"   - 分红股sheet排序规则：下期日期升序（待定后排），待定按去年日期升序")
print(f"   - 生成文件：__00_总仓位.xls")