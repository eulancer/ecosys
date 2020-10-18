import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt

import config
from collector.tushare_util import get_pro_client
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


# 当前交易日的所有股票代码
def get_stock():
    pro = get_pro_client()
    # 当前交易日的所有股票代码
    df = pro.stock_basic(exchange='', list_status='L',
                         fields='ts_code,symbol,name,area,industry,list_date')
    print(len(df))

    # 获取当前所有非新股次新股代码和名称 20190101以后上市的股票
    df = df[df['list_date'].apply(int).values < 20190101]
    # 获取当前所有非新股次新股代码和名称
    codes = df.ts_code.values
    names = df.name.values
    # 构建一个字典方便调用
    code_name = dict(zip(names, codes))
    return code_name


#  获取数据1：使用tushare获取上述股票周价格数据并转换为周收益率
def get_data(code, start='20200101', end='20201016'):
    pro = get_pro_client()
    df = pro.daily(ts_code=code, start_date=start, end_date=end, fields='trade_date,close')
    # 将交易日期设置为索引值
    df.index = pd.to_datetime(df.trade_date)
    df = df.sort_index()
    return df.close


# 获取数据2：使用mysql获取上述股票周价格数据并转换为周收益率
def read_data(code):
    sql = "SELECT * FROM stock_his_data where trade_date>20190101 and ts_code='" + code + "'"  # SQL query
    # print(sql)
    df = pd.read_sql(sql=sql, con=config.engine)  # read data to DataFrame 'df'
    # 将交易日期设置为索引值
    df.index = pd.to_datetime(df.trade_date)
    df = df.sort_index()
    df = df['close']
    # df.to_csv("cs.csv", encoding="GBk")
    # print("read_data")
    return df


# 计算收益率
def cal_ret(df, w=5):
    """w:周5;月20;半年：120; 一年250
    """
    df = df / df.shift(w) - 1
    return df.iloc[w:, :].fillna(0)


# 获取所有股票在某个期间的RPS值


# 计算每个交易日所有股票滚动w日的RPS
def all_RPS(data):
    # dates = data.index.strftime('%Y%m%d')
    dates = data.index
    print("data~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # print(data)
    RPS = {}
    for i in range(len(data)):
        RPS[dates[i]] = pd.DataFrame(get_RPS(data.iloc[i]).values, columns=['收益率', '排名', 'RPS'],
                                     index=get_RPS(data.iloc[i]).index)
        # print("get_RPS(data.iloc[i]).index")
        # print(dates[i])
        # print(RPS[dates[i]])
    return RPS


# 计算RPS
def get_RPS(ser):
    df = pd.DataFrame(ser.sort_values(ascending=False))
    df['n'] = range(1, len(df) + 1)
    df['rps'] = (1 - df['n'] / len(df)) * 100
    # print("df")
    # print(df)

    return df


# 获取所有股票在某个期间的RPS值
def all_data(rps, ret):
    df = pd.DataFrame(np.NaN, columns=ret.columns, index=ret.index)
    for date in ret.index:
        # date = date.strftime('%Y%m%d')
        d = rps[date]
        for c in d.index:
            df.loc[date, c] = d.loc[c, 'RPS']
            # print(c)
            # print("df.loc[date, c]")
            # print(df.loc[date, c])
    return df


# 对股票价格走势和RPS进行可视化
def plot_rps(stock, w, data, df):
    print(stock)
    plt.subplot(211)
    w = w
    data[stock][120:].plot(figsize=(16, 16), color='r')
    plt.title(stock + '股价走势', fontsize=15)
    plt.yticks(fontsize=12)
    plt.xticks(fontsize=12)

    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.subplot(212)
    df[stock].plot(figsize=(16, 8), color='b')
    print(df[stock])
    plt.title(stock + 'RPS相对强度', fontsize=15)
    # my_ticks = pd.date_range('20200609', '2020-09-03', freq='m')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.show()
    print("结束")


def main():
    code_name = get_stock()
    # 获取股票数据
    data = pd.DataFrame()
    i = 0
    for name, code in code_name.items():
        # data[name] = get_data(code)  从网上获取数据
        data[name] = read_data(code)  # 从数据库获取数据
        # print(data[name])
        # i = i + 1
        # print(i)
        # if i > 30:
        # break
    # data.to_csv('daily_data.csv', encoding='gbk')
    # data = pd.read_csv('daily_data.csv', encoding='gbk', index_col='trade_date')

    ret120 = cal_ret(data, w=120)
    print("ret120")
    rps120 = all_RPS(ret120)
    print("rps120")
    # 构建一个以前面收益率为基础的空表
    df_new = pd.DataFrame(np.NaN, columns=ret120.columns, index=ret120.index)

    df = all_data(rps120, ret120)
    print(df)

    # dates = ['20200228', '20200331', '20200430', '202007531', '20200630', '20200731', '20200831', '20200930']
    dates = ['20200930']
    """
    df_rps = pd.DataFrame()
    for date in dates:
        df_rps[date] = rps120[date].index[:50]
    print(df_rps)
    """

    stock = '春风动力'
    w = 120
    plot_rps(stock, w, data, df)


if __name__ == "__main__":
    main()
