# 【Python爬虫案例】如何用Python爬取股市数据，并进行数据可视化
# b站网址：https://www.bilibili.com/video/BV1Gf4y197s2/?spm_id_from=333.1387.favlist.content.click&vd_source=1aabf6d13273d470d124a884db6b11d0

# 网页爬虫抓取东方财富网数据的步骤
#  1. 打开数据网址 https://data.eastmoney.com/zjlx/detail.html
#  2. import requests三方组件
#  3. response = requests.get(AAA)
#     取得AAA的方法 (演示)： 谷歌浏览器 -- 打开数据网址  -- 网页窗口点右键  -- 点检查 -- network -- 右边跳出代码窗口
#                     在右边的网页窗口点右键  -- 重新加载  -- 右边代码窗口会看到很多网页加载项  //无实际用处 ， 忽略
#  4. 取得AAA的方法 (使用)： 谷歌浏览器 -- 打开数据网址  -- 网页窗口点右键  -- 点检查 -- network -- 右边跳出代码窗口
#                           在右边的网页窗口点净额排序 -- 右边跳出代码窗口会出现几项新的加载项网址 -- 点击get？开头的加载项
#                           -- 点击下面的data  -- 点击下面的diff  -- 会出现一个股票列表
#                           -- 点击代码窗口左边的heards标签烂  -- 下面的request url就是我们所需要的网址
#                           -- 右键点击get? -- copy -- copy as cURL(cmd)
#  5. 打开自动转化网址 https://curlconverter.com/   --  把刚才copy的网址黏贴进去  -- 下面会自动生产代码
#     （如果有错误，就把错误后面的部分去掉，只保留前面的网址部分）

#  说明1：下面的cookies和headers可删除掉，进行简化



print("east money")

import requests
import json

cookies = {
    'qgqp_b_id': 'a6d93b0734081ca4a251c5e9db36c584',
    'st_si': '93474612291201',
    'st_pvi': '71063777505321',
    'st_sp': '2024-11-17%2022%3A56%3A48',
    'st_inirUrl': '',
    'st_sn': '1',
    'st_psi': '20241117225648681-113300300813-7559131466',
    'st_asi': 'delete',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    # 'Cookie': 'qgqp_b_id=a6d93b0734081ca4a251c5e9db36c584; st_si=93474612291201; st_pvi=71063777505321; st_sp=2024-11-17%2022%3A56%3A48; st_inirUrl=; st_sn=1; st_psi=20241117225648681-113300300813-7559131466; st_asi=delete',
    'Referer': 'https://data.eastmoney.com/zjlx/detail.html',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


response = requests.get(
    'https://push2.eastmoney.com/api/qt/clist/get?&fid=f62&po=1&pz=50&pn=2&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13',
    cookies=cookies,
    headers=headers,
)

# print (response)   #<Response [200]>

#第二步： 数据清洗

# print (response.text)
# print (type(response.text))

resp_dict = json.loads(response.text)

# print (resp_dict)
# print (type(resp_dict))

companys =[]
prices =[]

datas = resp_dict.get('data').get('diff')
for data in datas:
    # print(data)

    company = data.get('f14')  #公司名称
    share_1 = data.get('f184')     #今日主力流入占比
    # share_5 = data.get('')     #5天内机构购买量
    # share_10 = data.get('')     #10天内机构购买量
    price = data.get('f2')     #股价


    if(share_1 >30):
       companys.append(company)
       prices.append(price)


print(companys)
print(prices)




# 下面从第2句开始有错误，所以只拷贝第一句到https://curlconverter.com/里面
# curl ^"https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery1123021866400437329447_1765625252729^&fid=f62^&po=0^&pz=50^&pn=1^&np=1^&fltt=2^&invt=2^&ut=8dec03ba335b81bf4ebdf7b29ec27d15^&fs=m^%^3A0^%^2Bt^%^3A6^%^2Bf^%^3A^!2^%^2Cm^%^3A0^%^2Bt^%^3A13^%^2Bf^%^3A^!2^%^2Cm^%^3A0^%^2Bt^%^3A80^%^2Bf^%^3A^!2^%^2Cm^%^3A1^%^2Bt^%^3A2^%^2Bf^%^3A^!2^%^2Cm^%^3A1^%^2Bt^%^3A23^%^2Bf^%^3A^!2^%^2Cm^%^3A0^%^2Bt^%^3A7^%^2Bf^%^3A^!2^%^2Cm^%^3A1^%^2Bt^%^3A3^%^2Bf^%^3A^!2^&fields=f12^%^2Cf14^%^2Cf2^%^2Cf3^%^2Cf62^%^2Cf184^%^2Cf66^%^2Cf69^%^2Cf72^%^2Cf75^%^2Cf78^%^2Cf81^%^2Cf84^%^2Cf87^%^2Cf204^%^2Cf205^%^2Cf124^%^2Cf1^%^2Cf13^" ^
#   -H ^"Accept: */*^" ^
#   -H ^"Accept-Language: zh-CN,zh;q=0.9^" ^
#   -H ^"Connection: keep-alive^" ^
#   -b ^"qgqp_b_id=d6509a8756844017aadb2f8c439ea160; fullscreengg=1; fullscreengg2=1; st_si=55979280077969; st_nvi=-MrtDBIBAYlXwkAMRU_SA1302; nid18=0e17cb22ecf6960f4858bfd8cbdced17; nid18_create_time=1765621341517; gviem=bnjiNxVc95XM1IEHYcoUR5a7c; gviem_create_time=1765621341517; st_asi=delete; st_pvi=42778556761729; st_sp=2025-12-13^%^2018^%^3A22^%^3A21; st_inirUrl=; st_sn=3; st_psi=20251213192732807-113300300813-4421254618^" ^
#   -H ^"Referer: https://data.eastmoney.com/zjlx/detail.html^" ^
#   -H ^"Sec-Fetch-Dest: script^" ^
#   -H ^"Sec-Fetch-Mode: no-cors^" ^
#   -H ^"Sec-Fetch-Site: same-site^" ^
#   -H ^"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36^" ^
#   -H ^"sec-ch-ua: ^\^"Chromium^\^";v=^\^"142^\^", ^\^"Google Chrome^\^";v=^\^"142^\^", ^\^"Not_A Brand^\^";v=^\^"99^\^"^" ^
#   -H ^"sec-ch-ua-mobile: ?0^" ^
#   -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^"
