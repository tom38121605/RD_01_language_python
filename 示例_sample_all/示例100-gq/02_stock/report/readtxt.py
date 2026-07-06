import glob
import re

# 获取当前目录下所有 F#*.txt 文件并排序
prefiles = glob.glob("F[0-9]*.txt")
print("pre files", prefiles)

key1 = lambda x: int(re.search(r'F(\d+)', x).group(1))
files = sorted(prefiles, key=key1  )
print("sorted files", files)

all_test_dicts = {}
all_names = {}  # 存储每个字典中代码对应的名称

for file_path in files:

    #----------------------文件名和字典名处理-------------------------

    # 提取数字和后面的文字
    match = re.search(r'F(\d+)([^.]*)\.txt', file_path)
    if not match:
        continue

    num = match.group(1)
    suffix = match.group(2)  # 例如 "分红G" 或 "涨停回调"

    # print(num, suffix)    # 2 B

    # 生成字典名
    if suffix:
        dict_name = f"test_dict{num}{suffix}"
    else:
        dict_name = f"test_dict{num}"

    data_dict = {}
    name_dict = {}  # 存储代码对应的名称


    #----------------------读取文件内容-------------------------

    with open(file_path, 'r', encoding='gbk') as f:
        lines = f.readlines()

    print(lines)

    header_line = None
    data_start_line = 0

    for i, line in enumerate(lines):
        if '代码' in line and '名称' in line:
            header_line = line
            data_start_line = i + 1
            print("start=",data_start_line)

            break

    if header_line is None:
        header_line = lines[1]
        data_start_line = 2

    # 首行字符串，通过tab分拆出“代码，名称”等
    headers = [h.strip() for h in header_line.strip().split('\t')]

#------------------------------------------------------------------------

    for line in lines[data_start_line:]:
        if line.strip() and not line.startswith('数据来源'):
            values = [v.strip() for v in line.strip().split('\t')]
            if len(values) == len(headers):
                row_dict = {}
                code = values[0]

                # 如果代码是519888，跳过该条记录
                if code == '519888':
                    continue

                # 保存名称
                name_idx = headers.index('名称') if '名称' in headers else 1
                name_dict[code] = values[name_idx]

                for i, header in enumerate(headers):
                    val = values[i]
                    try:
                        if '.' in val:
                            row_dict[header] = float(val)
                        elif val.isdigit():
                            row_dict[header] = int(val)
                        else:
                            row_dict[header] = val
                    except (ValueError, TypeError):
                        row_dict[header] = val
                data_dict[code] = row_dict

    test_dict = {}
    for code, info in data_dict.items():
        far_up = info.get('远涨', 0)
        far_down = info.get('远跌', 0)
        test_dict[code] = f"{far_up}, {far_down}"

    all_test_dicts[dict_name] = test_dict
    all_names[dict_name] = name_dict
    globals()[dict_name] = test_dict

# 输出所有字典到 dict.txt
with open('dict.txt', 'w', encoding='utf-8') as f:
    f.write("# 所有字典汇总\n\n")

    for dict_name, test_dict in all_test_dicts.items():
        f.write(f"{dict_name} = {{\n")
        items = list(test_dict.items())
        name_dict = all_names.get(dict_name, {})

        for idx, (code, value) in enumerate(items):
            name = name_dict.get(code, '')
            if idx == len(items) - 1:
                if name:
                    f.write(f'    "{code}": "{value}"   # {name}\n')
                else:
                    f.write(f'    "{code}": "{value}"\n')
            else:
                if name:
                    f.write(f'    "{code}": "{value}",   # {name}\n')
                else:
                    f.write(f'    "{code}": "{value}",\n')
        f.write("}\n\n")

    f.write(f"# 共生成 {len(all_test_dicts)} 个字典\n")

print(f"已生成 {len(all_test_dicts)} 个字典，并保存到 dict.txt")
print("生成的字典:", list(all_test_dicts.keys()))