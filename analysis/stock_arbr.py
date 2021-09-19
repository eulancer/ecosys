# 先引入后面可能用到的包（package）
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from tqdm import tqdm
# 引入TA-Lib库
import talib as ta
from strategy.tushare_util import get_pro_client
from strategy.tushare_util import get_all_code_df
from datetime import datetime, timedelta
from loguru import logger

# 正常显示画图时出现的中文和负号
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
index = {'上证综指': '000001.SH', '深证成指': '399001.SZ',
         '沪深300': '000300.SH', '创业板指': '399006.SZ',
         '上证50': '000016.SH', '中证500': '000905.SH',
         '中小板指': '399005.SZ', '上证180': '000010.SH'}


# 获取当前交易的股票代码和名称
def get_code():
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    codes = df.ts_code.values
    names = df.name.values
    stock = dict(zip(names, codes))
    stocks = dict(stock, **index)
    return stocks


# 默认设定时间周期为当前时间往前推120个交易日
# 日期可以根据需要自己改动
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


# 计算AR、BR指标
# code 股票代码
# n ARBR 计算的时间跨度
@logger.catch
def arbr(code, n):
    df = get_data(code, n)[['ts_code', 'trade_date', 'open', 'high', 'low', 'close']]
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
    return df[['ts_code', 'trade_date', 'close', 'AR', 'BR']].dropna()


# 判断买入股票
# 买入信号：BR通常运行在AR上方，一旦BR跌破AR并在AR之下运行时，表明市场开始筑底，视为买进信号；BR<40,AR<60: 空方力量较强，但随时可能反转上涨，考虑买进。
# 参数：code 股票代码；n：时间跨度；

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


# 对价格和ARBR进行可视化
def plot_arbr(code, df, n=120):
    fig, ax = plt.subplots(2, 1, figsize=(14, 5))

    # 价格趋势
    fig.plot(df['trade_date'], df['close'])
    fig.xlabel('')
    fig.title(code + '价格走势', fontsize=15)

    # arbr趋势
    ax.plot(df['trade_date'], df[['AR', 'BR']])
    ax.title(code + '价格走势', fontsize=15)
    ax = plt.gca()
    x_major_locator = MultipleLocator(20)
    # ax为两条坐标轴的实例
    ax.xaxis.set_major_locator(x_major_locator)
    plt.show()


@logger.catch
def main():
    logger.add('runtime.log')
    n = 120  # 参数
    stocks = get_all_code_df()  # 将list改为 data frame
    stocks_p = []  # 保存候选的股票

    for code in tqdm(stocks['ts_code'].values):
        try:
            stock = arbr_result(code, n)
            if stock is not None:
                print(code)
                stocks_p.append(code)
                print("候选股票已添加")
                print(stocks_p)
        except:
            pass
    print(stocks_p)
    stocks_result = pd.DataFrame(stocks_p)
    print(stocks_result)

    # 存储数据
    with open(r'ArBr单.txt', 'w', encoding='utf-8')as f:
        f.write('出现买入信号,BR<40,AR<60: 空方力量较强，但随时可能反转上涨，考虑买进\n')
        stocks_result.to_csv(f, index=False)
    f.close()

    # plot_arbr('上证综指')
    # plot_arbr('上证综指', n=1000)
    # plot_arbr('创业板指', n=250)
    # plot_arbr('沪深300', n=250)
    # plot_arbr('东方电缆', n=210)


if __name__ == "__main__":
    main()
"""
双方的分界线是 100，100 以上是多方优势，100 以下是空方优势。
买入信号：
    BR通常运行在AR上方，一旦BR跌破AR并在AR之下运行时，表明市场开始筑底，视为买进信号；BR<40,AR<60: 空方力量较强，但随时可能反转上涨，考虑买进。
卖出信号：
    BR>400,AR>180，多方力量极强，但随时可能反转下跌，考虑卖出；BR快速上升，AR并未上升而是小幅下降或横盘，视为卖出信号。
背离信号：
AR、BR指标的曲线走势与股价K线图上的走势正好相反。
顶背离：
当股价K线图上的股票走势一峰比一峰高，股价一直向上涨，而AR、BR指标图上的走势却一峰比一峰低，说明出现顶背离，股价短期内将高位反转，是比较强烈的卖出信号。
底背离：
当股价K线图上的股票走势一底比一底低，股价一直向下跌，而AR、BR指标图上的走势却一底比一底高，说明出现底背离，股价短期内将低位反转，是比较强烈的买入信号。
"""
