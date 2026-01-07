from datetime import datetime
import xlrd
import xlwt
from collections import defaultdict
import re

# ---------------------- 1. 分红基日期字典 ----------------------
dividend_fund_date_dict = {
    "180102": ["待定", "权益登记日: 2025-01-24"],
    "515300": ["待定", "权益登记日:2025-06-16"],
    "159307": ["待定", "权益登记日:2025-03-17"],
    "510880": ["待定", "权益登记日:2025-01-20"],
    "510720": ["待定", "权益登记日:2025-01-13"],
    "508056": ["待定", "权益登记日:2025-04-01"],
    "515450": ["待定", "权益登记日:2025-07-14"],
    "513820": ["待定", "权益登记日:2025-01-21"],
}

# ---------------------- 2. 分红股基础信息 ----------------------
dividend_stock_base_info = {
    "000001": {"名称": "平安银行", "数量": 300, "当前价": 11.54},
    "605368": {"名称": "蓝天燃气", "数量": 11300, "当前价": 7.78},
    "600985": {"名称": "淮北矿业", "数量": 400, "当前价": 11.19},
    "601916": {"名称": "浙商银行", "数量": 5500, "当前价": 3.05},
    "601169": {"名称": "北京银行", "数量": 2900, "当前价": 5.49},
    "002807": {"名称": "江阴银行", "数量": 600, "当前价": 4.65},
    "600188": {"名称": "兖矿能源", "数量": 200, "当前价": 13.43},
    "600016": {"名称": "民生银行", "数量": 3000, "当前价": 3.86},
    "600681": {"名称": "百川能源", "数量": 1000, "当前价": 4.08},
    "600256": {"名称": "广汇能源", "数量": 2200, "当前价": 4.96},
    "603801": {"名称": "志邦家居", "数量": 1000, "当前价": 9.23},
    "002267": {"名称": "陕天然气", "数量": 100, "当前价": 7.53},
    "600219": {"名称": "南山铝业", "数量": 1000, "当前价": 3.50},
}

# ---------------------- 3. 分红股日期字典 ----------------------
dividend_date_dict = {
    "000001": ["待定", "预案公布日:2025-03-26"],
    "605368": ["2025年年报 2026/4/22", "预案公布日:2025-03-26"],
    "600985": ["2025年年报 2026/3/28", "预案公布日:2025-03-28"],
    "601916": ["2025年年报 2026/3/31", "预案公布日:2025-03-29"],
    "601169": ["2025年年报 2026-04-23", "预案公布日:2025-03-29"],
    "002807": ["待定", "预案公布日:2025-03-29"],
    "600188": ["2025年年报 2026/3/28", "预案公布日:2025-03-29"],
    "600016": ["2025年年报 2026-03-31", "预案公布日:2025-04-15"],
    "600681": ["2025年年报 2026-04-23", "预案公布日:2025-04-23"],
    "600256": ["2025年年报 2026-04-24", "预案公布日:2025-04-25"],
    "603801": ["2025年年报 2026-04-30", "预案公布日:2025-04-29"],
    "002267": ["待定", "预案公布日:2025-04-29"],
    "600219": ["2025年年报 2026-05-10", "预案公布日:2025-05-05"],
}

# ---------------------- 4. 策略字典 ----------------------
strategy_dict = {
    "000001": "分红股", "605368": "分红股", "600985": "分红股",
    "601916": "分红股", "601169": "分红股", "002807": "分红股",
    "600188": "分红股", "600016": "分红股", "600681": "分红股",
    "600256": "分红股", "603801": "分红股", "002267": "分红股", "600219": "分红股",
    "180102": "分红基", "515300": "分红基", "159307": "分红基",
    "510880": "分红基", "510720": "分红基", "508056": "分红基",
    "515450": "分红基", "513820": "分红基",
    "501018": "套利基", "002496": "业绩反转", "127033": "可转债", "160723": "套利基",
    "161129": "套利基", "512290": "超跌基", "600759": "业绩反转",
    "511880": "空策略", "002385": "热点发展", "512010": "超跌基", "159329": "海外基",
    "002570": "热点发展", "515710": "超跌基", "300891": "小盘猛牛",
    "002630": "业绩反转", "000516": "热点发展", "111024": "可转债",
    "002122": "业绩反转", "605058": "配债策略",
    "110081": "可转债", "600169": "业绩反转", "605162": "小盘猛牛", "002154": "涨停回调",
    "404003": "可转债", "600735": "业绩反转", "300044": "业绩反转",
    "520870": "海外基", "404002": "可转债", "161226": "套利基", "501300": "套利基",
    "161128": "套利基", "127015": "可转债", "160216": "套利基", "160324": "套利基",
    "161032": "超跌基", "164701": "套利基", "161116": "套利基",
    "161124": "套利基", "002124": "业绩反转",
    # 补充业绩反转股票代码（根据截图）
    "002630": "业绩反转", "002122": "业绩反转", "600169": "业绩反转", "600735": "业绩反转",
    "300044": "业绩反转", "002124": "业绩反转", "002496": "业绩反转", "002630": "业绩反转",
    "002122": "业绩反转", "600759": "业绩反转", "600169": "业绩反转", "002124": "业绩反转",
    "000698": "业绩反转", "600339": "业绩反转", "600858": "涨停回调", "002076": "业绩反转",
    "160719": "套利基", "600777": "业绩反转",
    "501001": "套利基", "600738": "热点发展",
    "161031": "套利基", "165525": "套利基",
}

# ---------------------- 5. 小盘猛牛年报日期字典 ----------------------
small_cap_annual_report_dict = {
    "300891": ["2025年报2026-04-21", ""],  # 小盘猛牛1
    "605162": ["2025年报2026-04-25", ""],  # 小盘猛牛2
    "300000": ["待定", "2024年报 2025-04-10"],  # 示例：待定日期的小盘猛牛股票
}

# ---------------------- 6. 热点发展年报日期字典 ----------------------
hot_development_annual_report_dict = {
    "002385": ["2025年报 2026-04-24", ""],  # 大北农
    "002570": ["2025年报 2026-04-28", ""],  # 贝因美
    "000516": ["待定", ""],  # 国际医学
}

# ---------------------- 7. 业绩反转年报日期字典 ----------------------
performance_reversal_annual_report_dict = {
    "002496": ["2025年报 2026-03-31", ""],  # *ST辉丰
    "002630": ["2025年报 2026-04-27", ""],  # ST华西
    "600735": ["2025年报 2026-04-30", ""],  # ST新华锦
    "002122": ["2025年报 2026-04-24", ""],  # ST汇洲
    "600759": ["2025年报 2026-04-23", ""],  # 洲际油气
    "600169": ["2025年报 2026-04-21", ""],  # ST太重
    "300044": ["2025年报 2026-03-31", ""],  # ST赛为
    "002124": ["2025年报 2026-04-29", ""],  # 天邦食品
    "000698": ["2025年报 2026-03-28", ""],  # ST沈化
    "600339": ["2025年报 2026-04-11", ""],  # 中油工程
    "600777": ["2025年报 2026-04-24", ""],  # *ST新潮

    "000000": ["待定", "2024年报 2025-05-10"],  # 示例：待定日期的股票
}


# ---------------------- 8. 日期解析工具函数（修复 timestamp 溢出问题） ----------------------
def extract_date_from_str(date_str):
    """
    从字符串中提取日期（处理"权益登记日:2025-01-13"等格式）
    修复 datetime.max.timestamp() 在某些系统上的溢出问题
    """
    if not date_str or date_str == "待定":
        return datetime(2099, 12, 31)  # 待定用一个极大值表示，升序时会排在最后
    # 提取日期（兼容"2025年报 2026-04-24"格式）
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if date_match:
        year, month, day = date_match.groups()
        return datetime(int(year), int(month), int(day))
    date_match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        year, month, day = date_match.groups()
        return datetime(int(year), int(month), int(day))
    return datetime(2099, 12, 31)  # 无有效日期时返回极大值


# ---------------------- 9. 各策略排序函数 ----------------------
def get_fund_dividend_sort_key(item):
    """分红基排序key：先下期日期升序，待定则按去年日期升序"""
    code = item[0]
    next_date_str, last_date_str = dividend_fund_date_dict.get(code, ["待定", ""])
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)

def get_stock_dividend_sort_key(item):
    """分红股排序key（原有逻辑）"""
    code = item[0]
    next_date_str = dividend_date_dict.get(code, ["", ""])[0]
    last_date_str = dividend_date_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


def get_small_cap_sort_key(item):
    """小盘猛牛排序key：先按「下期新年报日期」升序，待定则按「去年对应年报日期」升序"""
    code = item[0]
    next_date_str = small_cap_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = small_cap_annual_report_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    # 升序排序：直接返回日期（小日期在前），待定的会因极大值排在最后
    return (next_date, last_date)


def get_hot_development_sort_key(item):
    """热点发展排序key：先按「下期新年报日期」降序，待定则按「去年对应年报日期」降序"""
    code = item[0]
    next_date_str = hot_development_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = hot_development_annual_report_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (-next_date.timestamp(), -last_date.timestamp())


def get_performance_reversal_sort_key(item):
    """业绩反转排序key：先按「下期新年报日期」升序，待定则按「去年对应年报日期」升序"""
    code = item[0]
    # 获取下期和去年年报日期
    next_date_str = performance_reversal_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = performance_reversal_annual_report_dict.get(code, ["", ""])[1]

    # 解析日期（待定返回极大值）
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)

    # 升序排序：直接返回日期（小日期在前），待定的会因极大值排在最后
    return (next_date, last_date)


# ---------------------- 10. 样式创建函数 ----------------------
def create_styles():
    styles = {}
    base_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 9 * 20
    base_style.font = font
    styles["base"] = base_style

    header_center = xlwt.XFStyle()
    header_center.font = font
    align_header = xlwt.Alignment()
    align_header.horz = xlwt.Alignment.HORZ_CENTER
    align_header.vert = xlwt.Alignment.VERT_CENTER
    header_center.alignment = align_header
    styles["header"] = header_center

    percent_right = xlwt.XFStyle()
    percent_right.font = font
    align_percent = xlwt.Alignment()
    align_percent.horz = xlwt.Alignment.HORZ_RIGHT
    percent_right.alignment = align_percent
    styles["percent"] = percent_right

    strategy_right = xlwt.XFStyle()
    strategy_right.font = font
    align_strategy = xlwt.Alignment()
    align_strategy.horz = xlwt.Alignment.HORZ_RIGHT
    strategy_right.alignment = align_strategy
    styles["strategy"] = strategy_right

    yellow_bg = xlwt.XFStyle()
    yellow_bg.font = font
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 34
    yellow_bg.pattern = pattern
    styles["yellow"] = yellow_bg

    styles["yellow_percent"] = xlwt.XFStyle()
    styles["yellow_percent"].font = font
    styles["yellow_percent"].alignment = align_percent
    styles["yellow_percent"].pattern = pattern

    styles["yellow_strategy"] = xlwt.XFStyle()
    styles["yellow_strategy"].font = font
    styles["yellow_strategy"].alignment = align_strategy
    styles["yellow_strategy"].pattern = pattern

    summary_style = xlwt.XFStyle()
    summary_style.font = font
    align_summary = xlwt.Alignment()
    align_summary.horz = xlwt.Alignment.HORZ_CENTER
    summary_style.alignment = align_summary
    styles["summary"] = summary_style

    total_percent_right = xlwt.XFStyle()
    total_percent_right.font = font
    align_total = xlwt.Alignment()
    align_total.horz = xlwt.Alignment.HORZ_RIGHT
    total_percent_right.alignment = align_total
    styles["total_percent"] = total_percent_right

    styles["yellow_total_percent"] = xlwt.XFStyle()
    styles["yellow_total_percent"].font = font
    styles["yellow_total_percent"].alignment = align_total
    styles["yellow_total_percent"].pattern = pattern

    date_right = xlwt.XFStyle()
    date_right.font = font
    align_date = xlwt.Alignment()
    align_date.horz = xlwt.Alignment.HORZ_RIGHT
    date_right.alignment = align_date
    styles["date_right"] = date_right

    styles["yellow_date_right"] = xlwt.XFStyle()
    styles["yellow_date_right"].font = font
    styles["yellow_date_right"].alignment = align_date
    styles["yellow_date_right"].pattern = pattern

    return styles


# ---------------------- 11. Sheet写入函数 ----------------------
def write_sheet_data(sheet, data_list, styles, row_height=11 * 20, is_strategy_sheet=False,
                     summary_data=None, summary_percent=None, total_capital=500000, is_dividend_sheet=False,
                     is_fund_sheet=False, is_small_cap_sheet=False, is_hot_development_sheet=False,
                     is_performance_reversal_sheet=False):
    col_widths = {
        0: 8, 1: 13, 2: 8, 3: 8, 4: 10, 5: 9, 6: 6, 7: 12,
        8: 10, 9: 12, 10: 18, 11: 22
    }
    for col_idx, width in col_widths.items():
        sheet.col(col_idx).width = width * 256

    # 表头逻辑：业绩反转新增年报日期列
    if is_fund_sheet or is_dividend_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新分红日期", "去年对应分红日期"]
    elif is_small_cap_sheet or is_hot_development_sheet or is_performance_reversal_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报日期", "去年对应年报日期"]
    else:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略"]

    sheet.row(0).height = row_height
    for col_idx, header in enumerate(headers):
        sheet.write(0, col_idx, header, styles["header"])

    # 排序逻辑：各策略使用对应排序规则
    if is_strategy_sheet and data_list:
        if is_fund_sheet:
            sorted_strategy_data = sorted(data_list, key=get_fund_dividend_sort_key)
        elif is_dividend_sheet:
            sorted_strategy_data = sorted(data_list, key=get_stock_dividend_sort_key)
        elif is_small_cap_sheet:
            sorted_strategy_data = sorted(data_list, key=get_small_cap_sort_key)
        elif is_hot_development_sheet:
            sorted_strategy_data = sorted(data_list, key=get_hot_development_sort_key)
        elif is_performance_reversal_sheet:
            sorted_strategy_data = sorted(data_list, key=get_performance_reversal_sort_key)
        else:
            sorted_strategy_data = sorted(data_list, key=lambda x: x[1]["金额"], reverse=True)

        # 重新计算累积和排名（按新排序）
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

    # 数据行写入
    row_idx = 1
    for item in data_list:
        code, info, strategy, rank, cumulative, total_cumulative_percent = item
        sheet.row(row_idx).height = row_height

        # 黄色行（第10行）样式
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

            # 日期列写入（黄色行）
            if is_fund_sheet:
                dates = dividend_fund_date_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])
            elif is_dividend_sheet:
                dates = dividend_date_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])
            elif is_small_cap_sheet:
                dates = small_cap_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])
            elif is_hot_development_sheet:
                dates = hot_development_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])
            elif is_performance_reversal_sheet:
                dates = performance_reversal_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])
        else:
            # 普通行样式
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

            # 日期列写入（普通行）
            if is_fund_sheet:
                dates = dividend_fund_date_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                sheet.write(row_idx, 11, dates[1], styles["date_right"])
            elif is_dividend_sheet:
                dates = dividend_date_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                sheet.write(row_idx, 11, dates[1], styles["date_right"])
            elif is_small_cap_sheet:
                dates = small_cap_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                sheet.write(row_idx, 11, dates[1], styles["date_right"])
            elif is_hot_development_sheet:
                dates = hot_development_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                sheet.write(row_idx, 11, dates[1], styles["date_right"])
            elif is_performance_reversal_sheet:
                dates = performance_reversal_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                sheet.write(row_idx, 11, dates[1], styles["date_right"])

        row_idx += 1

    # 汇总行（仅总仓位sheet）
    if summary_data and summary_percent:
        name_row = row_idx + 1
        sheet.row(name_row).height = row_height
        col_idx = 0
        for name in summary_data.keys():
            sheet.write(name_row, col_idx, name, styles["summary"])
            col_idx += 1
        amount_row = name_row + 1
        sheet.row(amount_row).height = row_height
        col_idx = 0
        for amt in summary_data.values():
            sheet.write(amount_row, col_idx, amt, styles["summary"])
            col_idx += 1
        percent_row = amount_row + 1
        sheet.row(percent_row).height = row_height
        col_idx = 0
        for pct in summary_percent.values():
            sheet.write(percent_row, col_idx, f"{pct}%", styles["summary"])
            col_idx += 1


# ---------------------- 12. 数据读取与处理 ----------------------
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
        count = float(count_val) if count_val else 0.0
        price = float(price_val) if price_val else 0.0
        try:
            code_str = str(int(float(code)))
            code = code_str.zfill(6)
        except:
            code = str(code)
        if code in position_dict:
            position_dict[code]["总数量"] += count
        else:
            position_dict[code] = {"名称": name, "总数量": count, "当前价": price}

total_capital = 500000
for code, info in position_dict.items():
    info["金额"] = int(info["总数量"] * info["当前价"])
    pct = (info["金额"] / total_capital) * 100
    info["仓位百分比"] = f"{round(pct, 1)}%"

sorted_positions = sorted(position_dict.items(), key=lambda x: x[1]["金额"], reverse=True)
full_data = []
cumulative_amount = 0
rank = 1
for code, info in sorted_positions:
    cumulative_amount += info["金额"]
    total_cumulative_pct = round((cumulative_amount / total_capital) * 100, 1)
    strategy = strategy_dict.get(code, "空策略") or "空策略"
    full_data.append((code, info, strategy, rank, cumulative_amount, total_cumulative_pct))
    rank += 1

strategy_groups = defaultdict(list)
for item in full_data:
    strategy_groups[item[2]].append(item)

strategy_total_amount = {k: sum([i[1]["金额"] for i in v]) for k, v in strategy_groups.items()}
strategy_total_percent = {k: round((v / total_capital) * 100, 1) for k, v in strategy_total_amount.items()}

strategy_order = [
    "分红股", "分红基", "reit", "业绩反转", "小盘猛牛",
    "热点发展", "配债策略", "涨停回调", "可转债",
    "套利基", "超跌基", "海外基", "空策略"
]
order_dict = {strategy: idx for idx, strategy in enumerate(strategy_order)}
sorted_strategy_names = sorted(strategy_total_amount.keys(), key=lambda x: order_dict.get(x, len(strategy_order)))
summary_data = {n: strategy_total_amount[n] for n in sorted_strategy_names}
summary_percent = {n: strategy_total_percent[n] for n in sorted_strategy_names}

# ---------------------- 13. 生成最终Excel ----------------------
final_workbook = xlwt.Workbook(encoding="utf-8")
styles = create_styles()

# 总仓位sheet
main_sheet_name = f"总仓位{len(sorted_strategy_names)}"
main_sheet = final_workbook.add_sheet(main_sheet_name)
write_sheet_data(main_sheet, full_data, styles, is_strategy_sheet=False,
                 summary_data=summary_data, summary_percent=summary_percent, total_capital=total_capital)

# 各策略sheet
for strategy_name in sorted_strategy_names:
    group_data = strategy_groups[strategy_name]
    safe_name = strategy_name.replace("/", "").replace("\\", "").replace(":", "")[:31]
    if not safe_name:
        safe_name = "空策略"
    strategy_sheet = final_workbook.add_sheet(safe_name)

    # 标记各策略类型
    is_fund_sheet = (strategy_name == "分红基")
    is_dividend_sheet = (strategy_name == "分红股")
    is_small_cap_sheet = (strategy_name == "小盘猛牛")
    is_hot_development_sheet = (strategy_name == "热点发展")
    is_performance_reversal_sheet = (strategy_name == "业绩反转")

    write_sheet_data(strategy_sheet, group_data, styles, is_strategy_sheet=True,
                     total_capital=total_capital, is_dividend_sheet=is_dividend_sheet,
                     is_fund_sheet=is_fund_sheet, is_small_cap_sheet=is_small_cap_sheet,
                     is_hot_development_sheet=is_hot_development_sheet,
                     is_performance_reversal_sheet=is_performance_reversal_sheet)

# 保存文件
final_workbook.save("__00_总仓位.xls")
print("✅ 表格生成完成！")
# print(f"   - 小盘猛牛sheet排序规则：先按「下期新年报日期」升序，待定值按「去年对应年报日期」升序")
# print(f"   - 热点发展sheet排序规则：先按「下期新年报日期」降序，待定值按「去年对应年报日期」降序")
# print(f"   - 业绩反转sheet排序规则：先按「下期新年报日期」升序，待定值按「去年对应年报日期」升序")
# print(f"   - 业绩反转/热点发展sheet已新增「下期新年报日期」「去年对应年报日期」列")