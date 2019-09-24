import pandas as pd
import numpy as np
import lib.BGI as BGI
from collector.tushare_util import get_pro_client


def main():
    pro = get_pro_client()
    quotes_daily = pro.weekly(trade_date='20181123', fields='ts_code,trade_date,open,high,low,close,vol,amount')
    quotes_daily.index = map(lambda x: x.replace('-', ''), quotes_daily.index)
    quotes_weekly = BGI.daily2weekly(quotes_daily, 'sum')  # 周度行情
    quotes_weekly.plot(figsize=(12, 5))


if __name__ == '__main__':
    main()
