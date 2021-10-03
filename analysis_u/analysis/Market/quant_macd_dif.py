import tushare as ts
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
import scipy.signal as signal
import scipy
from matplotlib.pyplot import MultipleLocator
from analysis_u.strategy.tushare_util import get_pro_client
# 用DIF寻找第一、二买卖点
detect_period = 60


class detect_dif_situation():
    def cross_zero_line_once(self, df, j):
        if ((df['dif'][j - 1] < 0) & (df['dif'][j] > 0)) or ((df['dif'][j - 1] > 0) & (df['dif'][j] < 0)):
            return True
        else:
            return False

    def detect_dif_up(self, df, lineEdit):
        # 检测是否过去detect_period天是否突破0轴(寻找买点)
        cross_time = 0
        cross_time_list = []
        for i in range(len(df) - detect_period, len(df)):
            if cross_time > 0:
                if (self.cross_zero_line_once(df, i)):
                    cross_time += 1
                    cross_time_list.append(i)
            else:
                if (self.cross_zero_line_once(df, i)) & ((df['dif'][i - 1] < 0) & (df['dif'][i] > 0)):
                    cross_time += 1
                    cross_time_list.append(i)
                    lineEdit.append('过去' + str(detect_period) + '天，在' + str(df['trade_date'][i]) + '第一次突破0轴（可能是第一买点）')
        if (cross_time > 1):
            if ((df['dif'][cross_time_list[1] - 1] > 0) & (df['dif'][cross_time_list[1]] < 0)):
                lineEdit.append(
                    '过去' + str(detect_period) + '天，在' + str(df['trade_date'][cross_time_list[1]]) + '第二次穿过0轴')
        if (cross_time == 3):
            if ((df['dif'][cross_time_list[2] - 1] < 0) & (df['dif'][cross_time_list[2]] > 0)):
                lineEdit.append(
                    '过去' + str(detect_period) + '天，在' + str(df['trade_date'][cross_time_list[2]]) + '第三次突破0轴（可能是第二买点）')
        if cross_time > 3:
            pass

    def detect_dif_down(self, df, lineEdit):
        # 检测是否过去detect_period天是否突破0轴（寻找卖点）
        cross_time = 0
        cross_time_list = []
        for i in range(len(df) - detect_period, len(df)):
            if cross_time > 0:
                if (self.cross_zero_line_once(df, i)):
                    cross_time += 1
                    cross_time_list.append(i)
            else:
                if (self.cross_zero_line_once(df, i)) & ((df['dif'][i - 1] > 0) & (df['dif'][i] < 0)):
                    cross_time += 1
                    cross_time_list.append(i)
                    lineEdit.append('过去' + str(detect_period) + '天，在' + str(df['trade_date'][i]) + '第一次穿过0轴（可能是第一卖点）')
        if (cross_time >= 2):
            if ((df['dif'][cross_time_list[1] - 1] < 0) & (df['dif'][cross_time_list[1]] > 0)):
                lineEdit.append(
                    '过去' + str(detect_period) + '天，在' + str(df['trade_date'][cross_time_list[1]]) + '第二次突破0轴')
        if (cross_time == 3):
            if ((df['dif'][cross_time_list[2] - 1] > 0) & (df['dif'][cross_time_list[2]] < 0)):
                lineEdit.append(
                    '过去' + str(detect_period) + '天，在' + str(df['trade_date'][cross_time_list[2]]) + '第三次穿过0轴（可能是第二卖点）')
        if cross_time > 3:
            pass


# 用DIF趋势线判断
detect_trend_period = 80


class trend_and_dif():
    def detect_peak_and_valley(self, df):
        kernel_size = 5
        smooth_signal = scipy.signal.medfilt(df['dif'], kernel_size=kernel_size)
        indices_peak = signal.find_peaks(smooth_signal[-detect_trend_period:], height=None, threshold=None, distance=5,
                                         prominence=None, width=None, wlen=None, rel_height=None,
                                         plateau_size=None)

        indices_valley = signal.find_peaks(np.array([-i for i in smooth_signal])[-detect_trend_period:], height=None,
                                           threshold=None, distance=5,
                                           prominence=None, width=None, wlen=None, rel_height=None,
                                           plateau_size=None)
        peak_list = [len(df) - detect_trend_period + indices_peak[0][i] for i in range(len(indices_peak[0]))]
        valley_list = [len(df) - detect_trend_period + indices_valley[0][i] for i in range(len(indices_valley[0]))]
        return peak_list, valley_list

    def solve_equation(self, point1, point2):
        k = (point1[1] - point2[1]) / (point1[0] - point2[0])
        b = point1[1] - k * point1[0]
        return k, b

    def detect_break_cross_trend(self, df, lineEdit):
        peak_list, valley_list = self.detect_peak_and_valley(df)
        # 检测是否向上突破下降趋势线
        k, b = self.solve_equation([peak_list[-1], df['dif'][peak_list[-1]]], [peak_list[-2], df['dif'][peak_list[-2]]])
        cross_point = 0
        for i in range(peak_list[-1], len(df)):
            if ((k * i + b - df['dif'][i]) < 0) & ((abs(df['dif'][i] - k * i + b) / abs(df['dif'][i])) > 0.05):
                cross_point = i
                break
        if cross_point != 0:
            lineEdit.append('过去' + str(detect_trend_period) + '天，在' + str(df['trade_date'][cross_point]) + '处突破了下降趋势线')

        # 检测是否跌破上升趋势线
        k1, b1 = self.solve_equation([valley_list[-1], df['dif'][valley_list[-1]]],
                                     [valley_list[-2], df['dif'][valley_list[-2]]])
        break_point = 0
        for i in range(valley_list[-1], len(df)):
            if ((k1 * i + b1 - df['dif'][i]) > 0) & ((abs(k1 * i + b1 - df['dif'][i]) / abs(df['dif'][i])) > 0.05):
                break_point = i
                break
        if break_point != 0:
            lineEdit.append('过去' + str(detect_trend_period) + '天，在' + str(df['trade_date'][break_point]) + '处跌破了上升趋势线')


# 判断DIF与收盘价的背离
detect_trend_period = 80


class detect_divergence():
    def solve_equation(self, point1, point2):
        k = (point1[1] - point2[1]) / (point1[0] - point2[0])
        b = point1[1] - k * point1[0]
        return k, b

    def detect_peak_and_valley(self, df, kernel_size):
        # 更灵敏就把kernel_size往下调
        smooth_signal = scipy.signal.medfilt(df, kernel_size=kernel_size)
        indices_peak = signal.find_peaks(smooth_signal[-detect_trend_period:], height=None, threshold=None, distance=2,
                                         prominence=None, width=None, wlen=None, rel_height=None,
                                         plateau_size=None)

        indices_valley = signal.find_peaks(np.array([-i for i in smooth_signal])[-detect_trend_period:], height=None,
                                           threshold=None, distance=5,
                                           prominence=None, width=None, wlen=None, rel_height=None,
                                           plateau_size=None)
        peak_list = [len(df) - detect_trend_period + indices_peak[0][i] for i in range(len(indices_peak[0]))]
        valley_list = [len(df) - detect_trend_period + indices_valley[0][i] for i in range(len(indices_valley[0]))]
        return peak_list, valley_list

    def detect_bottom_divergence(self, df, lineEdit):
        peak_list_dif, valley_list_dif = self.detect_peak_and_valley(df['dif'], 1)
        peak_list_close, valley_list_close = self.detect_peak_and_valley(df['close'], 5)
        k_dif, b_dif = self.solve_equation([valley_list_dif[-1], df['dif'][valley_list_dif[-1]]],
                                           [valley_list_dif[-2], df['dif'][valley_list_dif[-2]]])
        k_close, b_close = self.solve_equation([valley_list_close[-1], df['close'][valley_list_close[-1]]],
                                               [valley_list_close[-2], df['close'][valley_list_close[-2]]])
        first_buy_point = 0
        if (k_dif > 0) & (k_close < 0):
            first_buy_point = valley_list_dif[-1] + 1
        if first_buy_point != 0:
            lineEdit.append('过去' + str(detect_trend_period) + '天，发现DIF与收盘价的底背离，发生在' + str(
                df['trade_date'][first_buy_point]) + '(可能是第一买点)')
            former_peak_between_valley = 0
            for j in peak_list_dif:
                if valley_list_dif[-2] < j < valley_list_dif[-1]:
                    former_peak_between_valley = j
            for i in range(first_buy_point, len(df)):
                if former_peak_between_valley != 0 & (df['dif'][i] > df['dif'][former_peak_between_valley]):
                    lineEdit.append('过去' + str(detect_trend_period) + '天，DIF与收盘价的底背离后，发生在' + str(
                        df['trade_date'][i]) + ',突破DIF前高(可能是第二买点)')

    def detect_top_divergence(self, df, lineEdit):
        peak_list_dif, valley_list_dif = self.detect_peak_and_valley(df['dif'], 1)
        peak_list_close, valley_list_close = self.detect_peak_and_valley(df['close'], 5)
        # print('peak_list_dif:', df['trade_date'][peak_list_dif])
        k_dif, b_dif = self.solve_equation([peak_list_dif[-1], df['dif'][peak_list_dif[-1]]],
                                           [peak_list_dif[-2], df['dif'][peak_list_dif[-2]]])
        k_close, b_close = self.solve_equation([peak_list_close[-1], df['close'][peak_list_close[-1]]],
                                               [peak_list_close[-2], df['close'][peak_list_close[-2]]])
        first_sell_point = 0
        if (k_dif < 0) & (k_close > 0):
            first_sell_point = peak_list_dif[-1] + 1
        if first_sell_point != 0:
            lineEdit.append('过去' + str(detect_trend_period) + '天，发现DIF与收盘价的顶背离，发生在' + str(
                df['trade_date'][first_sell_point]) + '(可能是第一卖点)')
            former_valley_between_peak = 0
            for j in valley_list_dif:
                if peak_list_dif[-2] < j < peak_list_dif[-1]:
                    former_valley_between_peak = j
            for i in range(first_sell_point, len(df)):
                if former_valley_between_peak != 0 & (df['dif'][i] < df['dif'][former_valley_between_peak]):
                    lineEdit.append('过去' + str(detect_trend_period) + '天，DIF与收盘价的顶背离后，发生在' + str(
                        df['trade_date'][i]) + ',跌破DIF前低(可能是第二卖点)')


#
if __name__ == '__main__':
    pro = get_pro_client()
    code = '002594.SZ'
    begin_date = '20200709'
    end_date = '20210219'
    SHORT = 10  # 快速移动平均线的滑动窗口长度。
    LONG = 20  # 慢速移动平均线de 滑动窗口
    MID = 9
    df = pro.daily(ts_code=code, start_date=begin_date, end_date=end_date)
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
    x_major_locator = MultipleLocator(5)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.xticks(rotation=270)
    plt.show()
    print('开始DIF指标相关检测')
    print(
        '------------------------------------------------------------------------------------------------------------------------')
    dif_situation = detect_dif_situation()
    # DIF寻找买点
    dif_situation.detect_dif_up(df4)
    # DIF寻找卖点
    dif_situation.detect_dif_down(df4)
    print('-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -')
    # 趋势线波段
    trend_dif = trend_and_dif()
    trend_dif.detect_break_cross_trend(df4)
    print('-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -')
    # 检测DIF与收盘价的背离
    detect_divergence = detect_divergence()
    detect_divergence.detect_top_divergence(df4)
    detect_divergence.detect_bottom_divergence(df4)
