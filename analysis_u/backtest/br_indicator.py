import backtrader as bt
import datetime
import pandas as pd
import numpy as np
import sys
from analysis_u.strategy.tushare_util import get_pro_client
from loguru import logger


@logger.catch()
class SmaCross(bt.Strategy):
    params = dict(period=5
                  )

    def __init__(self):
        self.move_average = bt.ind.MovingAverageSimple(
            self.datas[0].close, period=self.params.period
        )

    def next(self):
        if not self.position.size:
            if self.datas[0].close[-1] < self.move_average.sma[0] < self.datas[0].close[0]:
                self.buy(size=100)
        elif self.datas[0].close[-1] > self.move_average.sma[0] > self.datas[0].close[0]:
            self.buy(size=100)


@logger.catch()
def main():
    pro = get_pro_client()
    dataS = pro.daily(ts_code='600000.SH', tart_date='20200701', end_date='20210930')
    dataS.sort_index(inplace=True, ascending=False)
    dataS['trade_date'] = pd.to_datetime(dataS['trade_date'], format='%Y%m%d')

    print(dataS)
    data = dataS[['open', 'high', 'low', 'close', 'vol', 'trade_date']].copy()
    data.rename(columns={'vol': 'volume', 'trade_date': 'datetime'}, inplace=True)
    data = data.set_index('datetime')
    # del data['datetime']
    print(data)
    # print(data)
    data['openinterest'] = 0
    data = bt.feeds.PandasData(dataname=data,
                               fromdate=datetime.datetime(2019, 1, 1),
                               todate=datetime.datetime(2019, 12, 31)
                               )
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(SmaCross)
    cerebro.broker.setcash(10000);
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()
    print('最终市值：%.2f' % cerebro.broker.get_value())
    cerebro.plot(style='bar')


if __name__ == "__main__":
    main()
