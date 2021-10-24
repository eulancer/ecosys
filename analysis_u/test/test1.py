    # 先引入后面可能用到的包（package）
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from tqdm import tqdm
# 引入TA-Lib库
import talib as ta
from analysis_u.strategy.tushare_util import get_pro_client
from analysis_u.strategy.tushare_util import get_all_code_df
from datetime import datetime, timedelta
from loguru import logger
import matplotlib as mplab
# 正常显示画图时出现的中文和负号
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
index = {'上证综指': '000001.SH', '深证成指': '399001.SZ',
         '沪深300': '000300.SH', '创业板指': '399006.SZ',
         '上证50': '000016.SH', '中证500': '000905.SH',
         '中小板指': '399005.SZ', '上证180': '000010.SH'}


@logger.catch
def main():
    code = '002706.SZ'
    arbr_result(code, n=120)


@logger.catch
def get_data(code, n):
    pro = get_pro_client()

    # 获取数据时间
    t = datetime.now()
    t0 = t - timedelta(n)
    start = t0.strftime('%Y%m%d')
    end = t.strftime('%Y%m%d')

    # 如果代码在字典index里，则取的是指数数据
    # 否则取的是个股数据

    if code in index.values():
        df = pro.index_daily(ts_code=code, start_date=start, end_date=end)

    else:
        df = pro.daily(ts_code=code, start_date=start, end_date=end)
    # 将交易日期设置为索引值
    df.index = pd.to_datetime(df.trade_date)
    df = df.sort_index()
    return df


@logger.catch
def arbr(code, n):
    df = get_data(code, n)[['ts_code', 'open', 'high', 'low', 'close']]
    print(df)
    try:
        df['HO'] = df.high - df.open
        df['OL'] = df.open - df.low
        df['HCY'] = df.high - df.close.shift(1)
        df['CYL'] = df.close.shift(1) - df.low
        # 计算AR、BR指标
        df['AR'] = ta.SUM(df.HO, timeperiod=26) / ta.SUM(df.OL, timeperiod=26) * 100
        df['BR'] = ta.SUM(df.HCY, timeperiod=26) / ta.SUM(df.CYL, timeperiod=26) * 100
    except:
        pass
    print(df)
    return df[['ts_code', 'close', 'AR', 'BR']].dropna()


def arbr_result(code, n):
    df = arbr(code, n)
    if df['AR'].iat[-1] > df['BR'].iat[-1] and df['BR'].iat[-1] < 100:
        print('出现买入信号,BR运行在AR下方')
        print(code)
        # stocks_p.append(stock)
        return None
    if df['AR'].iat[-1] < 70 and df['BR'].iat[-1] < 50:
        print(df['AR'].iat[-1], df['BR'].iat[-1])
        print('BR<40,AR<60: 空方力量较强，但随时可能反转上涨，考虑买进')
        plot_arbr(code, df)
        return code


@logger.catch
def plot_arbr(code, df, n=120):
    fig = plt.figure(dpi=100, figsize=(15, 5))

    #fig.suptitle(code + 'matplotlib object-oriented')
    ax = fig.add_subplot(211)
    # df['trade_date'] = df['trade_date'].strftime("%Y%m%d")
    ax.plot_date(df.index, df['close'], linestyle='-')

    dateFmt = mpl.dates.DateFormatter('%b')
    ax.xaxis.set_major_formatter(dateFmt)
    weeksLoc = mplab.dates.WeekdayLocator()
    monthsLoc = mplab.dates.MonthLocator()
    ax.xaxis.set_minor_locator(weeksLoc)
    ax.xaxis.set_major_locator(monthsLoc)
    ax.set(title=code + '价格走势')
    # plt.title(code + '价格走势', fontsize=15)
    # fig, ax = plt.subplots(2, 1, figsize=(14, 5))

    # 价格趋势
    # ax[0].plot(df['trade_date'], df['close'])
    # ax[0].xlabel('')
    # ax[0].title(code + '价格走势', fontsize=15)

    ax_arbr = fig.add_subplot(212)
    ax_arbr.plot_date(df.index, df[['AR', 'BR']], linestyle='-')
    ax_arbr.set_title(code + 'ARBR')
    # plt.suptitle(code + 'ARBR', fontsize=15)
    ax_arbr.xaxis.set_minor_locator(weeksLoc)
    ax_arbr.xaxis.set_major_locator(monthsLoc)
    ax_arbr.xaxis.set_major_formatter(dateFmt)
    # plt.plot(df['trade_date'], df[['AR', 'BR']])

    # arbr趋势
    # ax[1].plot(df['trade_date'], df[['AR', 'BR']])
    # ax[1].title(code + '价格走势', fontsize=15)
    # ax[1] = plt.gca()
    x_major_locator = MultipleLocator(20)
    # ax为两条坐标轴的实例
    # ax.xaxis.set_major_locator(x_major_locator)
    plt.show()


if __name__ == '__main__':
    main()
