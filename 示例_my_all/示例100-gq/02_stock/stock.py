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
    "000001": ["25年报 2026-03-21", "预案公布日:2025-03-26"],
    "605368": ["25年报 2026/4/22", "预案公布日:2025-03-26"],
    "600985": ["25年报 2026/3/28", "预案公布日:2025-03-28"],
    "601916": ["25年报 2026/3/31", "预案公布日:2025-03-29"],
    "601169": ["25年报 2026-04-23", "预案公布日:2025-03-29"],
    "002807": ["25报 2026-03-31", "预案公布日:2025-03-29"],
    "600188": ["25年报 2026/3/28", "预案公布日:2025-03-29"],
    "600016": ["25年报 2026-03-31", "预案公布日:2025-04-15"],
    "600681": ["25年报 2026-04-23", "预案公布日:2025-04-23"],
    "600256": ["25年报 2026-04-24", "预案公布日:2025-04-25"],
    "603801": ["25年报 2026-04-30", "预案公布日:2025-04-29"],
    "002267": ["25年报 2026-04-28", "预案公布日:2025-04-29"],
    "600219": ["25年年报 2026-03-27", "预案公布日:2025-05-05"],
    "600755": ["25年报 2026-04-23", "--"],
    "601006": ["25年报 2026-04-30", "--"],
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
    "603789": "业绩反转", "300173": "业绩反转", "600421": "业绩反转", "600581": "业绩反转",
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
    "002496": ["25年报 2026-03-31", ""],
    "002630": ["25年报 2026-04-27", ""],
    "600735": ["25年报 2026-04-30", ""],
    "002122": ["25年报 2026-04-24", ""],
    "600759": ["25年报 2026-04-23", ""],
    "600169": ["25年报 2026-04-21", ""],
    "300044": ["25年报 2026-03-31", ""],
    "002124": ["25年报 2026-04-29", ""],
    "000698": ["25年报 2026-03-28", ""],
    "600339": ["25年报 2026-04-11", ""],
    "600777": ["25年报 2026-04-24", ""],
    "300506": ["25年报 2026-04-10", ""],
    "002689": ["25年报 2026-04-29", ""],
    "002762": ["25年报 2026-04-16", "--"],
    "002424": ["25年报 2026-04-24", "--"],
    "300343": ["25年报 2026-04-15", "--"],
    "002076": ["25年报 2026-04-29", "--"],
    "000903": ["25年报 2026-04-28", "--"],
    "000595": ["25年报 2026-04-18", "--"],
    "300527": ["25年报 2026-04-29", "--"],
    "600636": ["25年报 2026-04-25", "--"],
    "002713": ["25年报 2026-04-27", "--"],
    "603595": ["25年报 2026-04-18", "--"],
    "300211": ["25年报 2026-04-24", "--"],
    "002693": ["25年报 2026-04-29", "--"],
    "002305": ["25年报 2026-04-27", "--"],
    "000000": ["待定", "--"],
    "000929": ["25年报 2026-03-31", ""],
    "603789": ["25年报 2026-04-25", ""],
    "300173": ["25年报 2026-04-29", ""],
    "600421": ["25年报 2026-04-30", ""],
    "300366": ["25年报 2026-04-24", ""],
    "300460": ["25年报 2026-04-27", ""],
}

# ---------------------- 8. 业绩反转申请摘帽日期字典 ----------------------
performance_reversal_delisting_application_dict = {
    "600358": "25年报 2026-03-21",
    "000929": "25年报 2026-04-13",
    "002496": "25年报 2026-04-18",
    "002762": "25年报 2026-04-16",
    "000595": "25年报 2026-04-18",
    "300211": "25年报 2026-04-24",
    "600777": "25年报 2026-04-24",
    "603789": "25年报 2026-04-25",
    "600636": "25年报 2026-04-25",
    "002713": "25年报 2026-04-27",
    "002305": "25年报 2026-04-27",
    "003032": "25年报 2026-04-28",
    "002693": "25年报 2026-04-29",
    "002076": "25年报 2026-04-29",
    "600892": "25年报 2026-04-30",
    "600421": "25年报 2026-04-30",
    "002124": "预重整日期 2026-05-09",
    "300311": "26-07-18",
    "000903": "26-08-08",
    "300527": "26-09-16",
    "300366": "26-10-24",
    "603595": "26-11-13",
    "002122": "26-11-13",
    "000698": "26-11-29",
    "002689": "26-12-20",
    "600624": "26-12-26",
    "600169": "26-12-29",
    "300460": "27-01-12",
    "000821": "27-01-16",
    "300173": "27-02-06",
    "000488": "摘帽日期 待定",
    "600537": "预重整日期 待定",
    "002055": "摘帽日期 待定",
    "002630": "摘帽日期 待定",
    "002512": "摘帽日期 待定",
    "600581": "摘帽日期 待定",
    "600735": "重整日期 待定",
}

# 周线 字典 (示例：半周线、空、周线等)
performance_reversal_week_line_dict = {
    "000595": "    半周线",  # 宝实
    "000698": "    否",  # 沈华
    "000821": "    半周线",  # 京机
    "000903": "    否",  # 云动
    "000929": "    否",  # 兰黄
    "002055": "    否",  # 得润
    "002076": "    否",  # 星光
    "002122": "    否",  # 汇洲
    "002124": "    半周线",  # 天邦食品
    "002305": "    否",  # 南置
    "002424": "    否",  # 百灵
    "002496": "    否",  # 辉丰
    "002512": "    半周线",  # 达华
    "002630": "    周线涨",  # 华西         //买入
    "002689": "    周线涨",  # 远智
    "002693": "    否",  # 双成
    "002713": "    否",  # 东易
    "002762": "    否",  # 金比
    "003032": "    否",  # 传智
    "300044": "    否",  # 赛为
    "300173": "    半周线",  # 福能
    "300211": "    否",  # 亿通
    "300343": "    否",  # 联创
    "300366": "    否",  # 创意
    "300460": "    否",  # 惠伦
    "300506": "    否",  # 名家汇
    "300527": "    周线涨",  # 应急
    "600169": "    非周帽",  # 太重
    "600358": "    否",  # 联合
    "600421": "    否",  # 华嵘
    "600581": "    否",  # 八钢
    "600624": "    否",  # 复华
    "600636": "    半周线",  # 国化
    "600735": "    否",  # 新华锦
    "600759": "    否",  # 洲际油气
    "600777": "    否",  # 新潮
    "600892": "    否",  # 大晟
    "603595": "    周线涨",  # 东尼
    "603789": "    否",  # 星农
}

# ===================== 业绩反转 - 合并字典：远涨,远跌 =====================
# 格式：key=股票代码, value="远涨数值,远跌数值"
performance_reversal_far_dict = {
    #持仓中
    "600636": "07, 69 ",    # 国化
    "603789": "10, 69 ",    # 星农
    "003032": "30, 85 ",    # 传智
    "002076": "88, 54 ",    # 星光
    "000903": "61, 58 ",    # 云动
    "300527": "64, 38 ",    # 应急
    "300366": "09, 72 ",   # 创意
    "603595": "17, 81 ",   # 东尼
    "002122": "69, 51 ",    # 汇洲
    "600624": "65, 52 ",    # 复华
    "600169": "39, 33 ",    # 太重
    "000821": "66, 57 ",    # 京机
    "300173": "54, 61 ",    # 福能
    "002630": "42, 63 ",    # 华西         //买入
    "002512": "74, 52 ",    # 达华
    "002055": "45, 64 ",    # 得润

     # ready
    "002124": "20, 78 ",    # 天邦食品
    "600892": "52, 52 ",    # 大晟
    "600421": "41, 59 ",    # 华嵘
    "000929": "96, 32 ",    # 兰黄
    "600581": "18, 74 ",   # 八钢
    "600358": "184, 27 ",  # 联合
    "000698": "51, 55 ",    # 沈华
    "002496": "66, 51 ",    # 辉丰
    "600735": "96, 35 ",    # 新华锦
    "600759": "185, 41 ",   # 洲际油气
    "002689": "79, 49 ",    # 远智
    "002762": "75, 67 ",    # 金比
    "002424": "69, 58 ",    #百灵
    "300460": "58, 70 ",    # 惠伦

     # 涨幅过大
    "300044": "375, 12 ",    # 赛为
    "600777": "294, 11 ",    # 新潮
    "300506": "290, 57 ",    # 名家汇
    "300343": "131, 79 ",   # 联创
    "000595": "209, 50 ",    # 宝实
    "002713": "626, 23 ",    # 东易
    "300211": "101, 48 ",     # 亿通
    "002693": "118, 81 ",    # 双成
    "002305": "89, 52 ",     # 南置
}

# ===================== 业绩反转 - 审计列字典 =====================
performance_reversal_audit_dict = {
    "000595": "    财务亏损 + 营收准ok",  # 宝实
    "000698": "    财务造假 + 已ok",  # 沈华
    "000821": "    财务造假 + 已ok",  # 京机
    "000903": "    财务造假 + 已ok",  # 云动
    "000929": "    财务亏损 + 已ok",  # 兰黄
    "002055": "    财务造假 + 已ok",  # 得润
    "002076": "    财务亏损 + 已ok",  # 星光
    "002122": "    财务造假 + 已ok",  # 汇洲
    "002124": "    正在重整 + 重整准ok",  # 天邦食品
    "002305": "    财务造假 + 已ok",  # 南置
    "002424": "    财务造假 + 已ok",  # 百灵
    "002496": "    无重整 + 财务亏损 + 已ok",  # 辉丰
    "002512": "    财务造假 + 已ok",  # 达华
    "002630": "    否定意见 + 将披星",  # 华西
    "002689": "    财务造假 + 已ok",  # 远智
    "002693": "    财务亏损 + 未明",  # 双成
    "002713": "    财务造假 + 已ok",  # 东易
    "002762": "    财务亏损 + 营收已ok",  # 金比
    "003032": "    财务亏损 + 或将摘帽",  # 传智
    "300044": "    正在重整 + 未明",  # 赛为
    "300173": "    财务造假 + 已ok",  # 福能
    "300211": "    财务亏损 + 营收已ok",  # 亿通
    "300343": "    财务造假 + 已ok",  # st联创
    "300366": "    财务造假 + 已ok",  # 创意
    "300460": "    财务造假 + 已ok",  # 惠伦
    "300506": "    财务亏损&持续经营 + 未明",  # 名家汇
    "300527": "    财务造假 + 已ok",  # 应急
    "600169": "    财务造假 + 已ok",  # 太重
    "600358": "    财务造假 + 已ok",  # 联合
    "600421": "    财务亏损 +  未明或雷",  # 华嵘
    "600581": "    财务亏损&净资产为负 + 未明",  # 八钢
    "600624": "    财务造假 + 已ok",  # 复华
    "600636": "    财务亏损 + 未明或雷",  # 国化
    "600735": "    挪用4亿&正在重整 + 未明",  # 新华锦
    "600759": "    已摘帽 + 已ok",  # 洲际油气
    "600777": "    审计非标 + 未明",  # 新潮
    "600892": "    财务亏损 + 未明",  # 大晟
    "603595": "    财务造假 + 已ok",  # 东尼
    "603789": "    财务造假&财务亏损 + 准ok",  # 星农

}

# ---------------------- 新增：业绩反转 要点字典 ----------------------
performance_reversal_memo_dict = {
    "000595": "    轴承风电光伏及储能电站 + 财务亏损 + 或将摘帽",  # 宝实
    "000698": "    烧碱&央企 + 财务造假 + 或将摘帽",  # 沈华
    "000821": "    钙钛矿光伏设备龙头 + 财务造假 + 或将摘帽",  # 京机
    "000903": "    小缸径柴油机&无人机 + 财务造假 + 或将摘帽",  # 云动
    "000929": "    白酒饮料 + 已完成重整 + 财务亏损 + 或将摘帽",  # 兰黄
    "002055": "    电子连接器 + 财务造假 + 正在整改摘帽未知",  # 得润
    "002076": "    传统照明&锂电光伏 + 财务亏损 + 或将摘帽",  # 星光
    "002122": "    工业母机&AI数据算力 + 财务造假 + 或将摘帽",  # 汇洲
    "002124": "    生猪&水产饲料 + 预重整押金 + 正在重整 + 或将戴帽",  # 天邦食品
    "002305": "    长租公寓 + 已央企重整 + 财务造假 + 或将摘帽",  # 南置
    "002424": "    苗药龙头 + 财务造假 + 正在处罚摘帽不明 + 大幅质押",  # 百灵
    "002496": "    农药龙头&石化仓储&生物农业 + 财务亏损 + 或将摘帽",  # 辉丰
    "002512": "    卫星组件运行 + 财务造假 + 正在整改摘帽未知",  # 达华
    "002630": "    锅炉&电厂环保工程&海外大订单 + 重整进行 + 否定意见 + 将披星",  # 华西
    "002689": "    电梯风电 + 财务造假 + 或将摘帽",  # 远智
    "002693": "    多肽药品 + 财务亏损 + 或将摘帽",  # 双成
    "002713": "    算力中心 + 已重整优质资产注入 + 或将摘帽",  # 东易
    "002762": "    母婴高端品牌&母婴补贴 + 或只摘星",  # 金比
    "003032": "    职业培训 + 财务亏损 + 或将摘帽",  # 传智
    "300044": "    无人机&机器人 + 财务亏损&持续经营 + 正在重整 + 摘帽不明",  # 赛为
    "300173": "    锂电装备龙头 + 财务造假 + 或将摘帽",  # 福能
    "300211": "    传感器&AI芯片 + 美国华米爹 + 财务亏损 + 或将摘帽",  # 亿通
    "300343": "    氟化工锂电池 + 财务造假 + 或将摘帽",  # st联创
    "300366": "    大数据AI&卫星通信组件 + 财务造假 + 或将摘帽",  # 创意
    "300460": "    石英晶体元器件 + 财务造假 + 或将摘帽",  # 惠伦
    "300506": "    智慧灯杆 + 财务亏损&持续经营 + 或只摘星",  # 名家汇
    "300527": "    浮桥军工&国资 + 财务造假 + 或将摘帽",  # 应急
    "600169": "    风力发电设备&矿山设备 + 财务造假 + 或将摘帽",  # 太重
    "600358": "    互联网营销 + 润田重组 + 财务造假 + 已申请摘帽",  # 联合
    "600421": "    装配式建筑构件 + 已重整注入保底资产 + 财务亏损 + 或将摘帽 + 负债91",  # 华嵘
    "600581": "    钢铁&煤矿 + 或央企注资产&债务豁免 + 财务亏损&净资产为负 + 或将27年摘帽 + 负债106",  # 八钢
    "600624": "    中成药&软件 + 财务造假 + 或将摘帽",  # 复华
    "600636": "    教育录播 + 财务亏损 + 或将摘帽",  # 国化
    "600735": "    石墨转型&发制品&外贸打底 + 挪用4亿 + 正在重整 + 摘帽不明",  # 新华锦
    "600759": "    哈萨克斯坦油田 + 伊拉克油田 + 批发市场 + 已摘帽",  # 洲际油气
    "600777": "    美国油气 + 审计非标 + 或将摘帽",  # 新潮
    "600892": "    游戏文旅国企老爹 + 财务亏损 + 或将摘帽 + 负债96",  # 大晟
    "603595": "    半导体 + 无重整 + 财务造假 + 或将摘帽",  # 东尼
    "603789": "    农机汽配 + 已完成重整 + 财务亏损 + 或只摘星",  # 星农
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


# def get_performance_reversal_sort_key(item):
#     code = item[0]
#     delisting_apply_date = extract_delisting_apply_date(code)
#     next_date_str = performance_reversal_annual_report_dict.get(code, ["待定", ""])[0]
#     next_date = extract_date_from_str(next_date_str)
#     return (delisting_apply_date, next_date)
def get_performance_reversal_sort_key(item):
    code = item[0]
    date_str = performance_reversal_delisting_application_dict.get(code, "")
    return date_str or "9999-12-31"  # 空日期排最后

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
    pink_font.colour_index = 14   # 红色10 粉红色14
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

    # 周线列专用：半周线 / 周线涨 粉红色字体
    week_pink_font = xlwt.Font()
    week_pink_font.height = 9 * 20
    week_pink_font.colour_index = 14  # 粉红色

    # 普通行 粉红色
    week_pink_style = xlwt.XFStyle()
    week_pink_style.font = week_pink_font
    styles["week_pink"] = week_pink_style

    # 黄色行 粉红色（黄底）
    week_yellow_pink_style = xlwt.XFStyle()
    week_yellow_pink_style.font = week_pink_font
    week_yellow_pink_style.pattern = pattern
    week_yellow_pink_style.alignment = align_date
    styles["week_yellow_pink"] = week_yellow_pink_style

    # 远涨专用颜色
    far_up_pink_font = xlwt.Font()
    far_up_pink_font.height = 9 * 20
    far_up_pink_font.colour_index = 14  # 粉红

    far_up_red_font = xlwt.Font()
    far_up_red_font.height = 9 * 20
    far_up_red_font.colour_index = 10  # 红色

    # 普通行
    far_up_pink = xlwt.XFStyle()
    far_up_pink.font = far_up_pink_font
    styles["far_up_pink"] = far_up_pink

    far_up_red = xlwt.XFStyle()
    far_up_red.font = far_up_red_font
    styles["far_up_red"] = far_up_red

    # 黄色行（黄底）
    far_up_yellow_pink = xlwt.XFStyle()
    far_up_yellow_pink.font = far_up_pink_font
    far_up_yellow_pink.pattern = pattern
    far_up_yellow_pink.alignment = align_date
    styles["far_up_yellow_pink"] = far_up_yellow_pink

    far_up_yellow_red = xlwt.XFStyle()
    far_up_yellow_red.font = far_up_red_font
    far_up_yellow_red.pattern = pattern
    far_up_yellow_red.alignment = align_date
    styles["far_up_yellow_red"] = far_up_yellow_red

    # 远跌专用颜色
    far_down_pink_font = xlwt.Font()
    far_down_pink_font.height = 9 * 20
    far_down_pink_font.colour_index = 14  # 粉红

    far_down_red_font = xlwt.Font()
    far_down_red_font.height = 9 * 20
    far_down_red_font.colour_index = 10  # 红色

    # 普通行
    far_down_pink = xlwt.XFStyle()
    far_down_pink.font = far_down_pink_font
    styles["far_down_pink"] = far_down_pink

    far_down_red = xlwt.XFStyle()
    far_down_red.font = far_down_red_font
    styles["far_down_red"] = far_down_red

    # 黄色行（黄底）
    far_down_yellow_pink = xlwt.XFStyle()
    far_down_yellow_pink.font = far_down_pink_font
    far_down_yellow_pink.pattern = pattern
    far_down_yellow_pink.alignment = align_date
    styles["far_down_yellow_pink"] = far_down_yellow_pink

    far_down_yellow_red = xlwt.XFStyle()
    far_down_yellow_red.font = far_down_red_font
    far_down_yellow_red.pattern = pattern
    far_down_yellow_red.alignment = align_date
    styles["far_down_yellow_red"] = far_down_yellow_red

    # ===================== 审计列 颜色样式 =====================
    audit_pink_font = xlwt.Font()
    audit_pink_font.height = 9 * 20
    audit_pink_font.colour_index = 14  # 粉红

    audit_red_font = xlwt.Font()
    audit_red_font.height = 9 * 20
    audit_red_font.colour_index = 10  # 红色

    # 普通行
    audit_pink = xlwt.XFStyle()
    audit_pink.font = audit_pink_font
    styles["audit_pink"] = audit_pink

    audit_red = xlwt.XFStyle()
    audit_red.font = audit_red_font
    styles["audit_red"] = audit_red

    # 黄色行（黄底）
    audit_yellow_pink = xlwt.XFStyle()
    audit_yellow_pink.font = audit_pink_font
    audit_yellow_pink.pattern = pattern
    audit_yellow_pink.alignment = align_date
    styles["audit_yellow_pink"] = audit_yellow_pink

    audit_yellow_red = xlwt.XFStyle()
    audit_yellow_red.font = audit_red_font
    audit_yellow_red.pattern = pattern
    audit_yellow_red.alignment = align_date
    styles["audit_yellow_red"] = audit_yellow_red


    return styles


# ---------------------- 15. Sheet写入函数（远涨远跌移到摘帽后、要点前） ----------------------
def write_sheet_data(sheet, data_list, styles, row_height=11 * 20, is_strategy_sheet=False,
                     summary_data=None, summary_percent=None, total_capital=500000, is_dividend_sheet=False,
                     is_fund_sheet=False, is_small_cap_sheet=False, is_hot_development_sheet=False,
                     is_performance_reversal_sheet=False, is_limit_up_callback_sheet=False,
                     is_combined_stock_sheet=False):
    col_widths = {
        0: 8, 1: 10, 2: 8, 3: 8, 4: 10, 5: 9, 6: 6, 7: 10,
        8: 10, 9: 8, 10: 15, 11: 10, 12: 5, 13: 5, 14: 25, 15: 25
    }
    for col_idx, width in col_widths.items():
        sheet.col(col_idx).width = width * 256

    # 表头
    if is_fund_sheet or is_dividend_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新分红日期", "去年对应分红日期"]
    elif is_performance_reversal_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "摘帽申请日期", "周线", "远涨", "远跌", "要点"]
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
                # 摘帽申请日期
                delisting_date = performance_reversal_delisting_application_dict.get(code, "")
                if is_delisting_date_less_than_2months(code):
                    sheet.write(row_idx, 10, delisting_date, styles["yellow_pink_delisting_apply"])
                else:
                    sheet.write(row_idx, 10, delisting_date, styles["yellow_delisting_apply_right"])

                # 周线
                week_line = performance_reversal_week_line_dict.get(code, "")
                week_line_stripped = week_line.strip()
                if week_line_stripped in ("半周线", "周线涨"):
                    sheet.write(row_idx, 11, week_line, styles["week_yellow_pink"])
                else:
                    sheet.write(row_idx, 11, week_line, styles["yellow"])

                # 远涨 + 远跌
                far_data = performance_reversal_far_dict.get(code, ",").split(",")
                far_up = far_data[0].strip()
                far_down = far_data[1].strip()

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 12, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 12, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 12, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 12, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 13, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 13, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 13, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 13, far_down, styles["yellow"])

                # 审计：已ok → 粉红，雷 → 红色
                audit_text = performance_reversal_audit_dict.get(code, "")
                audit_stripped = audit_text.strip()
                if audit_stripped.endswith("已ok"):
                    sheet.write(row_idx, 14, audit_text, styles["audit_yellow_pink"])
                elif audit_stripped.endswith("雷"):
                    sheet.write(row_idx, 14, audit_text, styles["audit_yellow_red"])
                else:
                    sheet.write(row_idx, 14, audit_text, styles["yellow"])

                # 要点
                memo = performance_reversal_memo_dict.get(code, "")
                sheet.write(row_idx, 15, memo, styles["yellow_memo_left"])

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
                # 摘帽申请日期
                delisting_date = performance_reversal_delisting_application_dict.get(code, "")
                if is_delisting_date_less_than_2months(code):
                    sheet.write(row_idx, 10, delisting_date, styles["pink_delisting_apply"])
                else:
                    sheet.write(row_idx, 10, delisting_date, styles["delisting_apply_right"])

                # 周线
                week_line = performance_reversal_week_line_dict.get(code, "")
                week_line_stripped = week_line.strip()
                if week_line_stripped in ("半周线", "周线涨"):
                    sheet.write(row_idx, 11, week_line, styles["week_pink"])
                else:
                    sheet.write(row_idx, 11, week_line, styles["base"])

                # 远涨 + 远跌
                far_data = performance_reversal_far_dict.get(code, ",").split(",")
                far_up = far_data[0].strip()
                far_down = far_data[1].strip()

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 12, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 12, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 12, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 12, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 13, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 13, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 13, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 13, far_down, styles["base"])

                # 审计：已ok → 粉红，雷 → 红色
                audit_text = performance_reversal_audit_dict.get(code, "")
                audit_stripped = audit_text.strip()
                if audit_stripped.endswith("已ok"):
                    sheet.write(row_idx, 14, audit_text, styles["audit_pink"])
                elif audit_stripped.endswith("雷"):
                    sheet.write(row_idx, 14, audit_text, styles["audit_red"])
                else:
                    sheet.write(row_idx, 14, audit_text, styles["base"])

                # 要点
                memo = performance_reversal_memo_dict.get(code, "")
                sheet.write(row_idx, 15, memo, styles["memo_left"])

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
# 注释/删除：合并股票相关的数据初始化
# combined_stock_data = []
# combined_strategies = ["分红股", "业绩反转", "小盘猛牛", "热点发展", "涨停回调", "配债股"]

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
        # 注释/删除：合并股票数据添加逻辑
        # if strategy in combined_strategies:
        #     combined_stock_data.append((code, info, strategy, rank, cumulative_amount, total_cumulative_pct))
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

# 注释/删除：合并股票sheet创建逻辑
# if combined_stock_data:
#     combined_sheet = final_workbook.add_sheet("合并股票")
#     write_sheet_data(
#         combined_sheet, combined_stock_data, styles,
#         is_strategy_sheet=True,
#         total_capital=total_capital,
#         is_combined_stock_sheet=True
#     )

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