
import sys
import numpy as np
import matplotlib.pyplot as plt
import h5py
from os.path import expanduser
import os.path

import time
import datetime
import ntplib
import glob

import pytesseract
from PIL import Image
import re


image_path = "01.png"

img = Image.open(image_path)

pytesseract.pytesseract.tesseract_cmd = r"D:\Program Files\Tesseract-OCR\tesseract.exe"

# config = "--psm 6 -c segment_penalty=10"
# text = pytesseract.image_to_string(img, config=config, lang='eng')

text = pytesseract.image_to_string(img, lang='eng')

print("文字：",text)
print("-" * 50)

# 解析表格
lines = text.strip().split('\n')

# 跳过空行
# lines = [line.strip() for line in lines if line.strip()]

new_lines = []
for line in lines:
    if line.strip():
        new_lines.append(line)
lines = new_lines

if len(lines) < 2:
    print("未能识别出表格数据")


# 从第二行开始解析数据（第一行是表头）
result_dict = {}

for line in lines[1:]:  # 跳过表头
    # 用正则提取数字
    numbers = re.findall(r'(\d+\.?\d*)', line)
    if len(numbers) >= 3:
        code = int(float(numbers[0]))
        x = float(numbers[1])
        z = float(numbers[2])
        result_dict[code] = {
            "X": x,
            "Z": z
        }


print("提取结果：")
print(result_dict)

# 输出为格式化字典
print("\n格式化输出：")
for code, values in result_dict.items():
    print(f"  {code}: X={values['X']}, Z={values['Z']}")


