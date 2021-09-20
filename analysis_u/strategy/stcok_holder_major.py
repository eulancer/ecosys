from datetime import datetime
from tqdm import tqdm
from analysis_u.strategy.tushare_util import get_pro_client
from analysis_u.strategy.tushare_util import get_all_code
import numpy as np
import pandas as pd
import time


# 获取十大股东持股数量
def get_holder_data(code, ann_date):
    pro = get_pro_client()
    df = pro.top10_holders(ts_code=code, ann_date=ann_date)
    df2 = df.drop_duplicates(['holder_name'], keep='first')
    return df2['hold_ratio'].sum()


# 十大股东持股数量大于70&
def get_all_stock(ann_date, percent):
    stocks = get_all_code()
    stocks_p = []
    for code in tqdm(stocks.values()):
        time.sleep(6)
        try:
            if get_holder_data(code, ann_date) > percent:
                stocks_p.append(code)
                print("该代码放入股票池 ")
                print(code)
                print(get_holder_data(code, ann_date))
        except Exception as re:
            print(re)
    print(stocks_p)
    with open('//holder70.txt', 'w') as f:
        for i in stocks_p:
            f.write(i)
    f.close()


def main():
    ann_date = '20210831'
    percent = 70
    get_all_stock(ann_date, percent)


if __name__ == "__main__":
    main()
