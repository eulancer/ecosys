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

detect_histogram_period = 60


class detect_macd_histogram():
    def detect_hist_peak(self, df):
        hist_peak_list = []
        higher_rate_hist_peak = 0.03
        for i in range(len(df) - detect_histogram_period, len(df) - 1):
            if (df['hist'][i] > 0) & (df['hist'][i - 1] > 0) & (df['hist'][i + 1] > 0):
                if ((df['hist'][i] - df['hist'][i - 1]) > df['hist'][i - 1] * higher_rate_hist_peak) & (
                        (df['hist'][i] - df['hist'][i + 1]) > df['hist'][i + 1] * higher_rate_hist_peak):
                    if df['hist'][i] > 0.2 * df['hist'].max():
                        hist_peak_list.append(i)
        return hist_peak_list

    def detect_hist_valley(self, df):
        hist_valley_list = []
        higher_rate_hist_valley = 0.02
        for i in range(len(df) - detect_histogram_period, len(df) - 1):
            if (df['hist'][i] < 0) & (df['hist'][i - 1] < 0) & (df['hist'][i + 1] < 0):
                if ((df['hist'][i] - df['hist'][i - 1]) < df['hist'][i - 1] * higher_rate_hist_valley) & (
                        (df['hist'][i] - df['hist'][i + 1]) < df['hist'][i + 1] * higher_rate_hist_valley):
                    if df['hist'][i] < 0.2 * df['hist'].min():
                        hist_valley_list.append(i)
        return hist_valley_list

    # 判断抽脚
    def detect_pull_feet(self, df, lineEdit):
        valley_list_hist = self.detect_hist_valley(df)
        # print()
        lineEdit.append('在' + str([df['trade_date'][i + 1] for i in
                                   valley_list_hist]) + '处发生抽脚，<font color=\"#CD5C5C\">Tips</font>:DIF线在0轴上方和0轴附近的成功率较高。“绿柱变红柱”买点比“绿柱抽脚”买点成功率高且更稳健。需要同时伴随成交量明显放大。')

    # 判断缩头
    def detect_shrink_head(self, df, lineEdit):
        peak_list_hist = self.detect_hist_peak(df)
        lineEdit.append('在' + str([df['trade_date'][i + 1] for i in
                                   peak_list_hist]) + '处发生缩头，<font color=\"#CD5C5C\">Tips</font>:多头市场的缩头可以看作涨势在减弱，但不一定会跌；而空头市场的缩头通常是新的一轮下跌的开始。')

    # 判断柱状线与收盘价顶背离
    def detect_top_divergence(self, df, lineEdit):
        hist_peak_list = []
        for i in range(len(df) - detect_histogram_period, len(df) - 1):
            if (df['hist'][i] > 0) & (df['hist'][i - 1] > 0) & (df['hist'][i + 1] > 0):
                if ((df['hist'][i] - df['hist'][i - 1]) > df['hist'][i - 1] * 0.03) & (
                        (df['hist'][i] - df['hist'][i + 1]) > df['hist'][i + 1] * 0.03):
                    if df['hist'][i] > 0.2 * df['hist'].max():
                        hist_peak_list.append(i)
        if len(hist_peak_list) > 1:
            if df['hist'][hist_peak_list[-1]] < df['hist'][hist_peak_list[-2]]:
                if df['close'][hist_peak_list[-1]] > df['close'][hist_peak_list[-2]]:
                    lineEdit.append('在' + str(df['trade_date'][hist_peak_list[-1]]) + '处发生柱状图和收盘价的顶背离')

    # 判断柱状线与收盘价底背离
    def detect_bottom_divergence(self, df, lineEdit):
        hist_valley_list = []
        for i in range(len(df) - detect_histogram_period, len(df) - 1):
            if (df['hist'][i] < 0) & (df['hist'][i - 1] < 0) & (df['hist'][i + 1] < 0):
                if ((df['hist'][i] - df['hist'][i - 1]) < df['hist'][i - 1] * 0.05) & (
                        (df['hist'][i] - df['hist'][i + 1]) < df['hist'][i + 1] * 0.05):
                    if df['hist'][i] < 0.2 * df['hist'].min():
                        hist_valley_list.append(i)
        if len(hist_valley_list) > 1:
            if df['hist'][hist_valley_list[-1]] > df['hist'][hist_valley_list[-2]]:
                if df['close'][hist_valley_list[-1]] <= df['close'][hist_valley_list[-2]]:
                    lineEdit.append('在' + str(df['trade_date'][hist_valley_list[-1]]) + '处发生柱状图和收盘价的底背离')

    # 判断杀多棒
    def detect_kill_long_bin(self, df, lineEdit):
        valley_list_hist = self.detect_hist_valley(df)
        kill_long_list = []
        if len(valley_list_hist) > 0:
            for i in range(len(valley_list_hist) - 1):
                if np.array([i for i in df['hist'][valley_list_hist[i]:valley_list_hist[i + 1]]]).max() < 0:
                    kill_long_list.append(valley_list_hist[i] + np.argmax(
                        np.array([i for i in df['hist'][valley_list_hist[i]:valley_list_hist[i + 1]]])))
                    lineEdit.append('在' + str(df['trade_date'][valley_list_hist[i] + np.argmax(np.array([i for i in
                                                                                                         df['hist'][
                                                                                                         valley_list_hist[
                                                                                                             i]:
                                                                                                         valley_list_hist[
                                                                                                             i + 1]]]))]) + '处出现\'<font color=\"#DAA520\">杀多棒</font>\'')

    # 判断逼空棒
    def detect_force_short_bin(self, df, lineEdit):
        peak_list_hist = self.detect_hist_peak(df)
        force_short_list = []
        if len(peak_list_hist) > 0:
            for i in range(len(peak_list_hist) - 1):
                if np.array([i for i in df['hist'][peak_list_hist[i]:peak_list_hist[i + 1]]]).min() > 0:
                    force_short_list.append(peak_list_hist[i] + np.argmax(
                        np.array([i for i in df['hist'][peak_list_hist[i]:peak_list_hist[i + 1]]])))
                    lineEdit.append('在' + str(df['trade_date'][peak_list_hist[i] + np.argmax(np.array([i for i in
                                                                                                       df['hist'][
                                                                                                       peak_list_hist[
                                                                                                           i]:
                                                                                                       peak_list_hist[
                                                                                                           i + 1]]]))]) + '处出现\'<font color=\"#DAA520\">逼空棒</font>\'')


if __name__ == '__main__':
    pro = get_pro_client()
    code = '000001.SZ'
    begin_date = '20210409'
    end_date = '20210930'
    SHORT = 10  # 快速移动平均线的滑动窗口长度。
    LONG = 20  # 慢速移动平均线de 滑动窗口
    MID = 9
    df = pro.daily(ts_code=code, start_date=begin_date, end_date=end_date)
    data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    code_name = data.loc[data['ts_code'] == code].name.values
    df2 = df.iloc[::-1]
    # 获取dif,dea,hist，它们的数据类似是tuple，且跟df2的date日期一一对应
    # 记住了dif,dea,hist前33个为Nan，所以推荐用于计算的数据量一般为你所求日期之间数据量的3倍
    # 这里计算的hist就是dif-dea,而很多证券商计算的MACD=hist*2=(dif-dea)*2
    dif, dea, hist = ta.MACD(df2['close'].astype(float).values, fastperiod=10, slowperiod=20, signalperiod=5)
    df3 = pd.DataFrame({'dif': dif[33:], 'dea': dea[33:], 'hist': hist[33:]},
                       index=df2['trade_date'][33:], columns=['dif', 'dea', 'hist'])
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
    lineEdit = []
    print('开始柱状图相关检测')
    print(
        '------------------------------------------------------------------------------------------------------------------------')
    macd_histogram = detect_macd_histogram()
    # DIF寻找买点
    macd_histogram.detect_pull_feet(df4, lineEdit)
    macd_histogram.detect_shrink_head(df4, lineEdit)
    print('-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -')
    macd_histogram.detect_top_divergence(df4, lineEdit)
    macd_histogram.detect_bottom_divergence(df4, lineEdit)
    print('-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -')
    macd_histogram.detect_kill_long_bin(df4, lineEdit)
    macd_histogram.detect_force_short_bin(df4, lineEdit)
    print('-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -')
