import tushare as ts
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
import scipy.signal as signal
import scipy
from matplotlib.pyplot import MultipleLocator
from analysis_u.strategy.tushare_util import get_pro_client

detect_cross_period = 80


class gold_death_cross():
    def detect_gold_cross(self, df, lineEdit):
        gold_cross_point_underzero = []
        for i in range(len(df) - detect_cross_period, len(df)):
            if (df['dif'][i] < 0) & (df['dea'][i] < 0):
                if (df['dif'][i - 1] < df['dea'][i - 1]) & (df['dif'][i] > df['dea'][i]):
                    gold_cross_point_underzero.append(i)
        gold_cross_point_abovezero = []
        for i in range(len(df) - detect_cross_period, len(df)):
            if (df['dif'][i] > 0) & (df['dea'][i] > 0):
                if (df['dif'][i - 1] < df['dea'][i - 1]) & (df['dif'][i] > df['dea'][i]):
                    gold_cross_point_abovezero.append(i)

        if len(gold_cross_point_underzero) > 0:
            if (df['dif'][gold_cross_point_underzero[0]] < 0) & (df['dea'][gold_cross_point_underzero[0]] < 0):
                lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                    df['trade_date'][gold_cross_point_underzero[0]]) + '处发现DIF0轴以下的黄金交叉')
            for i in range(len(gold_cross_point_underzero) - 1):
                if df['dif'][gold_cross_point_underzero[i]:gold_cross_point_underzero[i + 1]].max() < 0:
                    lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                        df['trade_date'][gold_cross_point_underzero[i + 1]]) + '处发现DIF0轴以下的二次黄金交叉')
                else:
                    lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                        df['trade_date'][gold_cross_point_underzero[i]]) + '处发现DIF0轴以下的黄金交叉')
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:发生一次DIF0轴以下黄金交叉，需判断，是突破下降趋势线的黄金交叉（1浪），还是在一波牛市后，首次发生在空方的黄金交叉（5浪）')
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:发生二次DIF0轴以下黄金交叉，<font color=\"#DAA520\">表明市场经过了充分的调整</font>，预示后市很可能有大幅上涨；要注意与背离、价格趋势线结合使用')
            lineEdit.append('-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -')

        if len(gold_cross_point_abovezero) > 0:
            if (df['dif'][gold_cross_point_abovezero[0]] > 0) & (df['dea'][gold_cross_point_abovezero[0]] > 0):
                lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                    df['trade_date'][gold_cross_point_abovezero[0]]) + '处发现DIF0轴以上的黄金交叉')
            for i in range(len(gold_cross_point_abovezero) - 1):
                if df['dif'][gold_cross_point_abovezero[i]:gold_cross_point_abovezero[i + 1]].min() > 0:
                    lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                        df['trade_date'][gold_cross_point_abovezero[i + 1]]) + '处发现DIF0轴以上的二次黄金交叉')
                else:
                    lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                        df['trade_date'][gold_cross_point_abovezero[i]]) + '处发现DIF0轴以上的黄金交叉')
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:发生一次DIF0轴以上黄金交叉，<font color=\"#DAA520\">买入成功率较高</font>，每一次在0轴之上以及0轴附近的黄金交叉都是加仓机会。但加仓要等价格拉开幅度，<font color=\"#DAA520\">不要在一个区间密集加仓</font>；最好采用正金字塔加仓法。')
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:发生二次DIF0轴以上黄金交叉，<font color=\"#DAA520\">绝佳的做多机会</font>；若指标在0轴之下经过长期震荡后，首次突破0轴发生的二次黄金交叉，这种机会往往在一波大牛市的初始阶段才会有的机会，是效用最大的入场机会；应该发生在0轴之上附近的位置,而不能是发生在高位的黄金交叉')
            lineEdit.append('-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -')

    def detect_death_cross(self, df, lineEdit):
        death_cross_point_underzero = []
        for i in range(len(df) - detect_cross_period, len(df)):
            if (df['dif'][i] < 0) & (df['dea'][i] < 0):
                if (df['dif'][i - 1] > df['dea'][i - 1]) & (df['dif'][i] < df['dea'][i]):
                    death_cross_point_underzero.append(i)
        death_cross_point_abovezero = []
        for i in range(len(df) - detect_cross_period, len(df)):
            if (df['dif'][i] > 0) & (df['dea'][i] > 0):
                if (df['dif'][i - 1] > df['dea'][i - 1]) & (df['dif'][i] < df['dea'][i]):
                    death_cross_point_abovezero.append(i)

        if len(death_cross_point_underzero) > 0:
            if (df['dif'][death_cross_point_underzero[0]] < 0) & (df['dea'][death_cross_point_underzero[0]] < 0):
                lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                    df['trade_date'][death_cross_point_underzero[0]]) + '处发现DIF0轴以下的死亡交叉')
            for i in range(len(death_cross_point_underzero) - 1):
                if df['dif'][death_cross_point_underzero[i]:death_cross_point_underzero[i + 1]].max() < 0:
                    lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                        df['trade_date'][death_cross_point_underzero[i + 1]]) + '处发现DIF0轴以下的二次死亡交叉')
                else:
                    lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                        df['trade_date'][death_cross_point_underzero[i]]) + '处发现DIF0轴以下的死亡交叉')
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:发生一次DIF0轴以下死亡交叉，<font color=\"#DAA520\">通常处于熊市中一波反弹的高位，是卖出信号</font>，如果不能重回0轴之上则说明空方还是占有统治地位，后市仍以看跌为主；若在0轴之下的黄金交叉抄底之后，经过一波反弹，在0轴之下靠近0轴的位置又发生死亡交叉，这时是无条件离场是合理的选择。')
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:发生二次DIF0轴以下死亡交叉，<font color=\"#DAA520\">无条件离场</font>。一般发生在大熊市的下跌C浪或下跌延长浪；两次死亡交叉应发生在0轴之下0轴附近，是经过小幅反弹后的连续两次死亡交叉，而不能是发生在低位的死亡交叉')
            lineEdit.append('-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -')

        if len(death_cross_point_abovezero) > 0:
            if (df['dif'][death_cross_point_abovezero[0]] > 0) & (df['dea'][death_cross_point_abovezero[0]] > 0):
                lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                    df['trade_date'][death_cross_point_abovezero[0]]) + '处发现DIF0轴以上的死亡交叉')
            for i in range(len(death_cross_point_abovezero) - 1):
                if df['dif'][death_cross_point_abovezero[i]:death_cross_point_abovezero[i + 1]].min() > 0:
                    lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                        df['trade_date'][death_cross_point_abovezero[i + 1]]) + '处发现DIF0轴以上的二次死亡交叉')
                else:
                    lineEdit.append('过去' + str(detect_cross_period) + '天，在' + str(
                        df['trade_date'][death_cross_point_abovezero[i]]) + '处发现DIF0轴以上的死亡交叉')
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:发生一次DIF0轴以上死亡交叉，通常0轴之上的死亡交叉发生在多方主导的大趋势中，它说明在大级别的上升趋势中有发生调整的可能，,<font color=\"#DAA520\">是中、短期顶部的标志</font>；应对策略：稳健做法是先了解一部分仓位，若卖出后股价没有明显下跌又创新高及时补仓；死亡交叉发生在高档区、结合趋势线等更有效，')
            lineEdit.append(
                '<font color=\"#CD5C5C\">Tips</font>:发生二次DIF0轴以上死亡交叉是对前一次交叉的确认,0轴上的第二次死亡交叉是可靠的卖出信号；最好与背离、价格趋势线相互验证,<font color=\"#DAA520\">在高位背离后的第二个死亡交叉，后市最大的可能是出现暴跌</font>')


if __name__ == '__main__':
    pro = get_pro_client()
    code = '002179.SZ'
    begin_date = '202101209'
    end_date = '20210919'
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
    print('开始DEA指标相关检测')
    print(
        '------------------------------------------------------------------------------------------------------------------------')
    lineEdit = []
    gold_cross = gold_death_cross()
    # DIF寻找买点
    gold_cross.detect_gold_cross(df4, lineEdit)
    gold_cross.detect_death_cross(df4, lineEdit)
