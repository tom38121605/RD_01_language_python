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
    "510880": ["待定", "权益登记日:2026-01-20"],
    "510720": ["待定", "权益登记日:2025-02-13"],
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
    "000001": ["2025年报 2026-03-21", "预案公布日:2025-03-26"],
    "605368": ["2025年年报 2026/4/22", "预案公布日:2025-03-26"],
    "600985": ["2025年年报 2026/3/28", "预案公布日:2025-03-28"],
    "601916": ["2025年年报 2026/3/31", "预案公布日:2025-03-29"],
    "601169": ["2025年年报 2026-04-23", "预案公布日:2025-03-29"],
    "002807": ["2025年报 2026-03-31", "预案公布日:2025-03-29"],
    "600188": ["2025年年报 2026/3/28", "预案公布日:2025-03-29"],
    "600016": ["2025年年报 2026-03-31", "预案公布日:2025-04-15"],
    "600681": ["2025年年报 2026-04-23", "预案公布日:2025-04-23"],
    "600256": ["2025年年报 2026-04-24", "预案公布日:2025-04-25"],
    "603801": ["2025年年报 2026-04-30", "预案公布日:2025-04-29"],
    "002267": ["2025年报 2026-04-28", "预案公布日:2025-04-29"],
    "600219": ["2025年年报 2026-03-27", "预案公布日:2025-05-05"],
    "600755": ["2025年报 2026-04-23", "--"],
    "601006": ["2025年报 2026-04-30", "--"],
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
    "603132": "涨停回调", "603759": "配债股",
    # 补充业绩反转/涨停回调股票代码（根据截图）
    "000698": "业绩反转", "600339": "业绩反转", "600858": "涨停回调", "002076": "业绩反转",
    "160719": "套利基", "600777": "业绩反转", "501001": "套利基", "600738": "热点发展",
    "161031": "套利基", "165525": "套利基", "160416": "套利基", "600755": "分红股",
    "300506": "业绩反转", "601006": "分红股", "164824": "海外基", "002689": "业绩反转",
    "128124": "可转债", "002762": "业绩反转", "501225": "套利基", "127025": "可转债",
    "600477": "涨停回调", "300343": "业绩反转", "002424": "业绩反转", "002055": "业绩反转",
    "600636": "业绩反转", "002788": "涨停回调", "002877": "涨停回调", "002632": "涨停回调",
    "000595": "业绩反转", "002693": "业绩反转", "300211": "业绩反转", "161126": "海外基",
    "162719": "套利基", "162411": "套利基", "001202": "配债股", "600853": "配债股",
    "000903": "业绩反转", "300527": "业绩反转", "603595": "业绩反转", "300052": "业绩反转",
    "002713": "业绩反转", "002305": "业绩反转",
}

# ---------------------- 5. 小盘猛牛年报日期字典 ----------------------
small_cap_annual_report_dict = {
    "300891": ["2025年报2026-04-21", ""],  # 惠云钛业
    "605162": ["2025年报2026-04-25", ""],  # 新中港
    "300000": ["待定", "2024年报 2025-04-10"],  # 示例：待定日期
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
    "300506": ["2025年报 2026-04-10", ""],  # *ST名家
    "002689": ["2025年报 2026-04-29", ""],  # ST远智
    "002762": ["2025年报 2026-04-16", "--"],
    "002424": ["2025年报 2026-04-24", "--"],
    "300343": ["2025年报 2026-04-15", "--"],
    "002076": ["2025年报 2026-04-29", "--"],
    "000903": ["2025年报 2026-04-28", "--"],
    "000595": ["2025年报 2026-04-18", "--"],
    "300527": ["2025年报 2026-04-29", "--"],
    "600636": ["2025年报 2026-04-25", "--"],
    "002713": ["2025年报 2026-04-27", "--"],
    "603595": ["2025年报 2026-04-18", "--"],
    "300211": ["2025年报 2026-04-24", "--"],
    "002693": ["2025年报 2026-04-29", "--"],
    "002305": ["2025年报 2026-04-27", "--"],
    "000000": ["待定", "--"],  # 测试：纯待定
}

# ---------------------- 新增：8. 业绩反转处罚摘帽申请日期字典 ----------------------
performance_reversal_delisting_application_dict = {
    "000698": "2025年报 2026-11-28",  # ST沈化（指定日期）
    # 其他股票可按需补充，格式："证券代码": "摘帽申请日期"，无数据留空或不添加
}

# ---------------------- 9. 涨停回调年报日期字典 ----------------------
limit_up_callback_annual_report_dict = {
    "002154": ["2025年报 2026-04-25", ""],  # 报喜鸟
    "600477": ["2025年报 2026-04-17", ""],  # 杭萧钢构
    "600858": ["待定", "2024年报 2025-04-20"],  # 银座股份
    "000001": ["待定", ""],  # 测试：纯待定
}


# ---------------------- 10. 日期解析工具函数 ----------------------
def extract_date_from_str(date_str):
    """
    从字符串提取日期，兼容多种格式
    - 待定/无日期 → 返回2099-12-31（极大值，升序排最后）
    - 有效日期 → 返回datetime对象（用于排序）
    """
    if not date_str or date_str == "待定" or date_str == "--":
        return datetime(2099, 12, 31)  # 待定用极大值，升序时排在最后
    # 匹配 YYYY-MM-DD 格式（如：2026-04-25）
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if date_match:
        year, month, day = date_match.groups()
        return datetime(int(year), int(month), int(day))
    # 匹配 YYYY/MM/DD 格式（如：2026/4/22）
    date_match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        year, month, day = date_match.groups()
        return datetime(int(year), int(month), int(day))
    return datetime(2099, 12, 31)  # 无有效日期 → 极大值


# ---------------------- 11. 各策略排序函数 ----------------------
def get_fund_dividend_sort_key(item):
    """分红基排序key：先下期日期升序，待定则按去年日期升序"""
    code = item[0]
    next_date_str, last_date_str = dividend_fund_date_dict.get(code, ["待定", ""])
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


def get_stock_dividend_sort_key(item):
    """分红股排序key"""
    code = item[0]
    next_date_str = dividend_date_dict.get(code, ["", ""])[0]
    last_date_str = dividend_date_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


def get_small_cap_sort_key(item):
    """小盘猛牛排序key"""
    code = item[0]
    next_date_str = small_cap_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = small_cap_annual_report_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


def get_hot_development_sort_key(item):
    """热点发展排序key"""
    code = item[0]
    next_date_str = hot_development_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = hot_development_annual_report_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (-next_date.timestamp(), -last_date.timestamp())


def get_performance_reversal_sort_key(item):
    """业绩反转排序key"""
    code = item[0]
    next_date_str = performance_reversal_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = performance_reversal_annual_report_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


def get_limit_up_callback_sort_key(item):
    """涨停回调排序key：先下期日期升序，待定则按去年日期升序"""
    code = item[0]
    next_date_str = limit_up_callback_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = limit_up_callback_annual_report_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


# ---------------------- 12. 新增：合并股票策略排序函数 ----------------------
def get_combined_stock_sort_key(item):
    """
    合并股票sheet排序规则：
    1. 先按策略优先级：分红股 > 业绩反转 > 小盘猛牛 > 热点发展 > 涨停回调 > 配债股
    2. 同策略内按各自的日期规则排序
    """
    code, info, strategy = item[0], item[1], item[2]
    # 策略优先级权重（数字越小优先级越高）
    strategy_priority = {
        "分红股": 1,
        "业绩反转": 2,
        "小盘猛牛": 3,
        "热点发展": 4,
        "涨停回调": 5,
        "配债股": 6
    }
    priority = strategy_priority.get(strategy, 99)
    # 同策略内按原有日期规则排序
    if strategy == "分红股":
        date_key = get_stock_dividend_sort_key(item)
    elif strategy == "业绩反转":
        date_key = get_performance_reversal_sort_key(item)
    elif strategy == "小盘猛牛":
        date_key = get_small_cap_sort_key(item)
    elif strategy == "热点发展":
        date_key = get_hot_development_sort_key(item)
    elif strategy == "涨停回调":
        date_key = get_limit_up_callback_sort_key(item)
    else:
        date_key = (datetime(2099, 12, 31), datetime(2099, 12, 31))
    return (priority, date_key)


# ---------------------- 13. 样式创建函数（新增摘帽日期列样式） ----------------------
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

    # 新增：摘帽申请日期列样式（右对齐，与日期列一致）
    styles["delisting_apply_right"] = xlwt.XFStyle()
    styles["delisting_apply_right"].font = font
    styles["delisting_apply_right"].alignment = align_date
    styles["yellow_delisting_apply_right"] = xlwt.XFStyle()
    styles["yellow_delisting_apply_right"].font = font
    styles["yellow_delisting_apply_right"].alignment = align_date
    styles["yellow_delisting_apply_right"].pattern = pattern

    return styles


# ---------------------- 14. Sheet写入函数（增强版：新增摘帽申请日期列） ----------------------
def write_sheet_data(sheet, data_list, styles, row_height=11 * 20, is_strategy_sheet=False,
                     summary_data=None, summary_percent=None, total_capital=500000, is_dividend_sheet=False,
                     is_fund_sheet=False, is_small_cap_sheet=False, is_hot_development_sheet=False,
                     is_performance_reversal_sheet=False, is_limit_up_callback_sheet=False,
                     is_combined_stock_sheet=False):  # 新增合并股票sheet标记
    # 列宽配置（新增摘帽申请日期列宽）
    col_widths = {
        0: 8, 1: 13, 2: 8, 3: 8, 4: 10, 5: 9, 6: 6, 7: 12,
        8: 10, 9: 12, 10: 18, 11: 22, 12: 22  # 新增第12列（摘帽申请日期）宽22
    }
    for col_idx, width in col_widths.items():
        sheet.col(col_idx).width = width * 256

    # 表头配置（业绩反转sheet新增摘帽申请日期列）
    if is_fund_sheet or is_dividend_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新分红日期", "去年对应分红日期"]
    elif is_performance_reversal_sheet:  # 业绩反转sheet表头（新增第12列）
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报日期", "去年对应年报日期", "处罚摘帽申请日期"]
    elif is_combined_stock_sheet:  # 合并股票sheet表头
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报/分红日期", "去年对应年报/分红日期"]
    elif is_small_cap_sheet or is_hot_development_sheet or is_limit_up_callback_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报日期", "去年对应年报日期"]
    else:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略"]

    # 写入表头
    sheet.row(0).height = row_height
    for col_idx, header in enumerate(headers):
        sheet.write(0, col_idx, header, styles["header"])

    # 策略sheet排序逻辑
    if is_strategy_sheet and data_list:
        # 合并股票sheet排序
        if is_combined_stock_sheet:
            sorted_strategy_data = sorted(data_list, key=get_combined_stock_sort_key)
        elif is_fund_sheet:
            sorted_strategy_data = sorted(data_list, key=get_fund_dividend_sort_key)
        elif is_dividend_sheet:
            sorted_strategy_data = sorted(data_list, key=get_stock_dividend_sort_key)
        elif is_small_cap_sheet:
            sorted_strategy_data = sorted(data_list, key=get_small_cap_sort_key)
        elif is_hot_development_sheet:
            sorted_strategy_data = sorted(data_list, key=get_hot_development_sort_key)
        elif is_performance_reversal_sheet:
            sorted_strategy_data = sorted(data_list, key=get_performance_reversal_sort_key)
        elif is_limit_up_callback_sheet:
            sorted_strategy_data = sorted(data_list, key=get_limit_up_callback_sort_key)
        else:
            sorted_strategy_data = sorted(data_list, key=lambda x: x[1]["金额"], reverse=True)

        # 重新计算排名和累积
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

            # 业绩反转sheet：写入摘帽申请日期（黄色行）
            if is_performance_reversal_sheet:
                # 年报日期列
                dates = performance_reversal_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])
                # 新增摘帽申请日期列
                delisting_date = performance_reversal_delisting_application_dict.get(code, "")
                sheet.write(row_idx, 12, delisting_date, styles["yellow_delisting_apply_right"])
            # 其他策略日期列（保留）
            elif is_limit_up_callback_sheet:
                dates = limit_up_callback_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])
            elif is_fund_sheet:
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
            elif is_combined_stock_sheet:
                if strategy == "分红股":
                    dates = dividend_date_dict.get(code, ["", ""])
                elif strategy == "业绩反转":
                    dates = performance_reversal_annual_report_dict.get(code, ["", ""])
                elif strategy == "小盘猛牛":
                    dates = small_cap_annual_report_dict.get(code, ["", ""])
                elif strategy == "热点发展":
                    dates = hot_development_annual_report_dict.get(code, ["", ""])
                elif strategy == "涨停回调":
                    dates = limit_up_callback_annual_report_dict.get(code, ["", ""])
                else:
                    dates = ["", ""]
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])

        # 普通行样式
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

            # 业绩反转sheet：写入摘帽申请日期（普通行）
            if is_performance_reversal_sheet:
                # 年报日期列
                dates = performance_reversal_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                sheet.write(row_idx, 11, dates[1], styles["date_right"])
                # 新增摘帽申请日期列（000698显示指定日期，其他为空）
                delisting_date = performance_reversal_delisting_application_dict.get(code, "")
                sheet.write(row_idx, 12, delisting_date, styles["delisting_apply_right"])
            # 其他策略日期列（保留）
            elif is_limit_up_callback_sheet:
                dates = limit_up_callback_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                sheet.write(row_idx, 11, dates[1], styles["date_right"])
            elif is_fund_sheet:
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
            elif is_combined_stock_sheet:
                if strategy == "分红股":
                    dates = dividend_date_dict.get(code, ["", ""])
                elif strategy == "业绩反转":
                    dates = performance_reversal_annual_report_dict.get(code, ["", ""])
                elif strategy == "小盘猛牛":
                    dates = small_cap_annual_report_dict.get(code, ["", ""])
                elif strategy == "热点发展":
                    dates = hot_development_annual_report_dict.get(code, ["", ""])
                elif strategy == "涨停回调":
                    dates = limit_up_callback_annual_report_dict.get(code, ["", ""])
                else:
                    dates = ["", ""]
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                sheet.write(row_idx, 11, dates[1], styles["date_right"])

        row_idx += 1

    # 汇总行（仅总仓位sheet）
    if not is_strategy_sheet and summary_data and summary_percent:
        row_idx += 1
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


# ---------------------- 15. 数据读取与处理 ----------------------
old_workbook = xlrd.open_workbook("1234.xls")
position_dict = {}

# 读取原始仓位数据（01-04 sheet）
for sheet_name in ["01", "02", "03", "04"]:
    sheet = old_workbook.sheet_by_name(sheet_name)
    for row_idx in range(1, sheet.nrows):
        code = sheet.cell_value(row_idx, 0)
        name = sheet.cell_value(row_idx, 1)
        count_val = sheet.cell_value(row_idx, 2)
        price_val = sheet.cell_value(row_idx, 3)

        # 跳过银华日利
        if "银华日利" in name:
            continue

        # 数据类型转换
        count = float(count_val) if count_val else 0.0
        price = float(price_val) if price_val else 0.0

        # 标准化证券代码（补零到6位）
        try:
            code_str = str(int(float(code)))
            code = code_str.zfill(6)
        except:
            code = str(code)

        # 合并同代码数量
        if code in position_dict:
            position_dict[code]["总数量"] += count
        else:
            position_dict[code] = {"名称": name, "总数量": count, "当前价": price}

# 计算金额和仓位百分比（总资金50万）
total_capital = 500000
for code, info in position_dict.items():
    info["金额"] = int(info["总数量"] * info["当前价"])
    pct = (info["金额"] / total_capital) * 100
    info["仓位百分比"] = f"{round(pct, 1)}%"

# 生成总数据列表（按金额降序）
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

# 按策略分组
strategy_groups = defaultdict(list)
for item in full_data:
    strategy_groups[item[2]].append(item)

# 计算策略汇总金额和百分比
strategy_total_amount = {k: sum([i[1]["金额"] for i in v]) for k, v in strategy_groups.items()}
strategy_total_percent = {k: round((v / total_capital) * 100, 1) for k, v in strategy_total_amount.items()}

# 策略显示顺序
strategy_order = [
    "分红股", "分红基", "reit", "业绩反转", "小盘猛牛",
    "热点发展", "配债股", "涨停回调", "可转债",
    "套利基", "超跌基", "海外基", "空策略"
]
order_dict = {strategy: idx for idx, strategy in enumerate(strategy_order)}
sorted_strategy_names = sorted(strategy_total_amount.keys(), key=lambda x: order_dict.get(x, len(strategy_order)))
summary_data = {n: strategy_total_amount[n] for n in sorted_strategy_names}
summary_percent = {n: strategy_total_percent[n] for n in sorted_strategy_names}

# ---------------------- 16. 新增：合并6个股票策略数据 ----------------------
# 定义需要合并的股票策略列表
stock_strategies = ["分红股", "业绩反转", "小盘猛牛", "热点发展", "涨停回调", "配债股"]
# 合并数据
combined_stock_data = []
for strategy in stock_strategies:
    if strategy in strategy_groups:
        combined_stock_data.extend(strategy_groups[strategy])

# ---------------------- 17. 生成最终Excel ----------------------
final_workbook = xlwt.Workbook(encoding="utf-8")
styles = create_styles()

# 总仓位sheet
main_sheet_name = f"总仓位{len(sorted_strategy_names)}"
main_sheet = final_workbook.add_sheet(main_sheet_name)
write_sheet_data(main_sheet, full_data, styles, is_strategy_sheet=False,
                 summary_data=summary_data, summary_percent=summary_percent, total_capital=total_capital)

# 新增：创建"总股票"sheet（合并6个策略）
stock_sheet = final_workbook.add_sheet("总股票")
write_sheet_data(stock_sheet, combined_stock_data, styles, is_strategy_sheet=True,
                 total_capital=total_capital, is_combined_stock_sheet=True)

# 各策略sheet（保留原有逻辑）
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
    is_limit_up_callback_sheet = (strategy_name == "涨停回调")

    # 写入策略sheet数据
    write_sheet_data(strategy_sheet, group_data, styles, is_strategy_sheet=True,
                     total_capital=total_capital, is_dividend_sheet=is_dividend_sheet,
                     is_fund_sheet=is_fund_sheet, is_small_cap_sheet=is_small_cap_sheet,
                     is_hot_development_sheet=is_hot_development_sheet,
                     is_performance_reversal_sheet=is_performance_reversal_sheet,
                     is_limit_up_callback_sheet=is_limit_up_callback_sheet)

# 保存文件
final_workbook.save("__00_总仓位.xls")

# 验证提示
print("✅ 表格生成完成！")
