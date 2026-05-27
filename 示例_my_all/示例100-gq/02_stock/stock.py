
# 远涨 -- 小于50时显示粉红色字体，大于70时显示红色字体
# 远跌 -- 大于60时显示粉红色字体，小于30时显示红色字体


from datetime import datetime, timedelta
import xlrd
import xlwt
from collections import defaultdict
import re



# ============================== 一。每周维护字典  ===============================

# ---------------------- 0.1：分红股， 远涨远跌字典 ----------------------
stock_dividend_struct_dict = {
    "600755": "0.201, -0.299",  # 厦门国贸
    "600681": "0.348, -0.321",  # 百川能源
    "002807": "0.492, -0.147",  # 江阴银行
    "601169": "0.425, -0.296",  # 北京银行
    "603801": "0.010, -0.707",  # 志邦家居
    "000001": "0.439, -0.218",  # 平安银行
    "601916": "0.384, -0.224",  # 浙商银行
    "605368": "0.036, -0.485",  # 蓝天燃气
    "600016": "0.205, -0.358",  # 民生银行
    "601006": "0.095, -0.238",  # 大秦铁路

    # # 多策略
    # "600681": "45, 27 ",  # 百川能源
    # "605368": "52, 45 ",  # 蓝天燃气
    # "600755": "44, 27 ",  # 厦门国贸
}

# ---------------------- 0.2：涨停回调, 远涨远跌字典 ----------------------
limit_up_callback_struct_dict = {
    "001202": "1.273, -0.330",  # 炬申股份
    "605368": "0.287, -0.493",  # 蓝天燃气
    "600681": "0.317, -0.337",  # 百川能源
    "605388": "0.518, -0.471",  # 均瑶健康
    "600662": "0.367, -0.333",  # 外服控股
    "600814": "0.497, -0.399",  # 杭州解百
    "600755": "0.296, -0.300",  # 厦门国贸
    "600858": "0.528, -0.357",  # 银座股份

    # # 多策略
    # "600681": "45, 27 ",  # 百川能源
    # "605368": "0.02, 0.49 ",  # 蓝天燃气
    # "600755": "44, 27 ",  # 厦门国贸
    #
    # "001202": "155, 29 ",  # 炬申股份
}


# ---------------------- 0.3：小盘猛牛, 远涨远跌字典 ----------------------

small_cap_callback_struct_dict = {
    "300891": "0.38, 0.39 ",    # 惠云钛业
}

# ---------------------- 0.4：热点发展, 远涨远跌字典 ----------------------

hot_development_struct_dict = {
    "000582": "1.26, 0 ",  # 北部湾港
}

# ---------------------- 0.5：配债股, 远涨远跌字典 ----------------------

bond_allot_struct_dict = {
    "603759": "0.57, 0.5 ",  # 海天股份

    # 多策略
    "001202": "1.27, 0.21 ",  # 炬申股份
}


# ---------------------- 0.6：分红基, 远涨远跌字典 ----------------------
dividend_fund_struct_dict = {

    "510720": "0.184, -0.090",  # 红利国企ETF国泰
    "515450": "0.440, -0.041",  # 红利低波50ETF南方
    "515300": "0.331, -0.096",  # 300红利低波ETF嘉实
    "159307": "0.313, -0.055",  # 红利低波100ETF博时
    "510880": "0.298, -0.077",  # 红利ETF华泰柏瑞
    "513820": "0.500, -0.071",  # 港股通红利ETF汇添富
    "180102": "0.012, -0.484",  # 华夏合肥高新REIT

}

# ---------------------- 0.7：超跌基, 远涨远跌字典 ----------------------
overdown_fund_struct_dict = {
    "512010": "0.11, 0.37 ",  # 医药ETF
    "512290": "0.18, 0.32 ",  # 生物医药
    "515710": "0.04, 0.41 ",  # 食品ETF
}

# ---------------------- 0.8：海外基, 远涨远跌字典 ----------------------
oversea_fund_struct_dict = {
    "161126": "0.16, 0.17 ",  # 标普医药
    "164824": "0.16, 0.25 ",  #	印度基金
    "159329": "0.03, 0.31 ",  # 沙特ETF南方
}

# ---------------------- 0.9：可转债, 远涨远跌字典 ----------------------
swapbond_fund_struct_dict = {
    "127025": "0.11, 0.18 ",  # 冀东转债
}


# ===================== 1.0：业绩反转，远涨远跌字典 =====================
# 格式：key=股票代码, value="远涨数值,远跌数值"
performance_reversal_far_dict = {
    "003032": "0.504, -0.647",  # *ST传智
    "002124": "0.414, -0.576",  # 天邦食品
    "000903": "0.191, -0.694",  # ST云动
    "300527": "0.534, -0.400",  # ST应急
    "300366": "0.171, -0.712",  # ST创意
    "002122": "0.574, -0.528",  # ST汇洲
    "000698": "0.438, -0.468",  # ST沈化
    "002689": "0.589, -0.437",  # ST远智
    "600624": "0.644, -0.520",  # ST复华
    "600169": "0.317, -0.231",  # ST太重
    "300460": "0.849, -0.432",  # ST惠伦
    "000821": "0.071, -0.637",  # ST京机
    "300173": "0.336, -0.604",  # ST福能
    "600759": "0.350, -0.708",  # ST洲际
    "000639": "0.068, -0.724",  # ST西王
    "600370": "0.149, -0.661",  # *ST三房
    "688201": "0.474, -0.717",  # ST信安
    "000010": "0.604, -0.575",  # *ST美丽
    "301030": "0.268, -0.778",  # *ST壮净
    "600735": "0.885, -0.364",  # ST新华锦
    "600053": "0.049, -0.628",  # *ST九鼎
    "600581": "0.082, -0.523",  # *ST八钢
    "002691": "0.398, -0.619",  # *ST冀凯
    "000488": "0.350, -0.585",  # ST晨鸣
    "002360": "0.539, -0.237",  # ST同德
    "000826": "0.674, -0.576",  # *ST启环
    "600537": "0.463, -0.650",  # *ST亿晶
    "600734": "0.104, -0.694",  # *ST实达
    "002512": "0.727, -0.427",  # ST达华
    "002055": "0.609, -0.365",  # ST得润
}


# ============================== 二。不常维护字典  ===============================



# ---------------------- 1： 分红股，字典合集 ----------------------

# ----------------- 1.1： 分红股日期字典 -----------------
dividend_stock_date_dict = {

    # 多策略
    "600681": ["25年报 26/04/29", "大会 26/05/19", "0.9+0.6"],  # 百川能源
    "605368": ["25年报 26/04/29", "大会 无效 26/05/13", "4+0"],  # 蓝天燃气
    "600755": ["25年报 26/04/23", "意向1.2 26/09/30", "1.0+1.2"],  # 厦门国贸

    # here
    "000001": ["25年报 26/03/21", "大会 26/05/22", "3.6"],    # 平安银行
    "600985": ["25年报 26/03/28", "大会 26/04/29", "2.55"],    # 淮北矿业
    "601916": ["25年报 26/03/31", "大会 26/06/18", "1.31"],    # 浙商银行

    "600016": ["25年报 26/03/31", "大会 待定 ", "1.36+0.53"],    # 民生银行
    "600219": ["25年报 26/03/27", "除息 26/05/20", "0.4+2.584+1.36"],    # 南山铝业

    "600256": ["25年报 26/04/24", "大会 26/05/20", "0.63"],    # 广汇能源

    "002267": ["25年报 26/04/28", "大会 26/05/22", "2.0"],    # 陕天然气
    "601169": ["25年报 26/04/28", "预案 26/05/21", "2.78"],    # 北京银行
    "002807": ["25年报 26/04/29", "除息 26/05/29", "1.0+1.2"],    # 江阴银行
    "603801": ["25年报 26/04/30", "预案 26/05/22", "4.0"],    # 志邦家居
    "601006": ["25年报 26/04/30", "预案 26/05/21", "1.4+0.8"],    # 大秦铁路

    # 涨幅太大
    "600188": ["25年报 26/03/28", "大会 待定", "1.8+3.2"],  # 兖矿能源

}

# ---------------------- 2： 涨停回调，字典合集 ----------------------

# ---------------------- 2.1： 涨停回调日期字典 ----------------------
limit_up_callback_dividend_date_dict = {
    # 多策略
    "600681": ["25年报 26/04/29", "大会 26/05/19", "0.9+0.6"],  # 百川能源
    "605368": ["25年报 26/04/29", "大会 无效 26/05/13", "4+0"],  # 蓝天燃气
    "600755": ["25年报 26/04/23", "意向 1.2 26/09/30", "1.0+1.2"],  # 厦门国贸

    "001202": ["25年报 26/04/17", "大会 无效 26/05/08", "0.0"],  # 炬申股份

    # here
    "600858": ["25年报 26/04/24", "意向2 26/09/30", "0.15+0.2"],  # 银座股份

    "600814": ["25年报 26/03/27", "大会 26/05/25", "0.41+0.84"],  # 杭州解百
    "600662": ["25年报 26/04/24", "预案 26/04/24", "1.5"],  # 外服控股

    "605388": ["25年报 26/04/29", "大会 无效 26/05/19", "0.0"],  # 均瑶健康

    # ready：
    # "002154": ["2025年报 2026-04-25", ""],  # 报喜鸟

    # old：
    # "600477": ["2025年报 2026-04-17", ""],  # 杭萧钢构

}



# ---------------------- 3： 小盘猛牛，字典合集 ----------------------

# ---------------------- 3.1. 小盘猛牛年报日期字典 ----------------------
small_cap_dividend_date__dict = {
    "300891": ["25年报 26/04/21", "预案 26/04/21", "0.0"], # 惠云钛业
}


# ---------------------- 4： 热点发展，字典合集 ----------------------

# ---------------------- 4.1. 热点发展年报日期字典 ----------------------
hot_development_dividend_data_dict = {
    "002570": ["25年报 26/04/28", "预案 26/04/28", "0.0"],  # 贝因美
}


# ---------------------- 5： 配债股，字典合集 ----------------------

# ---------------------- 5.1. 配债股年报日期字典 ----------------------
bond_allot_dividend_data_dict = {
    "603759": ["25年报 26/04/30", "预案 26/04/30", "1.15"],  # 海天股份
    "001202": ["25年报 26/04/17", "预案 26/04/17", "0.0"],  # 炬申股份
}



# ---------------------- 6： 分红基，字典合集 ----------------------

# ----------------- 6.1： 分红基日期字典 ------------------
fund_dividend_date_dict = {

    # 每月
    "510720": ["登记 26/04/13", "预计 26/05/13", "0.03*12" ],  # 红利国企，模仿上次填
    "513820": ["登记 26/04/24", "预计 26/05/24", "0.01*12" ],  # 港股通红利，模仿上次填

    #每季 （分红3-4次）
    "180102": ["登记 25/05/30", "预计 26/05/30", "0.36*2"],     # 合肥高新
    "515300": ["登记  25/06/16", "预计  26/06/16", "0.228*4" ],  # 300红利 ，模仿上次填
    "159307": ["登记 25/06/19 ", "预计 26/06/19", "0.13*4" ],  # 红利100博时，模仿上次填

    # 每半年
    "515450": ["登记 25/07/14", "预计 26/07/14", "0.3*2" ],  # 红利50南方，模仿上次填
    # 每年
    "510880": ["登记 26/01/20", "预计 27/01/20", "1.43" ],  # 红利ETF华泰柏瑞，模仿上次填
}

# ---------------------- 7： 业绩反转，字典合集 ----------------------

# ----------------- 7.1：业绩反转,申请摘帽日期字典 -----------------
performance_reversal_delisting_application_dict = {
    "600358": "摘帽申请  26/03/21",  # 国旅联合
    "000929": "摘帽申请  26/04/13",  # *ST兰黄
    "002496": "摘帽申请  26/04/18",  # *ST辉丰
    "002762": "摘帽申请  26/04/16",  # *ST金比
    "000595": "25年报 26/04/18",  # *ST宝实
    "300211": "25年报 26/04/24",  # *ST亿通
    "600777": "摘帽申请  26/04/24",  # *ST新潮
    "603789": "摘帽申请 无效 26/04/25",  # *ST星农
    "002713": "25年报 26/04/27",  # *ST东易
    "002305": "25年报 26/04/27",  # *ST南置
    "003032": "25年报 26/04/28",  # *ST传智
    "002693": "25年报 26/04/29",  # *ST双成
    "002076": "摘帽申请 26/04/29",  # *ST星光

    "600892": "25年报 26/04/30",  # *ST大晟

    "002124": "预重整日期 26/11/09",  # 天邦食品  ok
    "300311": "26/07/18",  # ST任子行
    "000903": "摘帽申请 无效 26/08/08",  # ST云动
    "300527": "摘帽申请 26/09/16",  # ST应急
    "300366": "摘帽申请 26/10/24",  # ST创意
    "603595": "摘帽申请 26/11/13",  # ST东尼
    "002122": "摘帽申请 26/11/13",  # ST汇洲
    "000698": "摘帽申请 26/11/29",  # ST沈化
    "002689": "摘帽申请 26/12/20",  # ST远智
    "600624": "摘帽申请 26/12/26",  # ST复华
    "600169": "摘帽申请 26/12/29",  # ST太重
    "300460": "摘帽申请 27/01/12",  # ST惠伦
    "000821": "摘帽申请 27/01/16",  #  ST京机
    "300173": "摘帽申请 27/02/06",  # ST福能

    "600476": "摘帽日期 待定",  # *ST湘邮
    "000488": "摘帽日期 待定",  # ST晨鸣  //27年大概率摘帽
    "002055": "摘帽日期 待定",  # ST得润
    "002630": "摘帽日期 待定",  # *ST华西
    "002512": "摘帽日期 待定",  # ST达华
    "600581": "摘帽日期 待定",  # *ST八钢
    "600735": "重整日期 待定",  # ST新华锦

    "600537": "预重整日期 待定",  # *ST亿晶
    "002321": "正常股",  # 华英农业
    "600889": "摘帽日期 二七年报",  # *ST京化

}

# ----------------- 7.2: 业绩反转,周线 字典 -----------------
performance_reversal_week_line_dict = {
    "000010": "    否",  # 美丽
    "000488": "    周线涨",  # 晨鸣
    "000595": "    半周线",  # 宝实
    "000639": "    否",  # ST西王
    "000698": "    否",  # 沈华
    "000821": "    半周线",  # 京机
    "000826": "    否",  # 同德
    "000903": "    否",  # 云动
    "000929": "    否",  # 兰黄
    "002055": "    否",  # 得润
    "002076": "    否",  # 星光
    "002122": "    否",  # 汇洲
    "002124": "    半周线",  # 天邦食品
    "002305": "    否",  # 南置
    "002360": "    否",  # 同德
    "002424": "    否",  # 百灵
    "002496": "    否",  # 辉丰
    "002512": "    半周线",  # 达华
    "002630": "    周线涨",  # 华西         //买入
    "002689": "    周线涨",  # 远智
    "002691": "    否",  # 冀凯
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
    "301030": "    否",  # 仕净

    "600053": "    否",  # 九鼎
    "600169": "    否",  # 太重
    "600358": "    否",  # 联合
    "600476": "    否",  # 湘邮
    "600581": "    否",  # 八钢
    "600624": "    否",  # 复华
    "600370": "    否",  # 三房
    "600734": "    否",  # 实达
    "600735": "    否",  # 新华锦
    "600759": "    否",  # 洲际油气
    "600777": "    否",  # 新潮
    "600892": "    否",  # 大晟
    "603595": "    周线涨",  # 东尼
    "603789": "    否",  # 星农

    "600537": "    否",  # *ST亿晶
    "002321": "    否",  # 华英农业
    "600889": "    否", # *ST京化
    "688201": "    否",  # ST信安
}

# ===================== 7.3：业绩反转,审计列字典 =====================
performance_reversal_audit_dict = {
    "000595": "    财务亏损 + 营收准ok",  # 宝实
    "000698": "    财务造假 + 已ok",  # 沈华
    "000821": "    财务造假 + 已ok",  # 京机
    "000903": "    财务造假 + 未明",  # 云动
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
    "600358": "    财务造假 + 已ok + 正在重整",  # 联合
    "600476": "    财务亏损 + 未明",  # 湘邮

    "600537": "    正在重整 + 等待路条",  # 亿晶光电
    "600581": "    财务亏损&净资产为负 + 未明",  # 八钢
    "600624": "    财务造假 + 已ok",  # 复华
    "600636": "    财务亏损 + 未明或雷",  # 国化
    "600735": "    挪用4亿&正在重整 + 未明",  # 新华锦
    "600759": "    已摘帽 + 已ok",  # 洲际油气
    "600777": "    审计非标 + 未明",  # 新潮
    "600892": "    财务亏损 + 未明",  # 大晟
    "603595": "    财务造假 + 已ok",  # 东尼
    "603789": "    财务造假&财务亏损 + 准ok",  # 星农

    "002321": "    正常股 ",  # 华英农业
    "600889": "    财务亏损 + 准ok",  # *ST京化

}

# ---------------------- 7.4：业绩反转,要点字典 ----------------------
performance_reversal_memo_dict = {
    "000595": "    轴承风电光伏及储能电站 + 财务亏损 + 或将摘帽",  # 宝实
    "000698": "    烧碱&央企 + 财务造假 + 或将摘帽",  # 沈华
    "000821": "    钙钛矿光伏设备龙头 + 财务造假 + 或将摘帽",  # 京机
    "000903": "    小缸径柴油机&无人机 + 财务造假&强调事项 + 未明",  # 云动
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

    "600476": "    邮政软件 + 净资产为负&信披违规&审计非标 + 暂无重组摘帽未明 + 负债202",  # *ST湘邮
    "600537": "    光伏电池&组件研发 + 净资产为负 + 正在重组 + 负债104",  # *亿晶
    "600581": "    钢铁&煤矿 + 或央企注资产&债务豁免 + 财务亏损&净资产为负 + 或将27年摘帽 + 负债106",  # 八钢
    "600624": "    中成药&软件 + 财务造假 + 或将摘帽",  # 复华
    "600636": "    教育录播 + 财务亏损 + 或将摘帽",  # 国化
    "600735": "    石墨转型&发制品&外贸打底 + 挪用4亿 + 正在重整 + 摘帽不明",  # 新华锦
    "600759": "    哈萨克斯坦油田 + 伊拉克油田 + 批发市场 + 已摘帽",  # 洲际油气
    "600777": "    美国油气 + 审计非标 + 或将摘帽",  # 新潮
    "600892": "    游戏文旅国企老爹 + 财务亏损 + 或将摘帽 + 负债96",  # 大晟
    "603595": "    半导体 + 无重整 + 财务造假 + 或将摘帽",  # 东尼
    "603789": "    农机汽配 + 已完成重整 + 财务亏损 + 或只摘星",  # 星农

    "002321": "    鸭&羽绒 + 国资变大股东 + 未戴帽 ",  # 华英农业
    "600889": "    重组已注资机器人丝杆业务 + 财务亏损 + 或可摘帽",  # *ST京化

}



# ============================== 三。策略名称总字典  ===============================


# ---------------------- A1： 单个策略字典 ----------------------

strategy_dict = {
    "000001": "分红股", "605368": "分红股", "600985": "分红股", "600219": "分红股",
    "601916": "分红股", "601169": "分红股", "002807": "分红股", "160723": "套利基",
    "600188": "分红股", "600016": "分红股", "600681": "分红股", "159329": "海外基",
    "600256": "分红股", "603801": "分红股", "002267": "分红股", "000537": "热点发展",
    "180102": "分红基", "515300": "分红基", "159307": "分红基", "160324": "套利基",
    "510880": "分红基", "510720": "分红基", "508056": "分红基",  "501300": "套利基",
    "515450": "分红基", "513820": "分红基", "002154": "涨停回调", "601669": "涨停回调",
    "501018": "套利基", "002496": "业绩反转", "127033": "可转债", "300311": "业绩反转",
    "161129": "套利基", "512290": "超跌基", "600759": "业绩反转",  "002512": "业绩反转",
    "511880": "空策略", "002385": "热点发展", "512010": "超跌基", "605162": "小盘猛牛",
    "002570": "热点发展", "515710": "超跌基", "300891": "小盘猛牛",  "600169": "业绩反转",
    "002630": "业绩反转", "000516": "热点发展", "111024": "可转债",  "110081": "可转债",
    "002122": "业绩反转", "600516": "涨停回调", "003032": "业绩反转",
    "404003": "可转债", "600735": "业绩反转", "300044": "业绩反转", "002076": "业绩反转",
    "520870": "海外基", "404002": "", "161226": "套利基", "600858": "涨停回调",
    "161128": "套利基", "127015": "可转债", "160216": "套利基", "600339": "业绩反转",
    "161032": "超跌基", "164701": "套利基", "161116": "套利基", "000698": "业绩反转",
    "161124": "套利基", "113701": "可转债", "600662": "涨停回调",
    "603132": "涨停回调", "603759": "配债股", "600814": "涨停回调", "603500": "配债股",
    "160719": "套利基", "600777": "业绩反转", "501001": "套利基", "600738": "热点发展",
    "161031": "套利基", "165525": "套利基", "160416": "套利基", "600755": "分红股",
    "300506": "业绩反转", "601006": "分红股", "164824": "海外基", "002689": "业绩反转",
    "128124": "可转债", "002762": "业绩反转", "501225": "套利基", "127025": "可转债",
    "600477": "涨停回调", "300343": "业绩反转", "002424": "业绩反转", "002055": "业绩反转",
    "600636": "业绩反转", "002788": "涨停回调", "002877": "涨停回调", "002632": "涨停回调",
    "000595": "业绩反转", "002693": "业绩反转", "300211": "业绩反转", "161126": "海外基",
    "162719": "套利基", "162411": "套利基", "001202": "配债股", "600853": "配债股",
    "605388": "涨停回调", "113575": "可转债",

    "000903": "业绩反转", "300527": "业绩反转", "603595": "业绩反转", "300052": "业绩反转",
    "002713": "业绩反转", "002305": "业绩反转", "300366": "业绩反转", "300460": "业绩反转",
    "002124": "业绩反转", "600624": "业绩反转", "000488": "业绩反转", "000929": "业绩反转",
    "000821": "业绩反转", "300020": "业绩反转", "600537": "业绩反转", "600892": "业绩反转",
    "603789": "业绩反转", "300173": "业绩反转",  "600581": "业绩反转", "000639": "业绩反转",
    "600358": "业绩反转", "002321": "业绩反转", "600889": "业绩反转", "000016": "业绩反转",
    "000826": "业绩反转", "301030": "业绩反转", "688201": "业绩反转", "000010": "业绩反转",
    "600053": "业绩反转", "603959": "业绩反转", "002726": "业绩反转", "600476": "业绩反转",
    "600370": "业绩反转", "002691": "业绩反转", "002360": "业绩反转", "600734": "业绩反转",

}

# ---------------------- A2： 多策略字典 ----------------------
multi_strategy_codes = {
    "600681": ["分红股", "涨停回调"],  # 百川能源
    "600755": ["分红股", "涨停回调"],  # 厦门国贸
    "605368": ["分红股", "涨停回调"],  # 蓝天燃气
    "001202": ["配债股", "涨停回调"],  # 炬申股份
    "002267": ["分红股", "涨停回调"],  # 陕天然气

    #测试数据
    # "601006": ["分红股", "小盘猛牛"],  # 大秦铁路   //测试数据
    # "603801": ["分红股", "热点发展"],  # 志邦家居   //测试数据
}



# ============================== 四。暂不归类字典  ===============================





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

def get_stock_dividend_sort_key(item):  # 分红股， ["25年报 26/03/21", "预案 25/03/21", "3.6"]
    code = item[0]    #item--所有股票的列，item[0]--股票代码
    # 取分红日期字典中的预案日期（第二个元素）作为排序依据
    dividend_info = dividend_stock_date_dict.get(code, ["", "", ""])  #根据股票代码，取得字典dividend_stock_date_dict里的数据
    # 分红日期（预案日期）是第二个元素，优先用这个排序
    dividend_date_str = dividend_info[1] if len(dividend_info) >= 2 else ""

    # 解析分红日期
    def parse_dividend_date(date_str):   # 内部子函数
        # if not date_str or date_str.strip() == "待定" or "预案" not in date_str:
        if not date_str or "待定"  in date_str or "无效"  in date_str:
            return datetime(2099, 12, 31)
        # 匹配 "预案 25/03/21" 或 "预案 2025-04-23" 格式
        # 先匹配两位数年份的格式
        date_match = re.search(r'(\d{2})/(\d{2})/(\d{2})', date_str)
        if date_match:
            yy, month, day = date_match.groups()  # 这里顺序必须是：年、月、日
            return datetime(2000 + int(yy), int(month), int(day))
        # 再匹配四位数年份的格式
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if date_match:
            year, month, day = date_match.groups()
            return datetime(int(year), int(month), int(day))
        return datetime(2099, 12, 31)

    dividend_date = parse_dividend_date(dividend_date_str)
    # 次要排序：年报日期（第一个元素）
    report_date_str = dividend_info[0] if len(dividend_info) >= 1 else ""
    report_date = extract_date_from_str(report_date_str)

    # 优先按分红日期升序，再按年报日期升序
    return (dividend_date, report_date)

# ==================== 涨停回调 - 按分红日期升序排序 ====================
def get_limit_up_callback_sort_key(item):   # 涨停回调
    code = item[0]  # 股票代码

    # 从 涨停回调的分红日期字典 中取数据
    dividend_info = limit_up_callback_dividend_date_dict.get(code, ["", ""])

    # 排序用：分红日期（第二个字段）
    dividend_date_str = dividend_info[1] if len(dividend_info) >= 2 else ""

    # 日期解析函数（和你原来风格完全一致）
    def parse_date(date_str):
        if not date_str or date_str.strip() == "待定":
            return datetime(2099, 12, 31)

        # 匹配 日/月/年 26/03/21
        date_match = re.search(r'(\d{2})/(\d{2})/(\d{2})', date_str)
        if date_match:
            day, month, yy = date_match.groups()
            return datetime(2000 + int(yy), int(month), int(day))

        # 匹配 年-月-日 2025-03-26
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if date_match:
            return datetime(*map(int, date_match.groups()))

        return datetime(2099, 12, 31)

    dividend_date = parse_date(dividend_date_str)

    # 次要排序：年报日期（第一个字段）
    report_date_str = dividend_info[0] if len(dividend_info) >= 1 else ""
    report_date = parse_date(report_date_str)

    # 先按分红日期升序，再按年报日期升序
    return (dividend_date, report_date)

# ==================== 小盘猛牛 - 按分红日期升序排序 ====================
def get_small_cap_sort_key(item):
    code = item[0]  # 股票代码

    # 从小盘猛牛分红日期字典 中取数据
    dividend_info = small_cap_dividend_date__dict.get(code, ["", "", ""])

    # 排序用：分红日期（第二个字段）
    dividend_date_str = dividend_info[1] if len(dividend_info) >= 2 else ""

    # 日期解析函数
    def parse_date(date_str):
        if not date_str or date_str.strip() == "待定":
            return datetime(2099, 12, 31)

        # 匹配 日/月/年 26/03/21
        date_match = re.search(r'(\d{2})/(\d{2})/(\d{2})', date_str)
        if date_match:
            day, month, yy = date_match.groups()
            return datetime(2000 + int(yy), int(month), int(day))

        # 匹配 年-月-日 2025-03-26
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if date_match:
            return datetime(*map(int, date_match.groups()))

        return datetime(2099, 12, 31)

    dividend_date = parse_date(dividend_date_str)

    # 次要排序：年报日期
    report_date_str = dividend_info[0] if len(dividend_info) >= 1 else ""
    report_date = parse_date(report_date_str)

    # 先按分红日期升序，再按年报日期升序
    return (dividend_date, report_date)

def get_hot_development_sort_key(item):  # 热点发展
    code = item[0]  # 股票代码

    # 从热点发展分红字典取数据
    dividend_info = hot_development_dividend_data_dict.get(code, ["", "", ""])

    # 排序用：分红日期（第二个字段）
    dividend_date_str = dividend_info[1] if len(dividend_info) >= 2 else ""

    # 日期解析函数（和你项目完全统一）
    def parse_date(date_str):
        if not date_str or date_str.strip() == "待定":
            return datetime(2099, 12, 31)

        # 匹配 日/月/年 26/03/21
        date_match = re.search(r'(\d{2})/(\d{2})/(\d{2})', date_str)
        if date_match:
            day, month, yy = date_match.groups()
            return datetime(2000 + int(yy), int(month), int(day))

        # 匹配 年-月-日 2025-03-26
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if date_match:
            return datetime(*map(int, date_match.groups()))

        return datetime(2099, 12, 31)

    dividend_date = parse_date(dividend_date_str)

    # 次要排序：年报日期
    report_date_str = dividend_info[0] if len(dividend_info) >= 1 else ""
    report_date = parse_date(report_date_str)

    # 先按分红日期升序，再按年报日期升序
    return (dividend_date, report_date)

# ==================== 配债股 - 按分红日期升序排序 ====================
def get_bond_allot_sort_key(item):
    code = item[0]  # 股票代码

    # 从配债股分红字典取数据
    dividend_info = bond_allot_dividend_data_dict.get(code, ["", "", ""])

    # 排序用：分红日期（第二个字段）
    dividend_date_str = dividend_info[1] if len(dividend_info) >= 2 else ""

    # 日期解析函数（和你项目完全统一）
    def parse_date(date_str):
        if not date_str or date_str.strip() == "待定":
            return datetime(2099, 12, 31)

        # 匹配 日/月/年 26/03/21
        date_match = re.search(r'(\d{2})/(\d{2})/(\d{2})', date_str)
        if date_match:
            day, month, yy = date_match.groups()
            return datetime(2000 + int(yy), int(month), int(day))

        # 匹配 年-月-日 2025-03-26
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if date_match:
            return datetime(*map(int, date_match.groups()))

        return datetime(2099, 12, 31)

    dividend_date = parse_date(dividend_date_str)

    # 次要排序：年报日期
    report_date_str = dividend_info[0] if len(dividend_info) >= 1 else ""
    report_date = parse_date(report_date_str)

    # 先按分红日期升序，再按年报日期升序
    return (dividend_date, report_date)

def get_fund_dividend_sort_key(item):   # 分红基， ["登记 26/04/13", "预计 26/05/13", "0.03*12" ]
    code = item[0]
    # 修正：fund_dividend_date_dict [登记日期, 预计日期, 分红金额]，共3个元素
    # 按实际字段含义解包（根据业务逻辑选择“登记日期”作为next_date_str，“预计日期”作为last_date_str）
    fund_info = fund_dividend_date_dict.get(code, ["待定", "待定", "0"])
    next_date_str, last_date_str, _ = fund_info  # 忽略第三个元素（分红金额）

    # 解析下期新分红日期（核心排序依据）
    def parse_dividend_date(date_str): # 内部子函数
        if not date_str or date_str.strip() == "待定":
            # 待定映射为2099年（极晚日期，排在最后）
            return datetime(2099, 12, 31)
        # 匹配 "登记 26/01/20" 或 "预计 26/06/19" 格式
        date_match = re.search(r'(\d{2})/(\d{2})/(\d{2})', date_str)
        if date_match:
            # 提取 日/月/年（两位年），转换为完整日期
            day, month, two_digit_year = date_match.groups()
            year = 2000 + int(two_digit_year)  # 26 → 2026
            return datetime(year, int(month), int(day))
        # 其他无法解析的日期也排在最后
        return datetime(2099, 12, 31)

    next_date = parse_dividend_date(next_date_str)
    # 次要排序依据：去年对应分红日期（可选，保持原逻辑）
    last_date = parse_dividend_date(last_date_str)

    # 排序键：先按下期新分红日期升序，再按去年日期升序
    return (next_date, last_date)


def get_performance_reversal_sort_key(item):  # 业绩反转，按摘帽申请日期升序
    code = item[0]

    # 获取摘帽申请日期（和分红股完全一样的逻辑）
    reversal_date_str = performance_reversal_delisting_application_dict.get(code, "")

    # 解析日期函数 → 完全参考分红股
    def parse_reversal_date(date_str):
        # 空 / 待定 / 无效 → 排最后
        if not date_str or "待定" in date_str or "无效" in date_str or "正常股" in date_str:
            return datetime(2099, 12, 31)

        # 匹配 26/03/21 这种日期
        date_match = re.search(r'(\d{2})/(\d{2})/(\d{2})', date_str)
        if date_match:
            yy, month, day = date_match.groups()
            return datetime(2000 + int(yy), int(month), int(day))

        # 匹配 2026-03-21 这种日期
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if date_match:
            year, month, day = date_match.groups()
            return datetime(int(year), int(month), int(day))

        # 无法解析 → 排最后
        return datetime(2099, 12, 31)

    # 解析出来的最终日期
    reversal_date = parse_reversal_date(reversal_date_str)

    # 按摘帽申请日期升序排序
    return reversal_date

# ---------------------- 13. 合并股票策略排序函数 ----nouse------------------
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
    elif strategy == "配债股":
        date_key = get_bond_allot_sort_key(item)
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
    pattern.pattern_fore_colour = 34   # 34 = 黄色
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

    # 红色字体样式（年化≤1.5用）
    red_style = xlwt.XFStyle()
    red_font = xlwt.Font()
    red_font.height = 9 * 20
    red_font.colour_index = 10  # 纯红色
    red_style.font = red_font
    red_style.alignment = align_date
    styles["red_text"] = red_style


    # 黄底 + 红色
    yellow_red_style = xlwt.XFStyle()
    yellow_red_style.font = red_font
    yellow_red_style.alignment = align_date
    yellow_red_style.pattern = pattern
    styles["yellow_red_text"] = yellow_red_style


    return styles


# ---------------------- 15. Sheet写入函数（远涨远跌移到摘帽后、要点前） ----------------------
def write_sheet_data(sheet, data_list, styles, row_height=11 * 20, is_strategy_sheet=False,
                     summary_data=None, summary_percent=None, total_capital=500000, is_stock_dividend_sheet=False,
                     is_fund_dividend_sheet=False, is_small_cap_sheet=False, is_hot_development_sheet=False,
                     is_performance_reversal_sheet=False, is_limit_up_callback_sheet=False,
                     is_combined_stock_sheet=False, is_bond_allot_sheet=False,is_overdown_sheet=False,
                     is_oversea_sheet=False,is_swapbond_sheet=False):
    col_widths = {
        0: 8, 1: 10, 2: 8, 3: 8, 4: 10, 5: 9, 6: 6, 7: 10,
        8: 10, 9: 8, 10: 13, 11: 12, 12: 12, 13: 8, 14: 25, 15: 25
    }  # K是10
    col_widths2 = {
        0: 8, 1: 10, 2: 8, 3: 8, 4: 10, 5: 9, 6: 6, 7: 10,
        8: 10, 9: 8, 10: 13, 11: 12, 12: 12, 13: 8, 14: 8, 15: 8
    }  # K是10

    # 应用列宽（5个特殊表用col_widths2，其他用col_widths）
    special_sheets = ["分红股", "分红基", "涨停回调", "配债股", "小盘猛牛", "热点发展"]
    current_sheet_name = sheet.name.strip()

    if current_sheet_name in special_sheets:
        # 重点表格：使用 col_widths2
        for col, width in col_widths2.items():
            sheet.col(col).width = width * 256
    else:
        # 其他表格：保持默认 col_widths
        for col, width in col_widths.items():
            sheet.col(col).width = width * 256

    # 表头
    if is_stock_dividend_sheet:  # 分红股
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报日期", "分红日期", "每十股分红", "年化收益",
                   "远涨", "远跌"]
    elif is_small_cap_sheet or is_hot_development_sheet or is_limit_up_callback_sheet or is_bond_allot_sheet:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报日期", "分红日期", "每十股分红", "年化收益",
                   "远涨", "远跌"]
    elif is_fund_dividend_sheet:  # 分红基金
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "去年对应分红日期", "下期新分红日期", "每十股分红", "年化收益",
                   "远涨", "远跌"]
    elif is_overdown_sheet:  # 超跌基金
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "远涨", "远跌"]
    elif is_oversea_sheet:  # 超跌基金
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "远涨", "远跌"]
    elif is_swapbond_sheet:  # 可转债
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "远涨", "远跌"]

    elif is_performance_reversal_sheet: #业绩反转
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "摘帽申请日期", "周线", "远涨", "远跌", "审计", "要点"]
    elif is_combined_stock_sheet: # 股票合并
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "下期新年报/分红日期", "去年对应年报/分红日期"]
    else:
        headers = ["证券代码", "证券名称", "数量", "当前价", "金额", "仓位百分比", "排名", "累积总金额",
                   "总累积仓位%", "策略", "远涨", "远跌"]

    sheet.row(0).height = row_height
    for col_idx, header in enumerate(headers):
        sheet.write(0, col_idx, header, styles["header"])

    if is_strategy_sheet and data_list:
        if is_combined_stock_sheet:  # 股票策略合并
            sorted_strategy_data = sorted(data_list, key=get_combined_stock_sort_key)
        elif is_fund_dividend_sheet:  # 分红基
            sorted_strategy_data = sorted(data_list, key=get_fund_dividend_sort_key)
        elif is_stock_dividend_sheet:  # 分红股
            sorted_strategy_data = sorted(data_list, key=get_stock_dividend_sort_key)  #没有传入item参数，是因为会自动调用每一个股票item
        elif is_small_cap_sheet:  # 小盘猛牛
            sorted_strategy_data = sorted(data_list, key=get_small_cap_sort_key)
        elif is_hot_development_sheet:  # 热点发展
            sorted_strategy_data = sorted(data_list, key=get_hot_development_sort_key)
        elif is_performance_reversal_sheet:  # 业绩反转
            sorted_strategy_data = sorted(data_list, key=get_performance_reversal_sort_key)
        elif is_limit_up_callback_sheet:  #涨停回调
            sorted_strategy_data = sorted(data_list, key=get_limit_up_callback_sort_key)
        elif  is_bond_allot_sheet:  # 配债股
            sorted_strategy_data = sorted(data_list, key=get_bond_allot_sort_key)
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

            if is_stock_dividend_sheet:  # 分红股
                item_list = dividend_stock_date_dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, next_report, styles["yellow"])
                sheet.write(row_idx, 11, div_date, styles["yellow"])
                sheet.write(row_idx, 12, per_div, styles["yellow_date_right"])

                # 年化收益
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])
                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                # sheet.write(row_idx, 13, annual_rate_text, styles["yellow_date_right"])

                # 年化收益颜色：≥4.5 粉红；≤1.5 红色
                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_date_right"])

                # ===================== 新增：远涨 远跌 =====================
                structure_str = stock_dividend_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if structure_str:
                    parts = structure_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["yellow"])

                # # ==================== 分红股 - 远涨 列颜色 ====================
                # far_up_val = 0
                # try:
                #     # 从字典取远涨数值
                #     far_up_val = int(stock_dividend_struct_dict[code].split(',')[0].strip())
                # except:
                #     far_up_val = 999
                #
                # # 黄色背景行
                # if far_up_val < 50:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_pink_delisting_apply"])
                # elif far_up_val > 70:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_red_text"])
                # else:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                #
                # # sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])  # 远跌
                #
                # # 远跌 颜色：>60粉红，<30红色
                # far_down_val = 0
                # try:
                #     far_down_val = int(stock_dividend_struct_dict[code].split(',')[1].strip())
                # except:
                #     far_down_val = 0
                #
                # if far_down_val > 60:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_pink_delisting_apply"])
                # elif far_down_val < 30:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_red_text"])
                # else:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])

            elif is_limit_up_callback_sheet:  # 涨停回调
                # 取出字典 3 个值：年报日期、分红日期、每十股分红
                item_list = limit_up_callback_dividend_date_dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, item_list[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, item_list[1], styles["yellow_date_right"])
                sheet.write(row_idx, 12, item_list[2], styles["yellow_date_right"])

                # ===================== 年化收益 =====================
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_date_right"])

                # ===================== 远涨 / 远跌（黄色背景 + 完整 try except） =====================
                struct_str = limit_up_callback_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["yellow"])


                # # -------------------- 远涨 颜色（完整 try/except） --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                #
                # # -------------------- 远跌 颜色（完整 try/except） --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])

            elif is_small_cap_sheet:  # 小盘猛牛  黄色
                # 取出字典 3 个值：年报日期、分红日期、每十股分红
                item_list = small_cap_dividend_date__dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, item_list[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, item_list[1], styles["yellow_date_right"])
                sheet.write(row_idx, 12, item_list[2], styles["yellow_date_right"])

                # ===================== 年化收益 =====================
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_date_right"])

                # ===================== 远涨 / 远跌 =====================
                struct_str = small_cap_callback_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["yellow"])

                # # -------------------- 远涨 颜色规则 --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                #
                # # -------------------- 远跌 颜色规则 --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])

            elif is_hot_development_sheet:  # 热点发展
                # 取出字典 3 个值：年报日期、分红日期、每十股分红
                item_list = hot_development_dividend_data_dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, item_list[0], styles["yellow_date_right"])
                sheet.write(row_idx, 11, item_list[1], styles["yellow_date_right"])
                sheet.write(row_idx, 12, item_list[2], styles["yellow_date_right"])

                # ===================== 年化收益 =====================
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_date_right"])

                # ===================== 远涨 / 远跌 =====================
                struct_str = hot_development_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()


                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["yellow"])

                # # -------------------- 远涨 颜色规则 --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                #
                # # -------------------- 远跌 颜色规则 --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])

            elif is_bond_allot_sheet:  # 配债股 黄色背景色
                # 取出字典 3 个值：下期新年报日期、分红日期、每十股分红
                item_list = bond_allot_dividend_data_dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, next_report, styles["yellow_date_right"])
                sheet.write(row_idx, 11, div_date, styles["yellow_date_right"])
                sheet.write(row_idx, 12, per_div, styles["yellow_date_right"])

                # ===================== 年化收益 =====================
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_date_right"])

                # ===================== 远涨 / 远跌 =====================
                struct_str = bond_allot_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["yellow"])

                # # -------------------- 远涨 颜色规则 --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                #
                # # -------------------- 远跌 颜色规则 --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])


            elif is_fund_dividend_sheet:   # 分红基
                item_list = fund_dividend_date_dict.get(code, ["", "", ""])
                last_date = item_list[0]
                next_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, last_date, styles["yellow"])
                sheet.write(row_idx, 11, next_date, styles["yellow"])
                sheet.write(row_idx, 12, per_div, styles["yellow_date_right"])

                # 年化收益（和分红股一样）
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])
                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                # sheet.write(row_idx, 13, annual_rate_text, styles["yellow_date_right"])

                # -------------- 分红基 年化收益颜色 --------------
                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                # 黄色行
                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["yellow_date_right"])

                # ===================== 新增：远涨 远跌 =====================
                struct_str = dividend_fund_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["yellow"])

                # # 分红基 远涨 颜色：<50粉红，>70红色
                # far_up_val = 0
                # try:
                #     far_up_val = int(dividend_fund_struct_dict[code].split(',')[0].strip())
                # except:
                #     far_up_val = 0
                #
                # if far_up_val < 50:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_pink_delisting_apply"])
                # elif far_up_val > 70:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_red_text"])
                # else:
                #     sheet.write(row_idx, 14, far_up, styles["yellow_date_right"])
                #
                # # sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])  # 远跌
                #
                # # 分红基 远跌 颜色：>60粉红，<30红色
                # far_down_val = 0
                # try:
                #     far_down_val = int(dividend_fund_struct_dict[code].split(',')[1].strip())
                # except:
                #     far_down_val = 0
                #
                # if far_down_val > 60:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_pink_delisting_apply"])
                # elif far_down_val < 30:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_red_text"])
                # else:
                #     sheet.write(row_idx, 15, far_down, styles["yellow_date_right"])

            # ---------------------- 超跌基 黄色背景 ----------------------
            elif is_overdown_sheet:
                # 远涨 远跌
                struct_str = overdown_fund_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 10, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 10, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 10, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 10, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 11, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 11, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 11, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 11, far_down, styles["yellow"])


                # # -------------------- 远涨 --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 10, far_up, styles["yellow_pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 10, far_up, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 10, far_up, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 10, far_up, styles["yellow_date_right"])
                #
                # # -------------------- 远跌 --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 11, far_down, styles["yellow_pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 11, far_down, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 11, far_down, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 11, far_down, styles["yellow_date_right"])

            # ---------------------- 海外基 黄色背景 ----------------------
            elif is_oversea_sheet:
                struct_str = oversea_fund_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 10, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 10, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 10, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 10, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 11, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 11, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 11, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 11, far_down, styles["yellow"])

                # # 远涨
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 10, far_up, styles["yellow_pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 10, far_up, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 10, far_up, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 10, far_up, styles["yellow_date_right"])
                #
                # # 远跌
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 11, far_down, styles["yellow_pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 11, far_down, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 11, far_down, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 11, far_down, styles["yellow_date_right"])

            # ---------------------- 可转债 黄色背景 ----------------------
            elif is_swapbond_sheet:
                struct_str = swapbond_fund_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 10, far_up, styles["far_up_yellow_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 10, far_up, styles["far_up_yellow_red"])
                    else:
                        sheet.write(row_idx, 10, far_up, styles["yellow"])
                except:
                    sheet.write(row_idx, 10, far_up, styles["yellow"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 11, far_down, styles["far_down_yellow_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 11, far_down, styles["far_down_yellow_red"])
                    else:
                        sheet.write(row_idx, 11, far_down, styles["yellow"])
                except:
                    sheet.write(row_idx, 11, far_down, styles["yellow"])

                # # 远涨
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 10, far_up, styles["yellow_pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 10, far_up, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 10, far_up, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 10, far_up, styles["yellow_date_right"])
                #
                # # 远跌
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 11, far_down, styles["yellow_pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 11, far_down, styles["yellow_red_text"])
                #     else:
                #         sheet.write(row_idx, 11, far_down, styles["yellow_date_right"])
                # except:
                #     sheet.write(row_idx, 11, far_down, styles["yellow_date_right"])


            elif is_performance_reversal_sheet:  # 业绩反转
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

                # print(far_up)

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                # print(far_up)

                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

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

            # elif is_combined_stock_sheet:  # 股票策略合并
            #     if strategy == "分红股":
            #         dates = dividend_stock_date_dict.get(code, ["", ""])
            #     elif strategy == "业绩反转":
            #         dates = performance_reversal_annual_report_dict.get(code, ["", ""])
            #     elif strategy == "小盘猛牛":
            #         dates = small_cap_dividend_date__dict.get(code, ["", ""])
            #     elif strategy == "热点发展":
            #         dates = hot_development_dividend_data_dict.get(code, ["", ""])
            #     elif strategy == "涨停回调":
            #         dates = limit_up_callback_dividend_date_dict.get(code, ["", ""])
            #     else:
            #         dates = ["", ""]
            #     sheet.write(row_idx, 10, dates[0], styles["yellow_date_right"])
            #     sheet.write(row_idx, 11, dates[1], styles["yellow_date_right"])
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

            if is_stock_dividend_sheet:  # 分红股
                item_list = dividend_stock_date_dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, next_report, styles["base"])
                sheet.write(row_idx, 11, div_date, styles["base"])
                sheet.write(row_idx, 12, per_div, styles["date_right"])

                # 年化收益
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                # sheet.write(row_idx, 13, annual_rate_text, styles["date_right"])

                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                # 普通行
                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["date_right"])

                # ===================== 新增：远涨 远跌 =====================
                structure_str = stock_dividend_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if structure_str:
                    parts = structure_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                # print(far_up)

                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["base"])

                # # sheet.write(row_idx, 14, far_up, styles["date_right"])  # 远涨
                # far_up_val = 0
                # try:
                #     far_up_val = int(stock_dividend_struct_dict[code].split(',')[0].strip())
                # except:
                #     far_up_val = 0
                #
                # if far_up_val < 50:
                #     sheet.write(row_idx, 14, far_up, styles["pink_delisting_apply"])
                # elif far_up_val > 70:
                #     sheet.write(row_idx, 14, far_up, styles["red_text"])
                # else:
                #     sheet.write(row_idx, 14, far_up, styles["date_right"])
                #
                # # sheet.write(row_idx, 15, far_down, styles["date_right"])  # 远跌
                #
                # # 远跌 颜色：>60粉红，<30红色
                # far_down_val = 0
                # try:
                #     far_down_val = int(stock_dividend_struct_dict[code].split(',')[1].strip())
                # except:
                #     far_down_val = 0
                #
                # if far_down_val > 60:
                #     sheet.write(row_idx, 15, far_down, styles["pink_delisting_apply"])
                # elif far_down_val < 30:
                #     sheet.write(row_idx, 15, far_down, styles["red_text"])
                # else:
                #     sheet.write(row_idx, 15, far_down, styles["date_right"])



            elif is_limit_up_callback_sheet:  # 涨停回调  普通背景色
                # 取出字典 3 个值：年报日期、分红日期、每十股分红
                item_list = limit_up_callback_dividend_date_dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, item_list[0], styles["date_right"])
                sheet.write(row_idx, 11, item_list[1], styles["date_right"])
                sheet.write(row_idx, 12, item_list[2], styles["date_right"])

                # ===================== 年化收益 =====================
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["date_right"])

                # ===================== 远涨 / 远跌 =====================
                struct_str = limit_up_callback_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["base"])

                # # -------------------- 远涨 普通背景 + 完整 try/except --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 14, far_up, styles["pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 14, far_up, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 14, far_up, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 14, far_up, styles["date_right"])
                #
                # # -------------------- 远跌 普通背景 + 完整 try/except --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 15, far_down, styles["pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 15, far_down, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 15, far_down, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 15, far_down, styles["date_right"])

            elif is_small_cap_sheet:  # 小盘猛牛 普通背景色
                # 取出字典 3 个值：年报日期、分红日期、每十股分红
                item_list = small_cap_dividend_date__dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, item_list[0], styles["date_right"])
                sheet.write(row_idx, 11, item_list[1], styles["date_right"])
                sheet.write(row_idx, 12, item_list[2], styles["date_right"])

                # ===================== 年化收益 =====================
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["date_right"])

                # ===================== 远涨 / 远跌 =====================
                struct_str = small_cap_callback_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["base"])

                # # -------------------- 远涨 颜色规则 --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 14, far_up, styles["pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 14, far_up, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 14, far_up, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 14, far_up, styles["date_right"])
                #
                # # -------------------- 远跌 颜色规则 --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 15, far_down, styles["pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 15, far_down, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 15, far_down, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 15, far_down, styles["date_right"])

            elif is_hot_development_sheet:  # 热点发展
                # 取出字典 3 个值：年报日期、分红日期、每十股分红
                item_list = hot_development_dividend_data_dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, item_list[0], styles["date_right"])
                sheet.write(row_idx, 11, item_list[1], styles["date_right"])
                sheet.write(row_idx, 12, item_list[2], styles["date_right"])

                # ===================== 年化收益 =====================
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["date_right"])

                # ===================== 远涨 / 远跌 =====================
                struct_str = hot_development_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["base"])

                # # -------------------- 远涨 颜色规则 --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 14, far_up, styles["pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 14, far_up, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 14, far_up, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 14, far_up, styles["date_right"])
                #
                # # -------------------- 远跌 颜色规则 --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 15, far_down, styles["pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 15, far_down, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 15, far_down, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 15, far_down, styles["date_right"])


            elif is_bond_allot_sheet:  # 配债股 普通背景色
                # 取出字典 3 个值：下期新年报日期、分红日期、每十股分红
                item_list = bond_allot_dividend_data_dict.get(code, ["", "", ""])
                next_report = item_list[0]
                div_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, next_report, styles["date_right"])
                sheet.write(row_idx, 11, div_date, styles["date_right"])
                sheet.write(row_idx, 12, per_div, styles["date_right"])

                # ===================== 年化收益 =====================
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["date_right"])

                # ===================== 远涨 / 远跌 =====================
                struct_str = bond_allot_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["base"])

                # # -------------------- 远涨 颜色规则 --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 14, far_up, styles["pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 14, far_up, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 14, far_up, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 14, far_up, styles["date_right"])
                #
                # # -------------------- 远跌 颜色规则 --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 15, far_down, styles["pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 15, far_down, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 15, far_down, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 15, far_down, styles["date_right"])

            elif is_fund_dividend_sheet:  # 分红基
                item_list = fund_dividend_date_dict.get(code, ["", "", ""])
                last_date = item_list[0]
                next_date = item_list[1]
                per_div = item_list[2]

                sheet.write(row_idx, 10, last_date, styles["base"])
                sheet.write(row_idx, 11, next_date, styles["base"])
                sheet.write(row_idx, 12, per_div, styles["date_right"])

                # 年化收益（和分红股一样）
                annual_rate_text = ""
                try:
                    div_str = str(per_div).strip()
                    clean_expr = ''.join([c for c in div_str if c in '0123456789.+-*/'])
                    div_val = float(eval(clean_expr))
                    current_price = float(info["当前价"])

                    if current_price > 0 and div_val >= 0:
                        annual_rate = (div_val / 10) / current_price * 100
                        annual_rate_text = f"{annual_rate:.2f}"
                except:
                    annual_rate_text = ""

                # sheet.write(row_idx, 13, annual_rate_text, styles["date_right"])

                # -------------- 分红基 年化收益颜色 --------------
                annual_val = 0.0
                try:
                    annual_val = float(annual_rate_text)
                except:
                    annual_val = 0.0

                # 普通行
                if annual_val >= 4.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["pink_delisting_apply"])
                elif annual_val <= 1.5:
                    sheet.write(row_idx, 13, annual_rate_text, styles["red_text"])
                else:
                    sheet.write(row_idx, 13, annual_rate_text, styles["date_right"])


                # ===================== 新增：远涨 远跌 =====================
                struct_str = dividend_fund_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                # print(far_up)

                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 14, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 14, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 14, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 14, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 15, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 15, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 15, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 15, far_down, styles["base"])


                # # 分红基 远涨 颜色：<50粉红，>70红色
                # far_up_val = 0
                # try:
                #     far_up_val = int(dividend_fund_struct_dict[code].split(',')[0].strip())
                # except:
                #     far_up_val = 0
                #
                # if far_up_val < 50:
                #     sheet.write(row_idx, 14, far_up, styles["pink_delisting_apply"])
                # elif far_up_val > 70:
                #     sheet.write(row_idx, 14, far_up, styles["red_text"])
                # else:
                #     sheet.write(row_idx, 14, far_up, styles["date_right"])
                #
                # # sheet.write(row_idx, 15, far_down, styles["date_right"])  # 远跌
                #
                # # 分红基 远跌 颜色：>60粉红，<30红色
                # far_down_val = 0
                # try:
                #     far_down_val = int(dividend_fund_struct_dict[code].split(',')[1].strip())
                # except:
                #     far_down_val = 0
                #
                # if far_down_val > 60:
                #     sheet.write(row_idx, 15, far_down, styles["pink_delisting_apply"])
                # elif far_down_val < 30:
                #     sheet.write(row_idx, 15, far_down, styles["red_text"])
                # else:
                #     sheet.write(row_idx, 15, far_down, styles["date_right"])

            # ---------------------- 超跌基 ----------------------
            elif is_overdown_sheet:
                # 远涨 远跌
                struct_str = overdown_fund_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                # print(far_up)

                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 10, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 10, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 10, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 10, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 11, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 11, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 11, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 11, far_down, styles["base"])

                # # -------------------- 远涨 --------------------
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 10, far_up, styles["pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 10, far_up, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 10, far_up, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 10, far_up, styles["date_right"])
                #
                # # -------------------- 远跌 --------------------
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 11, far_down, styles["pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 11, far_down, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 11, far_down, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 11, far_down, styles["date_right"])

            # ---------------------- 海外基 ----------------------
            elif is_oversea_sheet:
                struct_str = oversea_fund_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                # print(far_up)

                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 10, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 10, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 10, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 10, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 11, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 11, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 11, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 11, far_down, styles["base"])

                # # 远涨
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 10, far_up, styles["pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 10, far_up, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 10, far_up, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 10, far_up, styles["date_right"])
                #
                # # 远跌
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 11, far_down, styles["pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 11, far_down, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 11, far_down, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 11, far_down, styles["date_right"])date_right

            # ---------------------- 可转债 ----------------------
            elif is_swapbond_sheet:
                struct_str = swapbond_fund_struct_dict.get(code, "")
                far_up = ""
                far_down = ""
                if struct_str:
                    parts = struct_str.split(",")
                    if len(parts) >= 2:
                        far_up = parts[0].strip()
                        far_down = parts[1].strip()

                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                # print(far_up)

                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

                # 远涨
                try:
                    val = int(far_up)
                    if val <= 50:
                        sheet.write(row_idx, 10, far_up, styles["far_up_pink"])
                    elif val >= 70:
                        sheet.write(row_idx, 10, far_up, styles["far_up_red"])
                    else:
                        sheet.write(row_idx, 10, far_up, styles["base"])
                except:
                    sheet.write(row_idx, 10, far_up, styles["base"])

                # 远跌
                try:
                    val = int(far_down.strip())
                    if val >= 60:
                        sheet.write(row_idx, 11, far_down, styles["far_down_pink"])
                    elif val <= 30:
                        sheet.write(row_idx, 11, far_down, styles["far_down_red"])
                    else:
                        sheet.write(row_idx, 11, far_down, styles["base"])
                except:
                    sheet.write(row_idx, 11, far_down, styles["base"])

                # # 远涨
                # try:
                #     val = float(far_up)
                #     if val < 50:
                #         sheet.write(row_idx, 10, far_up, styles["pink_delisting_apply"])
                #     elif val > 70:
                #         sheet.write(row_idx, 10, far_up, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 10, far_up, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 10, far_up, styles["date_right"])
                #
                # # 远跌
                # try:
                #     val = float(far_down)
                #     if val > 60:
                #         sheet.write(row_idx, 11, far_down, styles["pink_delisting_apply"])
                #     elif val < 30:
                #         sheet.write(row_idx, 11, far_down, styles["red_text"])
                #     else:
                #         sheet.write(row_idx, 11, far_down, styles["date_right"])
                # except:
                #     sheet.write(row_idx, 11, far_down, styles["date_right"])

            elif is_performance_reversal_sheet:  # 业绩反转
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

                # 乘100 并 取整
                try:
                    far_up = str(int(float(far_up) * 100))
                except:
                    far_up = ""
                try:
                    far_down = str(int(abs(float(far_down)) * 100))
                except:
                    far_down = ""

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


            # elif is_combined_stock_sheet:  # 股票策略合并   //nouse
            #     if strategy == "分红股":
            #         dates = dividend_stock_date_dict.get(code, ["", ""])
            #     elif strategy == "业绩反转":
            #         dates = performance_reversal_annual_report_dict.get(code, ["", ""])
            #     elif strategy == "小盘猛牛":
            #         dates = small_cap_dividend_date__dict.get(code, ["", ""])
            #     elif strategy == "热点发展":
            #         dates = hot_development_dividend_data_dict.get(code, ["", ""])
            #     elif strategy == "涨停回调":
            #         dates = limit_up_callback_dividend_date_dict.get(code, ["", ""])
            #     else:
            #         dates = ["", ""]
            #     sheet.write(row_idx, 10, dates[0], styles["date_right"])
            #     sheet.write(row_idx, 11, dates[1], styles["date_right"])
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





# ---------------------- 16. 数据读取与处理 -------应是程序运行start---------------
old_workbook = xlrd.open_workbook("1234.xls")
position_dict = {}

# 依次遍历下面的sheet
for sheet_name in ["01", "02", "03", "04"]:
# for sheet_name in ["01", "02"]:

    sheet = old_workbook.sheet_by_name(sheet_name)  # 当前的sheet neme，如 “01”

    # 依次遍历本sheet中的每一行
    for row_idx in range(1, sheet.nrows):

        code = sheet.cell_value(row_idx, 0)        # “代码” 列
        name = sheet.cell_value(row_idx, 1)        # “名称” 列
        count_val = sheet.cell_value(row_idx, 2)   # “数量” 列
        price_val = sheet.cell_value(row_idx, 3)   # “价格” 列

        if code in ("511880", "404002", "600636"):
            continue

        count = float(count_val) if count_val else 0.0  # 字符串转数字
        price = float(price_val) if price_val else 0.0  # 字符串转数字

        # 下面是把代码前面补0，补足6位数字
        try:
            code_str = str(int(float(code))).strip()
            code = code_str.zfill(6)
        except:
            code = str(code).strip()

        # 把当前行加入到字典position_dict，如果是相同的股票则只增大数量
        if code in position_dict:
            position_dict[code]["总数量"] += count   # 相同股票
        else:
            position_dict[code] = {"名称": name, "总数量": count, "当前价": price}  # 新股票

# print(position_dict)    #--test

total_capital = 500000
for code, info in position_dict.items():
    info["金额"] = int(info["总数量"] * info["当前价"])                   #或字典position_dict新增了“金额”列
    info["仓位百分比"] = round((info["金额"] / total_capital) * 100, 1)  #或字典position_dict新增了"仓位百分比"列


# print(position_dict)   #--test

# ---------------------- 17. 数据分组 ----------------------
strategy_groups = defaultdict(list)  # 新定义一个列表strategy_groups，可直接用append添加键和键值
full_data = []
# 注释/删除：合并股票相关的数据初始化
# combined_stock_data = []
# combined_strategies = ["分红股", "业绩反转", "小盘猛牛", "热点发展", "涨停回调", "配债股"]

# 下面的x是position_dict的每一行数据，x[1]是每一行除键值code之外的数据 (相当于嵌套里的子字典)
sorted_positions = sorted(position_dict.items(), key=lambda x: x[1]["金额"], reverse=True)   # 按金额从大到小排序

# print(sorted_positions)    #--test

cumulative_amount = 0  # 累积金额
rank = 1

# 遍历所有股票排序后的字典 sorted_positions
for code, info in sorted_positions:

    cumulative_amount += info["金额"]                                            # 每一行相加的累积金额
    total_cumulative_pct = round((cumulative_amount / total_capital) * 100, 1)  # 每一行相加后的累积百分比

    # 判断是多策略，还是单策略
    if code in multi_strategy_codes:
        strategies = multi_strategy_codes[code]     # 多策略  //肯定存在，所以不用.get
    else:
        base_strategy = strategy_dict.get(code, "空策略") or "空策略"
        strategies = [base_strategy]
        # print(code)

    main_strategy = strategies[0]   # 该股票的主策略

    # 把这一行的基本数据和汇总数据，添加到full_data列表中(总仓位sheet用)  //总仓位没有"策略"键值，列表即可以
    if(info["当前价"]!=0):
        full_data.append((code, info, main_strategy, rank, cumulative_amount, total_cumulative_pct))

    # 把这一行的基本数据和汇总数据，添加到对应的策略字典中 (个策略sheet用)
    for strategy in strategies:
        strategy_groups[strategy].append((code, info, strategy, rank, cumulative_amount, total_cumulative_pct))

        # 注释/删除：合并股票数据添加逻辑
        # if strategy in combined_strategies:
        #     combined_stock_data.append((code, info, strategy, rank, cumulative_amount, total_cumulative_pct))

    rank += 1  #该股票金额最大排第一名，后面的股票依次名次+1

# print(full_data)          #--test
# print(strategy_groups)    #--test


# ---------------------- 18. 策略汇总 ----------------------

unique_codes = set()
strategy_total_amount = {}

for strategy, items in strategy_groups.items():
    total = 0

    for item in items:

        code = item[0]  # 股票代码

        # 对于多策略的股票， 总金额只在排在前面第一个的策略里计算   //应是总仓位里面的各策略数据
        if code not in unique_codes:
            total += item[1]["金额"]
            unique_codes.add(code)

    strategy_total_amount[strategy] = total  # 持仓策略各占多少金额统计

# print(strategy_total_amount)

# 持仓策略各占多少仓位百分比计算
strategy_total_percent = {
    k: round((v / total_capital) * 100, 1)
    for k, v in strategy_total_amount.items()
}

# print(strategy_total_percent)

strategy_order = [
    "分红股", "业绩反转", "小盘猛牛",  "涨停回调","配债股",  "热点发展",
     "分红基","套利基", "超跌基", "海外基",
    "可转债", "空策略"
]
order_dict = {strategy: idx for idx, strategy in enumerate(strategy_order)}  # 把strategy_order列表和序号123...合成一个字典

# print(order_dict)  # {'分红股': 0, '业绩反转': 1, '小盘猛牛': 2, '涨停回调': 3, ...... , '空策略': 11}

# 用第一个字典order_dict的编号，给第二个字典strategy_total_amount的名称/键值 排序， 生成一个新的列表  sorted_strategy_names
sorted_strategy_names = sorted(
    strategy_total_amount.keys(),
    key=lambda x: order_dict.get(x, len(strategy_order))  # len(strategy_order)  -- 指默认最大值，就是排在最后面的意思
)
# print(sorted_strategy_names)   # ['分红股', '涨停回调']

# summary_data = {n: strategy_total_amount[n] for n in sorted_strategy_names}      # 持仓策略各占多少金额统计 (按顺序后)
# 分解如下：
summary_data = {}
for n in sorted_strategy_names: # 把n（可理解为策略名）当作列表sorted_strategy_name的 key
    summary_data[n] = strategy_total_amount[n]   # 从字典strategy_total_amount里取出对应的值，合成新的字典summary_data

summary_percent = {n: strategy_total_percent[n] for n in sorted_strategy_names}  # 持仓策略各占多少仓位百分比计算  (按顺序后)

# print(summary_data)      # {'分红股': 2469, '涨停回调': 924}   //排序后
# print(summary_percent)   # {'分红股': 0.5, '涨停回调': 0.2}    //排序后

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

for strategy_name in sorted_strategy_names:
    group_data = strategy_groups[strategy_name]
    if not group_data:
        continue

    # safe_name = strategy_name.replace("/", "").replace("\\", "").replace(":", "").replace("*", "").replace("?",
    #                                                                                                        "").replace(
    #     "[", "").replace("]", "")[:31]
    safe_name = strategy_name.replace("/", "").replace("\\", "").replace(":", "").replace("*", "").replace("?", "").replace( "[", "").replace("]", "")[:31]

    if not safe_name:
        safe_name = "空策略"

    strategy_sheet = final_workbook.add_sheet(safe_name)

    is_fund_dividend_sheet = (strategy_name == "分红基")
    is_stock_dividend_sheet = (strategy_name == "分红股")
    is_small_cap_sheet = (strategy_name == "小盘猛牛")
    is_hot_development_sheet = (strategy_name == "热点发展")
    is_performance_reversal_sheet = (strategy_name == "业绩反转")
    is_limit_up_callback_sheet = (strategy_name == "涨停回调")
    is_bond_allot_sheet = (strategy_name == "配债股")
    is_overdown_sheet = (strategy_name == "超跌基")  # <--- 加这一行
    is_oversea_sheet = (strategy_name == "海外基")
    is_swapbond_sheet = (strategy_name == "可转债")

    write_sheet_data(
        strategy_sheet, group_data, styles,
        is_strategy_sheet=True,
        total_capital=total_capital,
        is_stock_dividend_sheet=is_stock_dividend_sheet,
        is_fund_dividend_sheet=is_fund_dividend_sheet,
        is_small_cap_sheet=is_small_cap_sheet,
        is_hot_development_sheet=is_hot_development_sheet,
        is_performance_reversal_sheet=is_performance_reversal_sheet,
        is_limit_up_callback_sheet=is_limit_up_callback_sheet,
        is_bond_allot_sheet=is_bond_allot_sheet,
        is_overdown_sheet=is_overdown_sheet,
        is_oversea_sheet=is_oversea_sheet,
        is_swapbond_sheet=is_swapbond_sheet

    )

final_workbook.save("__00_总仓位.xls")

print("✅ 生成完成！")