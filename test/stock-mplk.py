from matplotlib import pyplot as plt
import mplfinance as mpf
import pandas as pd
import talib
import numpy as np
from partd import pandas, numpy

from collector.tushare_util import get_pro_client
from dateutil.parser import parse


# 获取股票数据使用mpl并绘制K线图
def data_list(ts_code, start_date, end_date):
    pro = get_pro_client()
    # df = pro.daily(ts_code='000001.SZ', start_date='20200701', end_date='2020918')
    df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df = df[len(df):None:-1]
    print(df)
    # df.sort_index(inplace=True)
    data = pd.DataFrame()
    data['Open'] = df['open']
    data['High'] = df['high']
    data['Low'] = df['low']
    data['Close'] = df['close']
    data['Volume'] = df['vol']
    data['low'] = df['low']
    print(df.trade_date[1])
    print(parse(df.trade_date[1]))
    data.index = pd.DatetimeIndex(df.trade_date)
    return data
    # print(data.index)


# 数据分析标记
def data_analyze(data):
    """
    简单的数据分析，并返回数据分析的结果列表,具体算法随便写写的
    """
    if data.shape[0] == 0:
        data = data
    s_list = []
    b_list = []
    b = -1
    for i, v in data['High'].iteritems():
        if v > data['Open'][i] and (b == -1 or b == 1):
            b_list.append(data['Low'][i])
            b = 0
        else:
            b_list.append(np.nan)  # 添加nan的目的是，对齐主图的k线数量
        if data['Close'][i] < data['Open'][i] and (b == -1 or b == 0):
            s_list.append(v)
            b = 1
        else:
            s_list.append(np.nan)
    return b_list, s_list


def plot(data):
    b_list, s_list = data_analyze(data)
    add_plot = [
        #mpf.make_addplot(b_list, scatter=True, markersize=200, marker='^', color='y'),
        #mpf.make_addplot(s_list, scatter=True, markersize=200, marker='v', color='r'),
        # mpf.make_addplot(data[['Volume']]),
        # mpf.make_addplot(data['Close'], panel='lower', color='g', secondary_y='auto')
    ]
    mpf.plot(data, type='candle', style='charles', mav=(2, 5, 10), addplot=add_plot, volume=True,
             show_nontrading=False)


def main():
    data = data_list('000001.SH', '20200701', '20200930')

    plot(data)


if __name__ == "__main__":
    main()
