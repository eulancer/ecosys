import time
import tushare
import pandas as pd
from collector.tushare_util import get_pro_client


def get_stock_list():
    pro = get_pro_client()
    # 获取正常上市交易的股票列表，主要用股票代码
    df = pro.hk_daily(trade_date='20190913')
    print(df)

    return df


def main():
    get_stock_list()


if __name__ == '__main__':
    main()
