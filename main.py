import os
import cv2
from paddleocr import PPStructure, draw_structure_result, save_structure_res
import re
import time
import pandas as pd
import fire

table_engine = PPStructure(show_log=False)

validate_date_delta = 2


def check(date, username, name_ocr, time_ocr):
    if get_date_delta(time_ocr, date) > validate_date_delta:
        return False
    if len(username) != len(name_ocr):
        return False
    if not username.startswith(name_ocr.replace("*", "")):
        return False
    return True


def match(reg, total):
    reg_re = re.search(reg, total, re.M | re.I)
    reg_ocr = ""
    if reg_re and len(reg_re.groups()) >= 1:
        reg_ocr = reg_re.group(1)
    return reg_ocr


def get_date_delta(day1, day2):
    time_array1 = time.strptime(day1, "%Y.%m.%d")
    timestamp_day1 = int(time.mktime(time_array1))
    time_array2 = time.strptime(day2, "%Y.%m.%d")
    timestamp_day2 = int(time.mktime(time_array2))
    return (timestamp_day2 - timestamp_day1) // 60 // 60 // 24


def save_to_file(df, date):
    output_file_name = "check_" + date + ".xlsx"
    writer = pd.ExcelWriter(output_file_name)  # 初始化一个writer
    df.index += 1  # 序号从 1 开始
    df.to_excel(writer)  # table输出为excel, 传入writer
    writer.save()  # 保存


def deal_file(date="2020.06.24"):
    df = pd.DataFrame(columns=["姓名", "文件名日期", "截图姓名", "结果", "采样日期", "是否完成"])
    for file in os.listdir(date):
        img_path = date + "/" + file
        username = file.split(".")[0]
        img = cv2.imread(img_path)
        results = table_engine(img)

        total = ""
        for result in results:
            result.pop('img')
            for line in result["res"]:
                total += line["text"] + " "
        print(total)

        name_ocr = match(r'姓\s*名：\s*(\S*)', total)
        time_ocr = match(r'核酸检测时间\s*(\S*)', total)
        nucleic_result_ocr = match(r'(\S性)', total)
        print("name:", name_ocr)
        print("time:", time_ocr)
        print("nucleic_result:", nucleic_result_ocr)

        validate = check(date, username, name_ocr, time_ocr)
        df = df.append(
            {"姓名": username, "文件名日期": date, "截图姓名": name_ocr, "结果": nucleic_result_ocr,
             "采样日期": time_ocr, "是否完成": "是" if validate else "否"},
            ignore_index=True)
    save_to_file(df, date)


if __name__ == '__main__':
    start_time = time.time()
    fire.Fire(deal_file)
    end_time = time.time()
    print("运行时间:", end_time - start_time)
