from collector.tushare_util import get_pro_client
import datetime
import pandas as pd
from dateutil.parser import parse
import time


# 获取每天股票交易数据

def get_today_all_ts():
    # date_now = date
    pro = get_pro_client()
    # 先获得所有股票的收盘数据
    df_close = pro.daily(trade_date='20200918')
    # 获得所有股票的基本信息
    df_daily = pro.daily_basic(ts_code='', trade_date='20200918',
                               fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb')
    # 获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
    df_data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    df_all = pd.merge(df_close, df_daily)
    df_all = pd.merge(df_all, df_data)
    # print(df_all['list_date'])
    df_all['list_date'] = pd.to_datetime(df_all['list_date'])
    print(df_all['list_date'])


def main():
    pro = get_pro_client()
    # 先获得所有股票的收盘数据
    df_close = pro.daily_basic(trade_date='20200918')
    print(df_close)


if __name__ == "__main__":
    main()
