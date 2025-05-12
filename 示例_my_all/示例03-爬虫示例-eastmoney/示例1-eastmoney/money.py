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

# response = requests.get(
#     'https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112305221344159284751_1731855408438&fid=f62&po=1&pz=50&pn=2&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13',
#     cookies=cookies,
#     headers=headers,
# )

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
