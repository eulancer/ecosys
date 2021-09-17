# 先引入后面可能用到的包（package）
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
# 引入TA-Lib库
import talib as ta
from strategy.tushare_util import get_pro_client
from strategy.tushare_util import get_all_code_df
from datetime import datetime, timedelta
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
    # df = pro.stock_basic(exchange='', list_status='L')
    # 获取数据时间
    t = datetime.now()
    t0 = t - timedelta(n)
    start = t0.strftime('%Y%m%d')
    end = t.strftime('%Y%m%d')
    # 如果代码在字典index里，则取的是指数数据
    if code in index.values():
        df = pro.index_daily(ts_code=code, start_date=start, end_date=end)
    # 否则取的是个股数据
    else:
        df = pro.daily(ts_code=code, start_date=start, end_date=end)
    # 将交易日期设置为索引值
    df.index = pd.to_datetime(df.trade_date)
    df = df.sort_index()
    # 计算收益率

    return df


# 计算AR、BR指标
def arbr(code, n):
    # stocks = get_all_code_df()
    # code = stocks[stocks['name'] == name]['ts_code'].iat[0]
    print(code)
    # print(name)

    df = get_data(code, n)[['open', 'high', 'low', 'close']]
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
    return df[['close', 'AR', 'BR']].dropna()


# 买入信号：BR通常运行在AR上方，一旦BR跌破AR并在AR之下运行时，表明市场开始筑底，视为买进信号；BR<40,AR<60: 空方力量较强，但随时可能反转上涨，考虑买进。

# 判断买入股票
def arbr_result(code, n):
    df = arbr(code, n)
    if df['AR'].iat[0] > df['BR'].iat[0] and df['BR'].iat[0] < 100:
        # print('AR')
        # print(df['AR'].iat[0])
        # print('BR')
        # print(df['BR'].iat[0])
        print('出现买入信号,BR运行在AR下方')
        # stocks_p.append(stock)
    if df['AR'].iat[0] < 50 and df['BR'].iat[0] < 40:
        print('出现买入信号,BR<40,AR<50: 空方力量较强，但随时可能反转上涨，考虑买进')
        print(code)
        return code


# 对价格和ARBR进行可视化
def plot_arbr(stock, n=120):
    df = arbr(stock, n)
    df['close'].plot(color='r', figsize=(14, 5))
    plt.xlabel('')
    plt.title(stock + '价格走势', fontsize=15)
    df[['AR', 'BR']].plot(figsize=(14, 5))
    plt.xlabel('')
    plt.show()


def main():
    stocks = get_all_code_df()
    print(stocks)
    stocks_p = []
    for code in tqdm(stocks['ts_code'].values):
        try:
            stock = arbr_result(code, 120)
            stocks_s = stocks_p.append(stock)
        except:
            pass

    stocks_result = pd.DataFrame(stocks_s)
    print(stocks_result)
    with open(r'ArBR单.txt', 'w', encoding='utf-8')as f:
        f.write('股东小于4万市值小于200亿股东下降了15%以上非新股非ST名单\n')
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
