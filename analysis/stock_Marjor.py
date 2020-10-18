from collector.tushare_util import get_pro_client
import datetime
import pandas as pd
from dateutil.parser import parse
import time


# 获取盘面信息，对整体盘面做个评估，后续可对版本进行评估

# 获取所有股票信息
def get_stockData(trade_date):
    trade_date = trade_date
    pro = get_pro_client()
    # 先获得所有股票的收盘数据
    df_close = pro.daily(trade_date=trade_date)
    # 获得所有股票的基本信息
    df_daily = pro.daily_basic(trade_date=trade_date)
    # 获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
    df_data = pro.stock_basic()
    df_all = pd.merge(df_close, df_daily)
    df_all = pd.merge(df_all, df_data)
    # print(df_all['list_date'])
    df_all['list_date'] = pd.to_datetime(df_all['list_date'])
    return df_all


# 获取市值小于在多少之间的股票

def get_stocks_Value(down, up, trade_date):
    df_all = get_stockData(trade_date)
    print(df_all[df_all['total_mv'] < up])


def get_statics(trade_date):
    date_now = trade_date
    df_all = get_stockData(date_now)

    # 添加 交易所 列
    # 找出上涨的股票
    df_up = df_all[df_all['pct_chg'] > 0]

    # 走平股数
    df_even = df_all[df_all['pct_chg'] == 0]
    # 找出下跌的股票
    df_down = df_all[df_all['pct_chg'] < 0]
    # 找出下跌的股票

    # 找出涨停的股票
    limit_up = df_all[df_all['pct_chg'] >= 9.7]
    limit_down = df_all[df_all['pct_chg'] <= -9.7]

    # 涨停股数中的未封板股，上市日期小于15天
    limit_up_new = limit_up[pd.to_datetime(date_now) - limit_up['list_date'] <= pd.Timedelta(days=15)]

    # 涨停股数中次新股，上市日期小于1年
    limit_up_fresh = limit_up[pd.to_datetime(date_now) - limit_up['list_date'] <= pd.Timedelta(days=365)]

    # 涨停股数中的未封板股，上市日期小于15天
    limit_down_new = limit_down[pd.to_datetime(date_now) - limit_down['list_date'] <= pd.Timedelta(days=15)]
    # 涨停股数中次新股，上市日期小于1年
    limit_down_fresh = limit_down[pd.to_datetime(date_now) - limit_down['list_date'] <= pd.Timedelta(days=365)]

    print('A股上涨个数： %d, A股下跌个数： %d, A股走平个数: %d。' % (df_up.shape[0], df_down.shape[0], df_even.shape[0]))
    print('A股总成交额：%d, 总成交量：%d' % (df_all['amount'].sum(), df_all['vol'].sum()))
    print('A股平均市盈率：%.2f， 平均流通市值 %.2f 亿, 平均总市值 %.2f 亿' % (
        df_all['pe'].mean(), df_all['circ_mv'].mean(), df_all['total_mv'].mean()))
    print('涨停数量：%d 个, 涨停中上市日期小于15天的：%d, 涨停中上市日期小于1年的：%d' % (
        limit_up.shape[0], limit_up_new.shape[0], limit_up_fresh.shape[0]))
    print('跌停数量：%d 个, 跌停中上市日期小于15天的：%d, 跌停中上市日期小于1年的：%d' % (
        limit_down.shape[0], limit_down_new.shape[0], limit_down_fresh.shape[0]))

    # 获取指定列的分析统计结果
    for i in ['industry', 'area']:
        # 对涨停的股票分析
        output_limit_up = get_output(limit_up, columns=i, name='limit_up')
        print(output_limit_up)
        # 对跌停的股票分析
        output_limit_down = get_output(limit_down, columns=i, name='limit_down')
        print(output_limit_down)
        # 对全量的股票分析
        output_total = get_output(df_all, columns=i, name='total')
        print(output_total)


def get_output(df, columns='industry', name='_limit_up'):
    df = df.copy()
    output = pd.DataFrame()
    output = pd.DataFrame(df.groupby(columns)['ts_code'].count())
    output['pe_mean'] = df.groupby(columns)['pe'].mean()
    output['pe_median'] = df.groupby(columns)['pe'].median()

    output['circ_mv_mean'] = df.groupby(columns)['circ_mv'].mean()
    output['circ_mv_median'] = df.groupby(columns)['circ_mv'].median()

    output['total_mv'] = df.groupby(columns)['total_mv'].mean()
    output['total_mv_median'] = df.groupby(columns)['total_mv'].median()

    output['vol_mean'] = df.groupby(columns)['vol'].mean()
    output['vol_median'] = df.groupby(columns)['vol'].median()

    output['amount_mean'] = df.groupby(columns)['amount'].mean()
    output['amount_median'] = df.groupby(columns)['amount'].median()

    output.sort_values('ts_code', ascending=False, inplace=True)
    output.rename(columns={'ts_code': name + '_count'}, inplace=True)
    return output


# 获取市值小于在多少之间的股票

def get_stocks_Value(down, up, trade_date):
    df_all = get_stockData(trade_date)
    print(df_all)
    df = df_all['total_mv'] < 300000
    # print("~~~~~~~~~~~~~~")
    # print(df_all[df_all['total_mv'] < 100000])
    print("~~~~~~~~~~~~~~")
    print(df_all[(df_all['total_mv'] > 100000) & (df_all['total_mv'] < 150000)])


# 业绩增长的股票
def get_stock_increase(ts_code):
    pro = get_pro_client()
    print(pro.forecast(ts_code='002891.SZ'))


def main():
    pro = get_pro_client()
    trade_date = pro.trade_cal()
    today = datetime.date.today()
    print(today)
    date_ex = today.strftime('%Y%m%d')
    get_statics("20201016")
    # get_stocks_Value(0, 30, 20200923)
    # get_stock_increase()


if __name__ == "__main__":
    main()
