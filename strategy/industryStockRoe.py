from tqdm import tqdm

from strategy.tushare_util import get_pro_client
import pandas as pd
from datetime import datetime
import time
import numpy as np

sdate = '20130101'
edate = '20210831'
period = '20181231'
this_year = 2021
next_year_of_start_year = 2019
n = 3  # 统计的年数 ，this_year-next_year_of_start_year+1


# 财务指标数据fina_indicator
def get_fina_indicator(ts_code):
    pro = get_pro_client()
    fina = pro.fina_indicator(ts_code=ts_code, start_date=sdate, end_date=edate, period=period,
                              fields='end_date,ts_code,roe')
    # 时间 扣非  销售毛利率 ROE
    for i in range(next_year_of_start_year, this_year):
        p = str(i) + '1231'
        fina_next = pro.fina_indicator(ts_code=ts_code, start_date=sdate, end_date=edate, period=p,
                                       fields='end_date,ts_code,roe')
        fina = pd.concat([fina, fina_next])
    try:
        # Tushare提供的数据有时候有重复的部分，需要去掉
        fina = fina.drop([1])
    except:
        pass
    try:
        # 设置序列
        fina['index'] = range(0, n)
        fina = fina.set_index('index')
    except:
        pass
    # 接口调用次数限制限制
    time.sleep(2)
    return fina


def get_byRoe():
    stock_code = get_all_code()
    stocks_p = []
    num = 0
    for code in tqdm(stock_code['ts_code'].values):
        Roe = get_fina_indicator(code)
        # print(ROE['roe'])
        RoeState = 1
        for index, row in Roe.iterrows():
            print(row['roe'])  # 输出每行的索引值
            if row['roe'] is not None:
                if row['roe'] < 25:
                    print("不符合条件")
                    ROEstate = 0
                    break
                else:
                    ROEstate = 1
            else:
                print("ROE不存在")
                break
        if RoeState == 1:
            print("符合条件股票代码")
            name = stock_code[stock_code['ts_code'] == code]['name']
            print(str(code)+"~~"+str(name))
            stocks_p.append(code)
        else:
            pass
    print(stocks_p)
    ## 存数据
    with open('D:/Work/git/ecosys/data/ROE25.txt', 'w') as f:
        for i in stocks_p:
            f.write(i)
    f.close()


# 获取当前交易的股票代码和名称
def get_all_code():
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    # 去除ST股票
    df = df[~df.name.str.contains('ST')]
    # 去除202011以后的新股
    df['list_date'] = df['list_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
    df = df[(df['list_date'] < datetime(2017, 1, 1))]
    stocks = df[['ts_code', 'name']]
    print("股票数量为")
    print(len(stocks))
    return stocks


def main():
    trade_date = '20210903'
    get_byRoe()


if __name__ == "__main__":
    main()
