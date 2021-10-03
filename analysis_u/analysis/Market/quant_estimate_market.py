import tushare as ts
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
import scipy.signal as signal
import scipy
from matplotlib.pyplot import MultipleLocator
from analysis_u.strategy.tushare_util import get_pro_client

plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False

estimate_market_period = 60


class estimate_market():
    # 判断多空，中长期、中短期
    def long_or_short(self, df, lineEdit):
        last_index = len(df) - 1
        if (df['close'][last_index] > df['ma20'][last_index]) & (df['ma20'][last_index] > df['ma60'][last_index]):
            if (df['ma20'][last_index] > df['ma20'][last_index - 1]) & (
                    df['ma60'][last_index] > df['ma60'][last_index - 1]):
                if (df['dif'][last_index] > 0) & (df['hist'][last_index] > 0):
                    lineEdit.append('当前，长多且短多')

        if (df['ma20'][last_index] > df['close'][last_index]) & (df['close'][last_index] > df['ma60'][last_index]):
            if (df['ma20'][last_index] < df['ma20'][last_index - 1]) & (
                    df['ma60'][last_index] > df['ma60'][last_index - 1]):
                if (df['dif'][last_index] > 0) & (df['hist'][last_index] < 0):
                    lineEdit.append('当前，长多兼短空')

        if (df['ma60'][last_index] > df['close'][last_index]) & (df['close'][last_index] > df['ma20'][last_index]):
            if (df['ma20'][last_index] > df['ma20'][last_index - 1]) & (
                    df['ma60'][last_index] < df['ma60'][last_index - 1]):
                if (df['dif'][last_index] < 0) & (df['hist'][last_index] > 0):
                    lineEdit.append('当前，长空兼短多')

        if (df['ma60'][last_index] > df['ma20'][last_index]) & (df['ma20'][last_index] > df['close'][last_index]):
            if (df['ma20'][last_index] < df['ma20'][last_index - 1]) & (
                    df['ma60'][last_index] < df['ma60'][last_index - 1]):
                if (df['dif'][last_index] < 0) & (df['hist'][last_index] < 0):
                    lineEdit.append('当前，长空兼短空')

    def detect_long_short_transform(self, df, lineEdit):
        for i in range(len(df) - estimate_market_period, len(df)):
            if (df['dif'][i - 1] < 0) & (df['dif'][i] > 0):
                lineEdit.append('在' + str(df['trade_date'][i]) + '中长期由空转多')
            if (df['hist'][i - 1] < 0) & (df['hist'][i] > 0):
                lineEdit.append('在' + str(df['trade_date'][i]) + '中短期由空转多')
            if (df['dif'][i - 1] > 0) & (df['dif'][i] < 0):
                lineEdit.append('在' + str(df['trade_date'][i]) + '中长期由多转空')
            if (df['hist'][i - 1] > 0) & (df['hist'][i] < 0):
                lineEdit.append('在' + str(df['trade_date'][i]) + '中短期由多转空')

        last_index = len(df) - 1
        if (df['dif'][last_index] > 0) & (df['hist'][last_index] > 0):
            lineEdit.append('<font color=\"#CD5C5C\">Tips</font>:此时处于A类行情，最容易获利，一般为主升浪或者说波浪理论中的3浪')
        if (df['dif'][last_index] > 0) & (df['hist'][last_index] < 0):
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:此时处于B类行情，可以持股，处于调整之中但可以持股待涨，中长期多头中的短线空头，一般为上升浪之后的回调，是波浪理论中的某级别第2浪或第4浪')
        if (df['dif'][last_index] < 0) & (df['hist'][last_index] < 0):
            lineEdit.append('<font color=\"#CD5C5C\">Tips</font>:此时处于C类行情，最差的，是中长期空头与中短期空头，一般为主跌浪或者说C浪中的下跌')
        if (df['dif'][last_index] < 0) & (df['hist'][last_index] > 0):
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:此时处于D类行情，可以轻仓操作，但获利也比较困难，中长期空头中的短线多头，一般为下跌浪之后的反弹，是波浪理论中某级别的b浪')


if __name__ == '__main__':
    pro = get_pro_client()
    code = '002340.SZ'
    begin_date = '20210109'
    end_date = '20210930'
    SHORT = 10  # 快速移动平均线的滑动窗口长度。
    LONG = 20  # 慢速移动平均线de 滑动窗口
    MID = 9
    df = pro.daily(ts_code=code, start_date=begin_date, end_date=end_date)
    data = pro.query('stock_basic', exchange='', list_status='L',
                     fields='ts_code,symbol,name,area,industry,list_date')
    code_name = data.loc[data['ts_code'] == code].name.values
    df2 = df.iloc[::-1]
    # 获取dif,dea,hist，它们的数据类似是tuple，且跟df2的date日期一一对应
    # 记住了dif,dea,hist前33个为Nan，所以推荐用于计算的数据量一般为你所求日期之间数据量的3倍
    # 这里计算的hist就是dif-dea,而很多证券商计算的MACD=hist*2=(dif-dea)*2
    dif, dea, hist = ta.MACD(df2['close'].astype(float).values, fastperiod=10, slowperiod=20, signalperiod=5)
    ma_60 = ta.MA(df2['close'].astype(float).values, timeperiod=60)
    ma_20 = ta.MA(df2['close'].astype(float).values, timeperiod=20)
    df3 = pd.DataFrame({'dif': dif[33:], 'dea': dea[33:], 'hist': hist[33:], 'ma60': ma_60[33:], 'ma20': ma_20[33:]},
                       index=df2['trade_date'][33:], columns=['dif', 'dea', 'hist', 'ma60', 'ma20'])
    df4 = pd.merge(df3, df2, on='trade_date', how='left')
    plt.plot(df4['dif'], 'r')
    plt.plot(df4['dea'], 'y')
    plt.bar(df4['trade_date'], df4['hist'])
    plt.legend(['dif', 'dea', 'hist'])
    plt.title(str(code_name))
    x_major_locator = MultipleLocator(5)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.xticks(rotation=270)
    plt.show()
    print('开始市场研判')
    print(
        '------------------------------------------------------------------------------------------------------------------------')
    estimate_market = estimate_market()
    estimate_market.long_or_short(df4)
    estimate_market.detect_long_short_transform(df4)
