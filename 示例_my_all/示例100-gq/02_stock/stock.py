from datetime import datetime, timedelta
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
    "002630": "业绩反转", "000516": "热点发展", "111024": "可转债", "000537": "热点发展",
    "002122": "业绩反转", "605058": "配债策略",
    "110081": "可转债", "600169": "业绩反转", "605162": "小盘猛牛", "002154": "涨停回调",
    "404003": "可转债", "600735": "业绩反转", "300044": "业绩反转",
    "520870": "海外基", "404002": "", "161226": "套利基", "501300": "套利基",
    "161128": "套利基", "127015": "可转债", "160216": "套利基", "160324": "套利基",
    "161032": "超跌基", "164701": "套利基", "161116": "套利基", "601669": "涨停回调",
    "161124": "套利基", "113701": "可转债", "600662": "涨停回调", "000639": "热点发展",
    "603132": "涨停回调", "603759": "配债股", "600814": "涨停回调", "603500": "配债股",
    "600516": "涨停回调",
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
    "002713": "业绩反转", "002305": "业绩反转", "300366": "业绩反转", "300460": "业绩反转",
    "002124": "业绩反转", "600624": "业绩反转", "000488": "业绩反转", "000929": "业绩反转", "300311": "业绩反转",
    "000821": "业绩反转", "300020": "业绩反转", "600537": "业绩反转",
    "603789": "业绩反转", "300173": "业绩反转", "600421": "业绩反转",
    "600358": "业绩反转", "600892": "业绩反转", "003032": "业绩反转", "002512": "业绩反转",
}

# ---------------------- 新增：多策略归属字典 ----------------------
multi_strategy_codes = {
    "600681": ["分红股", "涨停回调"],
    "600755": ["分红股", "涨停回调"],
    "605368": ["分红股", "涨停回调"],
    "001202": ["配债股", "涨停回调"],
    "002267": ["分红股", "涨停回调"],
}

# ---------------------- 5. 小盘猛牛年报日期字典 ----------------------
small_cap_annual_report_dict = {
    "300891": ["2025年报2026-04-21", ""],
    "605162": ["2025年报2026-04-25", ""],
    "300000": ["待定", "2024年报 2025-04-10"],
}

# ---------------------- 6. 热点发展年报日期字典 ----------------------
hot_development_annual_report_dict = {
    "002385": ["2025年报 2026-04-24", ""],
    "002570": ["2025年报 2026-04-28", ""],
    "000516": ["待定", ""],
}

# ---------------------- 7. 业绩反转年报日期字典 ----------------------
performance_reversal_annual_report_dict = {
    "002496": ["2025年报 2026-03-31", ""],
    "002630": ["2025年报 2026-04-27", ""],
    "600735": ["2025年报 2026-04-30", ""],
    "002122": ["2025年报 2026-04-24", ""],
    "600759": ["2025年报 2026-04-23", ""],
    "600169": ["2025年报 2026-04-21", ""],
    "300044": ["2025年报 2026-03-31", ""],
    "002124": ["2025年报 2026-04-29", ""],
    "000698": ["2025年报 2026-03-28", ""],
    "600339": ["2025年报 2026-04-11", ""],
    "600777": ["2025年报 2026-04-24", ""],
    "300506": ["2025年报 2026-04-10", ""],
    "002689": ["2025年报 2026-04-29", ""],
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
    "000000": ["待定", "--"],
    "000929": ["2025年报 2026-03-31", ""],
    "603789": ["2025年报 2026-04-25", ""],
    "300173": ["2025年报 2026-04-29", ""],
    "600421": ["2025年报 2026-04-30", ""],
    "300366": ["2025年报 2026-04-24", ""],
    "300460": ["2025年报 2026-04-27", ""],
}

# ---------------------- 8. 业绩反转申请摘帽日期字典 ----------------------
performance_reversal_delisting_application_dict = {
    "600358": "2025年报 2026-03-21",
    "000929": "2025年报 2026-03-31",
    "002496": "2025年报 2026-03-31",
    "002762": "2025年报 2026-04-16",
    "000595": "2025年报 2026-04-18",
    "300211": "2025年报 2026-04-24",
    "600777": "2025年报 2026-04-24",
    "603789": "2025年报 2026-04-25",
    "600636": "2025年报 2026-04-25",
    "002713": "2025年报 2026-04-27",
    "002305": "2025年报 2026-04-27",
    "003032": "2025年报 2026-04-28",
    "002693": "2025年报 2026-04-29",
    "002076": "2025年报 2026-04-29",
    "600892": "2025年报 2026-04-30",
    "600421": "2025年报 2026-04-30",
    "002124": "预重整日期 2026-05-09",
    "300311": "2026-07-18",
    "000903": "2026-08-08",
    "300527": "2026-09-16",
    "300366": "2026-10-24",
    "603595": "2026-11-13",
    "002122": "2026-11-13",
    "000698": "2026-11-29",
    "002689": "2026-12-20",
    "600624": "2026-12-26",
    "600169": "2026-12-29",
    "300460": "2027-01-12",
    "000821": "2027-01-16",
    "300173": "2027-02-06",
    "000488": "摘帽日期 待定",
    "600537": "预重整日期 待定",
    "002055": "摘帽日期 待定",
    "002630": "摘帽日期 待定",
    "002512": "摘帽日期 待定",
    "600735": "重整日期 待定",
}

# ---------------------- 新增：业绩反转 要点字典 ----------------------
performance_reversal_memo_dict = {
    "600358": "互联网营销 + 润田重组 + 已申请摘帽",
    "002496": "农药龙头 + 石化仓储 + 生物农业 + 摘帽预期",
    "002630": "重整进行",
    "600735": "待重整",
    "002122": "即将摘帽",
    "600759": "业绩改善",
    "600169": "摘帽排队",
    "300044": "风险较低",
    "002124": "预重整",
    "000698": "基本面反转",
    "600339": "油气回暖",
    "600777": "摘帽在即",
    "300506": "扭亏为盈",
    "002689": "资产优化",
    "002762": "业绩回升",
    "002424": "医药回暖",
    "300343": "业务转型",
    "002076": "低位反转",
    "000903": "国企改革",
    "000595": "设备更新",
    "300527": "高端制造",
    "600636": "环保利好",
    "002713": "地产链复苏",
    "603595": "消费复苏",
    "300211": "医药反转",
    "002693": "物流改善",
    "002305": "基建受益",
    "000929": "白酒复苏",
    "603789": "新材料",
    "300173": "设备升级",
    "600421": "重整落地",
    "300366": "智能装备",
    "300460": "半导体",
}

# ---------------------- 9. 涨停回调年报日期字典 ----------------------
limit_up_callback_annual_report_dict = {
    "002154": ["2025年报 2026-04-25", ""],
    "600477": ["2025年报 2026-04-17", ""],
    "600858": ["待定", "2024年报 2025-04-20"],
    "000001": ["待定", ""],
    "600681": ["2025年年报 2026-04-23", "预案公布日:2025-04-23"],
}


# ---------------------- 10. 日期解析工具函数 ----------------------
def extract_date_from_str(date_str):
    if not date_str or date_str == "待定" or date_str == "--":
        return datetime(2099, 12, 31)
    date_str = date_str.strip()
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if date_match:
        year, month, day = date_match.groups()
        return datetime(int(year), int(month), int(day))
    date_match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        year, month, day = date_match.groups()
        return datetime(int(year), int(month), int(day))
    return datetime(2099, 12, 31)


# ---------------------- 11. 摘帽申请日期解析函数 ----------------------
def extract_delisting_apply_date(code):
    delisting_date_str = performance_reversal_delisting_application_dict.get(code, "")
    delisting_date_str = delisting_date_str.strip()
    return extract_date_from_str(delisting_date_str)


# ---------------------- 判断摘帽日期是否小于2个月 ----------------------
def is_delisting_date_less_than_2months(code):
    delisting_date = extract_delisting_apply_date(code)
    if delisting_date == datetime(2099, 12, 31):
        return False
    current_date = datetime.now()
    delta = delisting_date - current_date
    return delta.days < 60 and delta.days >= 0


# ---------------------- 12. 各策略排序函数 ----------------------
def get_fund_dividend_sort_key(item):
    code = item[0]
    next_date_str, last_date_str = dividend_fund_date_dict.get(code, ["待定", ""])
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


def get_stock_dividend_sort_key(item):
    code = item[0]
    next_date_str = dividend_date_dict.get(code, ["", ""])[0]
    last_date_str = dividend_date_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


def get_small_cap_sort_key(item):
    code = item[0]
    next_date_str = small_cap_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = small_cap_annual_report_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


def get_hot_development_sort_key(item):
    code = item[0]
    next_date_str = hot_development_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = hot_development_annual_report_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (-next_date.timestamp(), -last_date.timestamp())


def get_performance_reversal_sort_key(item):
    code = item[0]
    delisting_apply_date = extract_delisting_apply_date(code)
    next_date_str = performance_reversal_annual_report_dict.get(code, ["待定", ""])[0]
    next_date = extract_date_from_str(next_date_str)
    return (delisting_apply_date, next_date)


def get_limit_up_callback_sort_key(item):
    code = item[0]
    next_date_str = limit_up_callback_annual_report_dict.get(code, ["待定", ""])[0]
    last_date_str = limit_up_callback_annual_report_dict.get(code, ["", ""])[1]
    next_date = extract_date_from_str(next_date_str)
    last_date = extract_date_from_str(last_date_str)
    return (next_date, last_date)


# ---------------------- 13. 合并股票策略排序函数 ----------------------
def get_combined_stock_sort_key(item):
    code, info, strategy = item[0], item[1], item[2]
    strategy_priority = {
        "分红股": 1,
        "业绩反转": 2,
        "小盘猛牛": 3,
        "热点发展": 4,
        "涨停回调": 5,
        "配债股": 6
    }
    priority = strategy_priority.get(strategy, 99)
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


# ---------------------- 14. 样式创建函数 ----------------------
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

    styles["delisting_apply_right"] = xlwt.XFStyle()
    styles["delisting_apply_right"].font = font
    styles["delisting_apply_right"].alignment = align_date

    styles["yellow_delisting_apply_right"] = xlwt.XFStyle()
    styles["yellow_delisting_apply_right"].font = font
    styles["yellow_delisting_apply_right"].alignment = align_date
    styles["yellow_delisting_apply_right"].pattern = pattern

    pink_delisting_apply = xlwt.XFStyle()
    pink_font = xlwt.Font()
    pink_font.height = 9 * 20
    pink_font.colour_index = 10
    pink_delisting_apply.font = pink_font
    pink_delisting_apply.alignment = align_date
    styles["pink_delisting_apply"] = pink_delisting_apply

    yellow_pink_delisting_apply = xlwt.XFStyle()
    yellow_pink_delisting_apply.font = pink_font
    yellow_pink_delisting_apply.alignment = align_date
    yellow_pink_delisting_apply.pattern = pattern
    styles["yellow_pink_delisting_apply"] = yellow_pink_delisting_apply

    # 要点列样式（左对齐，适配文字）
    memo_left = xlwt.XFStyle()
    memo_left.font = font
    align_memo = xlwt.Alignment()
    align_memo.horz = xlwt.Alignment.HORZ_LEFT
    memo_left.alignment = align_memo
    styles["memo_left"] = memo_left

    yellow_memo_left = xlwt.XFStyle()
    yellow_memo_left.font = font
    yellow_memo_left.alignment = align_memo
    yellow_memo_left.pattern = pattern
    styles["yellow_memo_left"] = yellow_memo_left

    return styles


# ---------------------- 15. Sheet写入函数（新增业绩反转【要点】列） ----------------------
def write_sheet_data(sheet, data_list, styles, row_height=11 * 20, is_strategy_sheet=False,
                     summary_data=None, summary_percent=None, total_capital=500000, is_dividend_sheet=False,
                     is_fund_sheet=False, is_small_cap_sheet=False, is_hot_development_sheet=False,
                     is_performance_reversal_sheet=False, is_limit_up_callback_sheet=False,
                     is_combined_stock_sheet=False):
    col_widths = {
        0: 8, 1: 13, 2: 8, 3: 8, 4: 10, 5: 9, 6: 6, 7: 12,
        8: 10, 9: 12, 10: 18, 11: 22, 12: 25  # 12列=要点
    }
    for col_idx, width in col_widths.items():
        sheet.col(col_idx).width = width * 256

    # 表头：业绩反转新增【要点】
    if is_fund_sheet or is_dividend_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新分红日期", "去年对应分红日期"]
    elif is_performance_reversal_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报日期", "摘帽申请日期", "要点"]  # 这里加了要点
    elif is_combined_stock_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报/分红日期", "去年对应年报/分红日期"]
    elif is_small_cap_sheet or is_hot_development_sheet or is_limit_up_callback_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报日期", "去年对应年报日期"]
    else:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略"]

    sheet.row(0).height = row_height
    for col_idx, header in enumerate(headers):
        sheet.write(0, col_idx, header, styles["header"])

    if is_strategy_sheet and data_list:
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

    row_idx = 1
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
            sheet.write(row_idx, 8, f"{total_cumulative_percent}%", styles["yellow_total_percent"])
            sheet.write(row_idx, 9, strategy, styles["yellow_strategy"])

            if is_performance_reversal_sheet:
                dates = performance_reversal_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
                delisting_date = performance_reversal_delisting_application_dict.get(code, "")
                if is_delisting_date_less_than_2months(code):
                    sheet.write(row_idx, 11, delisting_date, styles["yellow_pink_delisting_apply"])
                else:
                    sheet.write(row_idx, 11, delisting_date, styles["yellow_delisting_apply_right"])
                # 写入要点
                memo = performance_reversal_memo_dict.get(code, "")
                sheet.write(row_idx, 12, memo, styles["yellow_memo_left"])

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

            if is_performance_reversal_sheet:
                dates = performance_reversal_annual_report_dict.get(code, ["", ""])
                sheet.write(row_idx, 10, dates[0], styles["date_right"])
                delisting_date = performance_reversal_delisting_application_dict.get(code, "")
                if is_delisting_date_less_than_2months(code):
                    sheet.write(row_idx, 11, delisting_date, styles["pink_delisting_apply"])
                else:
                    sheet.write(row_idx, 11, delisting_date, styles["delisting_apply_right"])
                # 写入要点
                memo = performance_reversal_memo_dict.get(code, "")
                sheet.write(row_idx, 12, memo, styles["memo_left"])

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


# ---------------------- 16. 数据读取与处理 ----------------------
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
            code_str = str(int(float(code))).strip()
            code = code_str.zfill(6)
        except:
            code = str(code).strip()
        if code in position_dict:
            position_dict[code]["总数量"] += count
        else:
            position_dict[code] = {"名称": name, "总数量": count, "当前价": price}

total_capital = 500000
for code, info in position_dict.items():
    info["金额"] = int(info["总数量"] * info["当前价"])
    info["仓位百分比"] = round((info["金额"] / total_capital) * 100, 1)

# ---------------------- 17. 数据分组 ----------------------
strategy_groups = defaultdict(list)
full_data = []
combined_stock_data = []
combined_strategies = ["分红股", "业绩反转", "小盘猛牛", "热点发展", "涨停回调", "配债股"]

sorted_positions = sorted(position_dict.items(), key=lambda x: x[1]["金额"], reverse=True)
cumulative_amount = 0
rank = 1

for code, info in sorted_positions:
    cumulative_amount += info["金额"]
    total_cumulative_pct = round((cumulative_amount / total_capital) * 100, 1)

    if code in multi_strategy_codes:
        strategies = multi_strategy_codes[code]
    else:
        base_strategy = strategy_dict.get(code, "空策略") or "空策略"
        strategies = [base_strategy]

    main_strategy = strategies[0]
    full_data.append((code, info, main_strategy, rank, cumulative_amount, total_cumulative_pct))

    for strategy in strategies:
        strategy_groups[strategy].append((code, info, strategy, rank, cumulative_amount, total_cumulative_pct))
        if strategy in combined_strategies:
            combined_stock_data.append((code, info, strategy, rank, cumulative_amount, total_cumulative_pct))
    rank += 1

# ---------------------- 18. 策略汇总 ----------------------
unique_codes = set()
strategy_total_amount = {}
for strategy, items in strategy_groups.items():
    total = 0
    for item in items:
        code = item[0]
        if code not in unique_codes:
            total += item[1]["金额"]
            unique_codes.add(code)
    strategy_total_amount[strategy] = total

strategy_total_percent = {
    k: round((v / total_capital) * 100, 1)
    for k, v in strategy_total_amount.items()
}

strategy_order = [
    "分红股", "分红基", "reit", "业绩反转", "小盘猛牛",
    "热点发展", "配债策略", "涨停回调", "可转债",
    "套利基", "超跌基", "海外基", "配债股", "空策略"
]
order_dict = {strategy: idx for idx, strategy in enumerate(strategy_order)}
sorted_strategy_names = sorted(
    strategy_total_amount.keys(),
    key=lambda x: order_dict.get(x, len(strategy_order))
)

summary_data = {n: strategy_total_amount[n] for n in sorted_strategy_names}
summary_percent = {n: strategy_total_percent[n] for n in sorted_strategy_names}

# ---------------------- 19. 生成Excel ----------------------
final_workbook = xlwt.Workbook(encoding="utf-8")
styles = create_styles()

main_sheet_name = f"总仓位{len(sorted_strategy_names)}"
main_sheet = final_workbook.add_sheet(main_sheet_name)
write_sheet_data(
    main_sheet, full_data, styles,
    is_strategy_sheet=False,
    summary_data=summary_data,
    summary_percent=summary_percent,
    total_capital=total_capital
)

if combined_stock_data:
    combined_sheet = final_workbook.add_sheet("合并股票")
    write_sheet_data(
        combined_sheet, combined_stock_data, styles,
        is_strategy_sheet=True,
        total_capital=total_capital,
        is_combined_stock_sheet=True
    )

for strategy_name in sorted_strategy_names:
    group_data = strategy_groups[strategy_name]
    if not group_data:
        continue

    safe_name = strategy_name.replace("/", "").replace("\\", "").replace(":", "").replace("*", "").replace("?",
                                                                                                           "").replace(
        "[", "").replace("]", "")[:31]
    if not safe_name:
        safe_name = "空策略"

    strategy_sheet = final_workbook.add_sheet(safe_name)

    is_fund_sheet = (strategy_name == "分红基")
    is_dividend_sheet = (strategy_name == "分红股")
    is_small_cap_sheet = (strategy_name == "小盘猛牛")
    is_hot_development_sheet = (strategy_name == "热点发展")
    is_performance_reversal_sheet = (strategy_name == "业绩反转")
    is_limit_up_callback_sheet = (strategy_name == "涨停回调")

    write_sheet_data(
        strategy_sheet, group_data, styles,
        is_strategy_sheet=True,
        total_capital=total_capital,
        is_dividend_sheet=is_dividend_sheet,
        is_fund_sheet=is_fund_sheet,
        is_small_cap_sheet=is_small_cap_sheet,
        is_hot_development_sheet=is_hot_development_sheet,
        is_performance_reversal_sheet=is_performance_reversal_sheet,
        is_limit_up_callback_sheet=is_limit_up_callback_sheet
    )

final_workbook.save("__00_总仓位.xls")

print("✅ 生成完成！")
