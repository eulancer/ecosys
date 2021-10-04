"""
抛物线转向（SAR）也称停损点转向，其全称叫“Stop and Reveres”，缩写“SAR”，
SAR指标又称为“傻瓜”指标，被广大投资者特别是中小散户普遍运用。SAR指标的一般研判标准包括以下四方面：

1、当股票价格从SAR曲线下方开始向上突破SAR曲线时，为买入信号，预示着股票价格一轮上升行情可能展开，投资者应迅速及时地买进该股票。
2、当股票价格向上突破SAR曲线后继续向上，而SAR曲线也同时向上运动时，表明上涨趋势已形成。SAR曲线对股票价格构成强劲的支撑，投资者应坚决看多或逢低买入该股票。
3、当股票价格从SAR曲线上方开始向下突破SAR曲线时，为卖出信号，预示着股票价格一轮下跌行情可能展开，投资者应及时地卖出该股票。
4、当股票价格向下突破SAR曲线后继续向下，而SAR曲线也同时向下运动的话，表明下跌趋势已形成，SAR曲线对价格会构成巨大的压力，投资者应坚决看空或逢高做空该股票。
"""
import datetime
from datetime import datetime
import talib as tl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import matplotlib as mpl
from matplotlib.patches import Rectangle

from analysis_u.strategy.tushare_util import get_pro_client

from loguru import logger
from matplotlib.ticker import AutoMinorLocator, MultipleLocator, FuncFormatter

"""
避免打印时出现省略号
"""
mpl.rcParams["font.sans-serif"] = ["FangSong"]
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

"""
    参数数据与
    types = [1, 2]  # 1 为指数 '2 为股票
    ts_code = '300683.SZ'
    start_date = '20200201'
    end_date = '20210930'
"""


@logger.catch()
def MA60120_index(ts_code, start_date, end_date, types):
    pro = get_pro_client()
    print(types)
    if types == 1:
        data = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        print(data)
    if types == 2:
        data = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        print(data)

    data['trade_date'] = pd.to_datetime(data['trade_date'], format='%Y%m%d')
    data.index = data['trade_date']
    data.sort_index(inplace=True, ascending=True)
    del data['trade_date']
    data['ma60'] = tl.MA(data['close'], timeperiod=60)
    data['ma120'] = tl.MA(data['close'], timeperiod=120)
    data['SAR'] = tl.SAR(data.high, data.low)

    fig, axs = plt.subplots(2, dpi=80, figsize=(12, 7.5))

    # MA60 和Ma120 曲线
    axs[0].plot(data.index, data[['close', 'ma60', 'ma120']])
    axs[0].set_ylabel('point')
    # 填充
    axs[0].fill_between(data.index, data['ma60'], data['ma120'],
                        data['ma120'] >= data['ma60'], facecolor='green',
                        alpha=0.5)
    axs[0].fill_between(data.index, data['ma60'], data['ma120'],
                        data['ma120'] < data['ma60'], facecolor='r',
                        alpha=0.5)
    axs[0].legend(data[['close', 'ma60', 'ma120']], loc=4, ncol=1)
    axs[0].set_xticklabels(data.index, rotation=0)
    axs[0].set(title='MA60~MA120---' + ts_code)

    #  设置时间刻度，月度
    monthsLoc = mpl.dates.MonthLocator()
    weeksLoc = mpl.dates.WeekdayLocator()

    axs[0].xaxis.set_minor_locator(monthsLoc)

    monthsFmt = mpl.dates.DateFormatter('%Y-%m')
    axs[0].xaxis.set_major_formatter(monthsFmt)

    axs[0].spines['right'].set_color("none")
    axs[0].spines['top'].set_color("none")
    axs[0].grid()

    # SAR 曲线绘制
    axs[1].plot(data.index, data[['close', 'SAR']])
    axs[1].set(title='SAR')

    axs[1].set_ylabel('point')
    axs[1].set_xticklabels(data.index, rotation=0)
    axs[1].xaxis.set_major_formatter(monthsFmt)
    axs[1].legend(data[['close', 'SAR']], loc=4, ncol=1)
    axs[1].spines['right'].set_color("none")
    axs[1].spines['top'].set_color("none")
    axs[1].grid()
    # fig.autofmt_xdate()

    print(data)
    plt.show()


def main():
    types = [1, 2] # 1 为指数； 2 为股票
    ts_code = '300683.SZ'
    start_date = '20200201'
    end_date = '20210930'
    MA60120_index(ts_code, start_date, end_date, types[1])


if __name__ == "__main__":
    main()
"""
    pro = get_pro_client()
    data = pro.fund_daily(ts_code='510300.SH', start_date='2020 0701', end_date='20210930')
    data['trade_date'] = pd.to_datetime(data['trade_date'])

    data.index = data['trade_date']
    data.sort_index(inplace=True, ascending=True)
    del data['trade_date']
    data['SAR'] = tl.SAR(data.high, data.low)
    data['ma60'] = tl.MA(data['close'], timeperiod=60)
    data['ma120'] = tl.MA(data['close'], timeperiod=120)
    # 
    # 采用dataframe自身的函数，坐标轴刻度能够自适应

    data[['close', 'ma60', 'ma120']].plot(grid=True, title='000001.SH')
    plt.figure(dpi=100)
    # plt.plot(data.index, data[['close', 'SAR']])

    print(data)
    plt.show()
"""
