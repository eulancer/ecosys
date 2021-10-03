import tushare as ts
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
import scipy.signal as signal
import scipy
from matplotlib.pyplot import MultipleLocator
from analysis_u.analysis.Market.quant_macd_dif import *
from analysis_u.analysis.Market.quant_macd_dif import detect_divergence
from analysis_u.analysis.Market.quant_macd_dea import *
from analysis_u.analysis.Market.quant_macd_histogram import *
from analysis_u.analysis.Market.quant_estimate_market import *

plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QLineEdit, QPushButton
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QTextBrowser, QHBoxLayout, QVBoxLayout
import time


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.iniUI()
        # self.buttonClicked()

    def iniUI(self):
        self.setWindowTitle("MACD信号检测器")
        self.resize(900, 900)

        self.lineEdit = QTextBrowser(self)
        self.lineEdit.move(160, 30)
        self.lineEdit.resize(700, 800)
        font = self.lineEdit.font()  # lineedit current font
        font.setPointSize(12)  # change it's size
        self.lineEdit.setFont(font)

        self.qle = QLineEdit(self)
        self.qle.setPlaceholderText("输入股票代码")
        self.qle.move(20, 80)
        btn = QPushButton("确定", self)
        btn.move(20, 120)
        # print(qle.text())
        btn.clicked.connect(self.buttonClicked)

    def buttonClicked(self):
        pro = get_pro_client()
        code = str(self.qle.text())
        begin_date = '20210409'
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
        df3 = pd.DataFrame(
            {'dif': dif[33:], 'dea': dea[33:], 'hist': hist[33:], 'ma60': ma_60[33:], 'ma20': ma_20[33:]},
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
        self.lineEdit.append('<font color=\"#FF7F50\">股票' + str(code_name) + '的macd指标分析</font>')
        self.lineEdit.append('<font color=\"#E9967A\">开始DIF指标相关检测</font>')
        self.lineEdit.append(
            '<font color=\"#FF0000\">---------------------------------------------------------------------------------</font>')

        dif_situation = detect_dif_situation()
        # DIF寻找买点
        self.lineEdit.append('买点考量')
        dif_situation.detect_dif_up(df4, self.lineEdit)
        # DIF寻找卖点
        self.lineEdit.append('卖点考量')
        dif_situation.detect_dif_down(df4, self.lineEdit)
        self.lineEdit.append(
            '<font color=\"#FF4500\">-   -   -   -   -   -   -   -   -   -   -   -   -     -   -   -   -  -  -  -  -</font>')

        # 趋势线波段
        trend_dif = trend_and_dif()
        trend_dif.detect_break_cross_trend(df4, self.lineEdit)
        self.lineEdit.append(
            '<font color=\"#FF4500\">-   -   -   -   -   -   -   -   -   -   -   -   -     -   -   -   -  -  -  -  -</font>')
        # 检测DIF与收盘价的背离
        detect_divergence1 = detect_divergence()
        detect_divergence1.detect_top_divergence(df4, self.lineEdit)
        detect_divergence1.detect_bottom_divergence(df4, self.lineEdit)
        self.lineEdit.append('\t')
        self.lineEdit.append('\t')

        self.lineEdit.append('开始DEA指标相关检测')
        self.lineEdit.append(
            '<font color=\"#FF0000\">---------------------------------------------------------------------------------')
        gold_cross = gold_death_cross()
        # DIF寻找买点
        gold_cross.detect_gold_cross(df4, self.lineEdit)
        gold_cross.detect_death_cross(df4, self.lineEdit)
        self.lineEdit.append('\t')
        self.lineEdit.append('\t')

        self.lineEdit.append('开始柱状图相关检测')
        self.lineEdit.append(
            '<font color=\"#FF0000\">---------------------------------------------------------------------------------')
        macd_histogram = detect_macd_histogram()
        # DIF寻找买点
        macd_histogram.detect_pull_feet(df4, self.lineEdit)
        macd_histogram.detect_shrink_head(df4, self.lineEdit)
        self.lineEdit.append(
            '<font color=\"#FF4500\">-   -   -   -   -   -   -   -   -   -   -   -   -     -   -   -   -  -  -  -  -</font>')
        macd_histogram.detect_top_divergence(df4, self.lineEdit)
        macd_histogram.detect_bottom_divergence(df4, self.lineEdit)
        self.lineEdit.append(
            '<font color=\"#FF4500\">-   -   -   -   -   -   -   -   -   -   -   -   -     -   -   -   -  -  -  -  -</font>')
        macd_histogram.detect_kill_long_bin(df4, self.lineEdit)
        macd_histogram.detect_force_short_bin(df4, self.lineEdit)
        self.lineEdit.append('\t')
        self.lineEdit.append('\t')

        self.lineEdit.append('开始市场研判')
        self.lineEdit.append(
            '<font color=\"#FF0000\">---------------------------------------------------------------------------------')
        estimate_market1 = estimate_market()
        estimate_market1.long_or_short(df4, self.lineEdit)
        self.lineEdit.append(
            '<font color=\"#FF4500\">-   -   -   -   -   -   -   -   -   -   -   -   -     -   -   -   -  -  -  -  -</font>')
        estimate_market1.detect_long_short_transform(df4, self.lineEdit)
        self.lineEdit.append('\t')
        self.lineEdit.append('\t')
        self.lineEdit.append('\t')
        self.lineEdit.append('\t')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())
