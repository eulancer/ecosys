from datetime import datetime

from collector.tushare_util import get_pro_client
import numpy as np
import pandas as pd
import time


# 获取当前交易的股票代码和名称
def get_all_code():
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    # 去除ST股票
    df = df[~df.name.str.contains('ST')]
    # 去除2020101以后的新股
    df['list_date'] = df['list_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
    print(df['list_date'])
    df = df[(df['list_date'] < datetime(2020, 1, 1))]

    codes = df.ts_code.values
    names = df.name.values
    stock = dict(zip(names, codes))
    return stock


def get_holder_data(code, ann_date):
    pro = get_pro_client()
    df = pro.top10_holders(ts_code=code, ann_date=ann_date)
    df2 = df.drop_duplicates(['holder_name'], keep='first')
    # print(df2['hold_ratio'].sum())
    return df2['hold_ratio'].sum()


def get_all_stock(ann_date):
    stocks = get_all_code()
    stocks_p = []
    ann_date = ann_date
    i = 1
    for code in stocks.values():
        i = i + 1
        print("第" + str(i) + "次")
        time.sleep(6)
        try:
            if get_holder_data(code, ann_date) > 70:
                stocks_p.append(code)
                print("该代码放入股票池 ")
                print(code)
                print(get_holder_data(code, ann_date))
        except Exception as re:
            print(re)
    print(stocks_p)
    with open('D:/Works/Python/ecosys/data/holder70.txt', 'w') as f:
        for i in stocks_p:
            f.write(i)
    f.close()


def main():
    ann_date = '20201031'
    get_all_stock(ann_date)


if __name__ == "__main__":
    main()