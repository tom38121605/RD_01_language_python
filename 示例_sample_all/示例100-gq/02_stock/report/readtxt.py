import glob
import re

# 获取当前目录下所有 F#*.txt 文件并排序
prefiles = glob.glob("F[0-9]*.txt")
print("pre files", prefiles)   # ['F1分HG.txt', 'F2涨停HT.txt']

key1 = lambda x: int(re.search(r'F(\d+)', x).group(1))
files = sorted(prefiles, key=key1  )
print("sorted files", files)   # ['F1分HG.txt', 'F2涨停HT.txt']

all_test_dicts = {} # 远z远d部分子字典，{'test_dict1B': {'600016': '0.283, -0.412', '600755': '0.204, -0.362'}}
all_names = {}      # 注释部分的子字典，{'test_dict1B': {'600016': '民生YH', '600755': '厦门GM'}}

for file_path in files:

    #----------------------文件名和字典名处理-------------------------

    # 提取两堵墙之间数字和后面的文字， 两堵墙是 "F .txt"
    # match = re.search(r'F(\d+)([^.]*)\.txt', file_path)
    match = re.search(r'F(\d+)(.*)\.txt', file_path)  # 取得F后面的数字和数字后面文件名的所有字符串
    if not match:
        continue

    num = match.group(1)   # 1
    suffix = match.group(2)  #  "分HG"

    # print(num, suffix)    # 1 分HG

    # 依次生成当前文件的字典名
    if suffix:
        dict_name = f"test_dict{num}{suffix}"  # 取得字典名： test_dict1分HG
    else:
        dict_name = f"test_dict{num}"

    data_dict = {}
    name_dict = {}  # 存储各票代码对应的名称，如 蓝天RQ


    #----------------------读取文件内容-------------------------

    with open(file_path, 'r', encoding='gbk') as f:
        lines = f.readlines()

    # print(lines)  # 全文

    header_line = None
    data_start_line = 0

    for i, line in enumerate(lines):

        # print(line)

        if '代码' in line and '名称' in line:   # 判断是否为 header 行
            header_line = line
            data_start_line = i + 1
            print("start=",data_start_line)   # 2

            break

    if header_line is None:
        header_line = lines[1]
        data_start_line = 2

    # 首行字符串，通过tab分拆出“代码，名称”等
    headers = [h.strip() for h in header_line.strip().split('\t')]
    print("headers=", headers)  # headers= ['代码', '名称', ..., '流通S值Y']

    name_idx = headers.index('名称') if '名称' in headers else 1
    print("name_idx=", name_idx)

    #------------------------------------------------------------------------

    for line in lines[data_start_line:]:
        # print(line)
        if line.strip() and not line.startswith('数据来源'):

            # 明细行字符串，通过tab分拆出“远z，远d”等
            values = [v.strip() for v in line.strip().split('\t')]
            print("values=", values)  # values= ['605388', '均瑶JK', ... , '29.003']

            # 如果该行的记录有效，则如下处理
            if len(values) == len(headers):  #如果明细行和首行里面的元素数量相同，则如下处理
                row_dict = {}
                code = values[0]

                # 如果代码是519888，跳过该条记录
                if code == '519888':
                    continue

                # 下面两行删除
                # name_idx = headers.index('名称') if '名称' in headers else 1
                # print("name_idx=", name_idx)

                # 保存GP名称，到name_dict
                name_dict[code] = values[name_idx]
                print("name_dict=", name_dict)       #{'600016': '民生YH'}

                # 把各行的数据和header，合并生成一个数据子字典row_dict
                for i, header in enumerate(headers):
                    val = values[i]

                    # 下面是空格，数字，小数点的相关处理
                    try:
                        if '.' in val:
                            row_dict[header] = float(val)
                        elif val.isdigit():
                            row_dict[header] = int(val)
                        else:
                            row_dict[header] = val
                    except (ValueError, TypeError):
                        row_dict[header] = val

                # 在把该行的code作为key，和子字典row_dict，再合并生成一个父字典 data_dict
                data_dict[code] = row_dict

                print("row_dict=", row_dict)    # {'代码': 600662, ... , '十日涨': 0.033}
                print("data_dict=", data_dict)  # {'600662': {'代码': 600662, ... , '十日涨': 0.033} }


# ----------here -------------------
    test_dict = {}
    for code, info in data_dict.items():
        far_up = info.get('远涨', 0)
        far_down = info.get('远跌', 0)
        test_dict[code] = f"{far_up}, {far_down}"

    all_test_dicts[dict_name] = test_dict
    all_names[dict_name] = name_dict

    globals()[dict_name] = test_dict

print("\n")
print(all_test_dicts)  # {'test_dict1B': {'600016': '0.283, -0.412', '600755': '0.204, -0.362'}}
print(all_names)       # {'test_dict1B': {'600016': '民生YH', '600755': '厦门GM'}}

# 输出所有字典到 dict.txt
with open('dict.txt', 'w', encoding='utf-8') as f:
    f.write("# 所有字典汇总\n\n")

    for dict_name, test_dict in all_test_dicts.items():

        sdictname = f"{dict_name} = {{\n"    # 各字典的首行，字典名称，如 test_dict1分HG = {
        f.write(sdictname)

        items = list(test_dict.items())
        name_dict = all_names.get(dict_name, {})

        print(items)        # [('600016', '0.283, -0.412'), ('600755', '0.204, -0.362')]  //列表，里面是元组
        # print(items[0])     # ('600016', '0.283, -0.412')

        print(name_dict)             # {'600016': '民生YH', '600755': '厦门GM'}   //子字典
        # print(name_dict['600016'])   # 民生YH


        for idx, (code, value) in enumerate(items):
            name = name_dict.get(code, '')   # 通过列表里元组的code(GP代码)，取得字典里相应的name(GP名称)
            print(name)  # 民生YH

            if idx == len(items) - 1: # 最后一行，末尾没有逗号
                if name:
                    sline = f'    "{code}": "{value}"   # {name}\n'  # "600755": "0.204, -0.362"   # 厦门GM
                else:
                    sline = f'    "{code}": "{value}"\n'

            else:   #末尾多一个逗号
                if name:
                    sline = f'    "{code}": "{value}",   # {name}\n'  # "600016": "0.283, -0.412",   # 民生YH
                else:
                    sline = f'    "{code}": "{value}",\n'

            f.write(sline)
        f.write("}\n\n")

    f.write(f"# 共生成 {len(all_test_dicts)} 个字典\n")

print(f"{len(all_test_dicts)} 个字典，保存到 dict.txt")
# print("生成的字典:", list(all_test_dicts.keys()))