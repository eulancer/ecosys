import backtrader as bt
import datetime
import pandas as pd
import pandas as pd
import quantstats
import numpy as np
import sys
import pyfolio as pf
from analysis_u.strategy.tushare_util import get_pro_client
import matplotlib.pyplot as plt
from loguru import logger


@logger.catch()
# 策略函数
class SmaCross(bt.Strategy):
    params = dict(period=5, fgPrint=False
                  )

    def log(self, txt, dt=None, fgPrint=False):
        # log记录函数
        if self.params.fgPrint or fgPrint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s,%s', (dt.isoformat(), txt))
            # logger.info("log")

    def __init__(self):
        # 默认数据，一般使用股票池中下标为0的股票
        # 通常使用close,作为主要分析数据字段
        self.dataclose = self.datas[0].close
        self.move_average = bt.ind.MovingAverageSimple(
            self.datas[0].close, period=self.params.period
        )

    def next(self):
        # next 函数是最重要的trade交易函数
        # 调用log 函数，输出BT回测过程
        # self.log('收盘价 close %.2f' % self.dataclose[0])
        # 检查订单执行情况，默认每次只能执行一次订单
        # if self.order:
        # return
        # 检查丹青股票仓位
        # 股票池

        if not self.position.size:
            # 如果仓位为0，执行买入操作
            # 使用均线移动策略
            if self.datas[0].close[-1] < self.move_average.sma[0] < self.datas[0].close[0]:
                self.log('设置买单 buy create %.2f' % self.dataclose[0])
                self.buy(size=1500)

        # elif self.datas[0].close[-1] > self.move_average.sma[0] > self.datas[0].close[0]:
        # self.log('设置卖 sell create %.2f' % self.dataclose[0])
        # self.sell(size=100)

        else:
            # 如果仓位>0,就可以执行卖的操作
            # 这个是仓位设置模式
            # 设置5个交易日后，可以进行卖操作
            if len(self) > (self.bar_executed + 5):
                self.log('设置卖 sell create %.2f' % self.dataclose[0])
                self.sell(size=1500)

        # self.log('CLose收盘价,%.2f' % self.dataclose[0])

    # def stop(self):

    # notify_order 非必须
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行 buy executed,报价： %.2f,佣金 Comm %.2f' % (order.executed.price, order.executed.comm))
            elif order.issell():
                self.log('卖单执sell executed,报价： %.2f，佣金 Comm %.2f' % (order.executed.price, order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单order 取消')
        # 检查完成，没有交易中订单
        self.order = None


@logger.catch()
# 1、创建主函数
def main():
    # topqt，作为当前工作目录
    # sys.path.append("topqt/")
    # 设置股票池(待定)
    # syblst = ['600919.SH', '600919.SH']

    pro = get_pro_client()

    # 准备股票日线数据，输入到backtrader,
    ## tushare的数据是降序，要改为升序；
    ## 将pandas的列名修改为符合backtrader的格式，包括：'vol': 'volume', 'trade_date': 'datetime'

    dataS = pro.daily(ts_code='601919.SH', start_date='20180601', end_date='20210930')
    dataS.sort_index(inplace=True, ascending=False)
    dataS['trade_date'] = pd.to_datetime(dataS['trade_date'], format='%Y%m%d')
    data = dataS[['open', 'high', 'low', 'close', 'vol', 'trade_date']].copy()
    data.rename(columns={'vol': 'volume', 'trade_date': 'datetime'}, inplace=True)
    data = data.set_index('datetime')

    data['openinterest'] = 0  # 0不平仓；-1平仓；
    # 调用pandas dataframe格式数据

    data = bt.feeds.PandasData(dataname=data,
                               fromdate=datetime.datetime(2018, 6, 2),
                               todate=datetime.datetime(2021, 9, 30)
                               )

    # 2、创建主控制器
    cerebro = bt.Cerebro()
    # 导入数据
    cerebro.adddata(data)
    # 导入策略参数寻优

    # broker设置资金、手续费
    cerebro.broker.setcommission(commission=0.001)
    cerebro.broker.setcash(10000)
    start_cash = cerebro.broker.startingcash
    print('开始资金: %.2f' % cerebro.broker.getvalue())
    # 设置每手交易为10，不在使用默认值，默认为1
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # 设置买入设置，策略，数量
    cerebro.addstrategy(SmaCross, fgPrint=False)

    # 设置回测结果分析：
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqnAnz')
    cerebro.addanalyzer(bt.analyzers.VWR, _name='VWR')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio', legacyannual=True)
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')

    tframes = dict(days=bt.TimeFrame.Days, weeks=bt.TimeFrame.Weeks, months=bt.TimeFrame.Months,
                   years=bt.TimeFrame.Years)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='TimeAnz', timeframe=tframes['years'])

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    # 3、运行行数
    logger.info("开始执行run量化回测运算")
    results = cerebro.run()
    # cerebro.run()

    ROI = (cerebro.broker.getvalue() - cerebro.broker.startingcash) / cerebro.broker.startingcash * 100
    logger.info("完成量化回测运算")
    print('最终市值：%.2f' % cerebro.broker.getvalue())
    print('ROI 投资回报率：%.2f' % ROI)

    # 打印分析量化数据，采用内置的指标分析库
    logger.info('分析量化回测数据')
    strat = results[0]
    anzs = strat.analyzers
    dsharp = anzs.SharpeRatio.get_analysis()['sharperatio']
    trade_info = anzs.TradeAnalyzer.get_analysis()

    dw = anzs.DW.get_analysis()
    max_DrawDown_len = dw['max']['len']
    max_DrawDown = dw['max']['drawdown']
    max_DrawDown_money = dw['max']['moneydown']

    print('t 夏普指数 SharpRatio', dsharp)
    print('t 最大回测周期 max_DrawDown_len', max_DrawDown_len)
    print('t 最大回测 max_DrawDown', max_DrawDown)
    print('t 最大回测资金 max_DrawDown_money', max_DrawDown_money)

    # 打印分析指标分析结果，采用第三方quantstats- 非必须
    for alyzer in strat.analyzers:
        alyzer.print()

    # 生成量化分析图表（应用外部组件quantstats）- 非必须
    logger.info('专业量化分析图表')
    pyfoliozer = anzs.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    pf.create_full_tear_sheet(
        returns,
        positions=positions,
        transactions=transactions,
        live_start_date='2019-06-02')

    returns.index = returns.index.tz_convert(None)  # pyfoliozer获取数据
    quantstats.reports.full(returns)
    quantstats.reports.html(returns, output='quantstats.html', title='Stock Sentiment')

    import webbrowser
    f = webbrowser.open('quantstats.html')

    # pf.create_full_tear_sheet(returns)  #create_full_tear_sheet 只适用在juypter

    # 4、绘制图形
    # 绘制蜡烛图
    params = dict(
        style='line',
        barup='red',
        bardown='green',
        volup='red',
        voldown='green',
    )
    logger.info("开始绘制图形")

    # iplot=False 会报错，可能是版本原因导致的
    cerebro.plot(numfigs=1, iplot=False, **params)


if __name__ == "__main__":
    main()
