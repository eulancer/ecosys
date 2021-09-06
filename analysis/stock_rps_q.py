import datetime
import pandas as pd
import config
from analysis import stock_rps

from scipy.constants import day


# 从数据库中获取复权价格和成交量

def get_price_vol_data():
    now = datetime.datetime.now()
    date = (now - datetime.timedelta(days=180)).strftime('%Y%m%d')
    sql = f'select * from stock_his_data where trade_date>{date}'
    print(sql)
    all_data = pd.read_sql(sql, config.engine)
    all_data = all_data.sort_values(['ts_code', 'trade_date'])
    print("all_data")
    codes = list(all_data.ts_code.unique())
    """
    # 前复权
    all_data['adjclose'] = all_data.groupby('ts_code').apply(
        lambda x: x.close * x.adj_factor / x.adj_factor.iloc[-1]).values
    all_data['adjvol'] = all_data.groupby('ts_code').apply(
        lambda x: x.vol * x.adj_factor / x.adj_factor.iloc[-1]).values
    all_data['adjopen'] = all_data.groupby('ts_code').apply(
        lambda x: x.open * x.adj_factor / x.adj_factor.iloc[-1]).values
    all_data['adjhigh'] = all_data.groupby('ts_code').apply(
        lambda x: x.high * x.adj_factor / x.adj_factor.iloc[-1]).values
    all_data['adjlow'] = all_data.groupby('ts_code').apply(
        lambda x: x.low * x.adj_factor / x.adj_factor.iloc[-1]).values
    """
    # print(all_data.groupby('ts_code')['close'])
    all_data['adjclose'] = all_data['close']
    all_data['adjvol'] = all_data['vol']
    all_data['adjopen'] = all_data['open']
    all_data['adjhigh'] = all_data['high']
    all_data['adjlow'] = all_data['low']
    # 设置索引
    all_data = all_data.set_index(['trade_date', 'ts_code'])[['adjclose', 'adjvol', 'adjopen', 'adjhigh', 'adjlow']]
    # 转成面板数据
    all_data = all_data.unstack()
    return codes, all_data


# 筛选价格和成交量突破N日阈值的个股

def find_price_vol_stock(n, r=1.2):
    codes, all_data = get_price_vol_data()
    print(codes)
    up_list = []
    print(all_data.count())
    b = 0
    for code in codes:
        close = all_data['adjclose'][code]
        open_ = all_data['adjopen'][code]
        high = all_data['adjhigh'][code]
        low = all_data['adjlow'][code]
        vol = all_data['adjvol'][code]
        # 剔除一字涨停
        flag = True
        if close.iloc[-1] == open_.iloc[-1] == high.iloc[-1] == low.iloc[-1]:
            print(close.iloc[-1])
            flag = False
            break
        # 最近五日没有长上影线,以单日回撤3%为长上影线
        for i in range(5):
            if close[-5:][i] * 1.03 < high[-5:][i]:
                flag = False
                break
        # 价格突破前N日新高
        p = close.iloc[-1]  # 当前价格
        p0 = close[-n:-1].min()
        p1 = close[-n:-1].max()  # 前n-1日最高价
        print(p1)
        # 价格短期已上涨超过50%，涨幅过大不宜介入
        '''
        if (p-p0)/p0>r:
            flag=False
            break '''
        # 价格突破且放量上涨
        if flag == True and \
                p1 < p < p1 * r and \
                vol[-5:].mean() / vol[-10:-5].mean() > 2.0:
            up_list.append(code)
        print(up_list)
    return up_list


# 剔除了次新股和ST股后对剩下的2871只股票进行筛选。
def find_stock(data, n=20):
    stock_list = []
    for c in data.columns:
        d0 = data[c][-n]
        d1 = data[c][-(n - 2):-1].max()
        d2 = data[c][-1]
        # 考虑股价在3-20元个股情况
        stock_list.append(c)
        """
        if 3 < d2 < 20 and d1 < d0 < d2 < d0 * 1.52:
            stock_list.append(c)
        """
    # print(len(stock_list))
    return stock_list


def main():
    stocks_60 = find_price_vol_stock(60)
    print(stocks_60)
    print('突破60日量价的个股为：\n')
    # print(stocks_60)
    print(f'突破60日量价个股个数为：{len(stocks_60)}')
    # data = stock_rps.read_data()
    # data.tail()
    # ss_20 = find_stock(data)
    # print(ss_20)


if __name__ == "__main__":
    main()
