import os
import time

import numpy as np

from collector.tushare_util import get_pro_client
import pandas as pd
from tqdm import tqdm
import json


def concept():
    # 概念和股票对应关系
    concept2code_dict = {}
    # 股票和概念对应概关系
    code2concept_dict = {}
    # 概念名称
    concept_name_dict = {}

    # 当日概念列表
    pro = get_pro_client()
    concept_df = pro.concept()
    print(concept_df)

    for i in concept_df.groupby('code'):
        #x = i['name'].iat[0]
        print(i)
    # 当日行情
    today = '20210908'
    hq_df = pro.daily(trade_date=today)

    for ts in tqdm(concept_df.code.to_list()):
        for _ in range(3):
            print(_)
            try:
                # 获取概念对应的股票清单
                code_df = pro.concept_detail(id=ts, fields='ts_code')
                # print("code_df")
                # print(code_df)
            except:
                print('retry')
            else:
                code_list = code_df.ts_code.to_list()
                # 将概念和概念对应的股票的股票代码放入数组
                concept2code_dict[ts] = code_list
                time.sleep(0.5)
                break
        #     with open("concept2code.json","r") as f:
        #         concept2code_dict=json.load(f)

        print('Generate code2concept')
        # 生成股票代码对应概念字典
        for ts_code in tqdm(hq_df.ts_code):
            #  print(1)
            code2concept_dict[ts_code] = []
            for k, v in concept2code_dict.items():
                # 如果代码在概念里，那么概念放入股票对应概念对应字典：
                if ts_code in v:
                    code2concept_dict[ts_code].append(k)

        print('Generate concept_name_dict')
        # 生成概念对应中文名字典
        # 这个代码暂时看不懂
        # 利用分组函数及匿名行数获取,



        concept_name_dict = concept_df.groupby('code')['name'].apply(lambda x: x.iat[0]).to_dict()
        print("concept_name_dict")
        print("-" * 30)
        print(concept_name_dict)
        # 将上述字典存入json文件以备后用
        with open("concept2code.json", "w") as f:
            json.dump(concept2code_dict, f)

        with open("code2concept.json", "w") as f:
            json.dump(code2concept_dict, f)

        with open("concept_name_dict.json", "w") as f:
            json.dump(concept_name_dict, f)
    else:
        # download为False，直接加载字典
        with open("concept2code.json", "r") as f:
            concept2code_dict = json.load(f)

        with open("code2concept.json", "r") as f:
            code2concept_dict = json.load(f)

        with open("concept_name_dict.json", "r") as f:
            concept_name_dict = json.load(f)

    print(concept_name_dict)


def main():
    concept()


if __name__ == "__main__":
    main()
