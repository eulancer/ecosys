from collector.tushare_util import get_pro_client
import datetime
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import config


# 获取当前交易的股票代码和名称
def get_all_code():
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    # 去除ST股票
    df = df[~df.name.str.contains('ST')]
    # 去除202011以后的新股
    df['list_date'] = df['list_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
    print(df['list_date'])
    df = df[(df['list_date'] < datetime(2021, 1, 1))]

    codes = df.ts_code.values
    names = df.name.values
    stock = dict(zip(names, codes))
    return stock


# 获取当前国企企业代码
def get_Ne_code():
    codes = []
    names = []
    with open(config.Ne_path) as f:
        raw_line = f.readlines()
        for i in raw_line:
            line = i.strip('')
            # print(line)
            if line.startswith('#'):
                continue
            (code, name) = line.split('\t')
            codes.append(code.strip('\t'))  # .strip('\t') 去空格
            names.append(name.strip('\n'))  # .strip('\n') 去除换行符
    f.close()
    stock = dict(zip(names, codes))
    # print(stock)
    return stock


# 默认设定时间周期为当前时间往前推120个交易日
# 日期可以根据需要自己改动
def get_holder_data(code, n=30):
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    t = datetime.now()
    t0 = t - timedelta(n)
    start = t0.strftime('%Y%m%d')
    end = t.strftime('%Y%m%d')
    # 将获取股东数量
    df = pro.stk_holdernumber(ts_code=code, start_date=start, end_date=end)
    return df


# 按日期获取
def get_holder_data(code, start, end):
    pro = get_pro_client()
    df = pro.stk_holdernumber(ts_code=code, start_date=start, end_date=end)
    return df


# 获取市值小于200亿的股票
def get_total_mv(code, trade_date):
    pro = get_pro_client()
    df = pro.query('daily_basic', ts_code=code, trade_date=trade_date,
                   fields='ts_code,trade_date,total_mv')
    return df.total_mv


# 获取去重的股票
def get_stock_list():
    stocks = get_all_code()
    all_stocks = get_all_code()
    Ne_stocks = get_Ne_code()
    print(Ne_stocks)
    # 去除国企
    try:
        for j in all_stocks:
            print(j)
            if j in Ne_stocks:
                print(j)
                print(stocks[j])
                del stocks[j]
    except IOError:
        print
        "Error: 没有找到文件或读取文件失败"
    else:
        print
        "内容写入文件成功"

    return stocks


# 获取股票的市值
def get_stock_total_mv(code, date):
    pro = get_pro_client()
    df = pro.query('daily_basic', ts_code=code, trade_date=date,
                   fields='ts_code,trade_date,total_mv')
    print(df)
    return df['total_mv'][0]


"""
# 获取报告周期小于2股东人数持续监测周最终股票名单
def get_stock(trade_date):
    n = 120
    stocks = get_stock_list()
    stocks_p = []
    trade_date = trade_date
    i = 1
    for code in stocks.values():
        i = i + 1
        print("第" + str(i) + "次")
        df = get_holder_data(code, n=n)
        time.sleep(0.01)
        # 报告周期小于2周
        inner_time = datetime.strptime(df["ann_date"][0], '%Y%m%d') - datetime.strptime(df["end_date"][0], '%Y%m%d')
        print(inner_time)
        try:
            if inner_time.days <= 15 and df["holder_num"][0] < 40000:
                num1 = df["holder_num"][0] - df["holder_num"][1]
                num2 = df["holder_num"][1] - df["holder_num"][2]
                # 股东人数持续监测
                if num1 < 0 and num2 < 0:
                    if get_stock_total_mv(code, trade_date) < 2000000:
                        # 该代码放入股票池
                        stocks_p.append(code)
                        print("该代码放入股票池 ")
                        print(code)
        except Exception as re:
            print(re)
    print(stocks_p)
    with open('D:/Work/git/ecosys/data/holder_list.txt', 'w') as f:
        for i in stocks_p:
            f.write(i)
    f.close()
"""


# 半半年和3季报股东股东15%的股票
# 获取报告周期小于2股东人数持续监测周最终股票名单
def get_stock(trade_date):
    stocks = get_all_code()
    stocks_p = []
    trade_date = trade_date
    i = 1
    for code in stocks.values():
        i = i + 1
        try:
            if get_stock_total_mv(code, trade_date) < 2000000:
                print("第" + str(i) + "次")
                time.sleep(0.55)
                df_mid = get_holder_data(code, 20210601, 20210630)
                df_third = get_holder_data(code, 20210801, 20210902)
                # 股东小于40000
                if df_third["holder_num"][0] < 40000:
                    # 股东下降比例
                    num1 = df_mid["holder_num"][0] - df_third["holder_num"][0]
                    num2 = df_mid["holder_num"][0]
                    rate = num1 / num2 * 100
                    # 股东人数持续监测
                    if rate >= 15:
                        # 该代码放入股票池
                        stocks_p.append(code)
                        print("该代码放入股票池 ")
                        print(code)
        except Exception as re:
            print(re)
    print(stocks_p)
    with open('D:/Work/git/ecosys/data/holder_list_0830-15-01  .txt', 'w') as f:
        for i in stocks_p:
            f.write(i)
    f.close()


def main():
    trade_date = 20210830
    get_stock(trade_date)


if __name__ == "__main__":
    main()
