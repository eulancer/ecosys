# 先引入后面可能用到的包（package）
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt

# 正常显示画图时出现的中文和负号
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

from datetime import datetime
import backtrader as bt


class MyStrategy(bt.Strategy):
    params = (('maperiod', 15),
              ('printlog', False),)

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close

        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # 添加移动均线指标
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    # 策略核心，根据条件执行买卖交易指令（必选）
    def next(self):
        # 记录收盘价
        # self.log(f'收盘价, {dataclose[0]}')
        if self.order:  # 检查是否有指令等待执行,
            return
        # 检查是否持仓
        if not self.position:  # 没有持仓
            # 执行买入条件判断：收盘价格上涨突破15日均线
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # 执行买入
                self.order = self.buy()
        else:
            # 执行卖出条件判断：收盘价格跌破15日均线
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # 执行卖出
                self.order = self.sell()

    # 交易记录日志（可省略，默认不输出结果）
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    # 记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}')
            self.bar_executed = len(self)

            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    # 回测结束后输出结果（可省略，默认输出结果）
    def stop(self):
        self.log('(MA均线： %2d日) 期末总资金 %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)

    def plot_stock(code, title, start, end):
        dd = ts.get_k_data(code, autype='qfq', start=start, end=end)
        dd.index = pd.to_datetime(dd.date)
        dd.close.plot(figsize=(14, 6), color='r')
        plt.title(title + '价格走势\n' + start + ':' + end, size=15)
        plt.annotate(f'期间累计涨幅:{(dd.close[-1] / dd.close[0] - 1) * 100:.2f}%', xy=(dd.index[-150], dd.close.mean()),
                     xytext=(dd.index[-500], dd.close.min()), bbox=dict(boxstyle='round,pad=0.5',
                                                                        fc='yellow', alpha=0.5),
                     arrowprops=dict(facecolor='green', shrink=0.05), fontsize=12)
        plt.show()

    def main(code, start, end='', startcash=10000, qts=500, com=0.001):
        # 创建主控制器
        cerebro = bt.Cerebro()
        # 导入策略参数寻优
        cerebro.optstrategy(MyStrategy, maperiod=range(3, 31))
        # 获取数据
        df = ts.get_k_data(code, autype='qfq', start=start, end=end)
        df.index = pd.to_datetime(df.date)
        df = df[['open', 'high', 'low', 'close', 'volume']]
        # 将数据加载至回测系统
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        # broker设置资金、手续费
        cerebro.broker.setcash(startcash)
        cerebro.broker.setcommission(commission=com)
        # 设置买入设置，策略，数量
        cerebro.addsizer(bt.sizers.FixedSize, stake=qts)
        print('期初总资金: %.2f' %
              cerebro.broker.getvalue())
        cerebro.run(maxcpus=1)
        print('期末总资金: %.2f' % cerebro.broker.getvalue())
