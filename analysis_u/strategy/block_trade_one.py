import datetime
from tqdm import tqdm
from analysis_u.strategy.tushare_util import get_pro_client
from analysis_u.strategy.tushare_util import get_all_code
import numpy as np
import pandas as pd
import time

"""
避免打印时出现省略号
"""
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)


# 获取最近交易某个股票大宗交易数据

def main():
    pro = get_pro_client()

    stock = '600733.SH'
    end_day = datetime.date(2022, 3, 4)
    start_day = datetime.date(2021, 10, 4)
    delta = datetime.timedelta(days=1)
    d = start_day
    while d <= end_day:
        df_block = pro.block_trade(ts_code=stock, trade_date=d.strftime('%Y%m%d'))
        if df_block.empty:
            pass
        else:
            print(df_block)
        d += delta


if __name__ == "__main__":
    main()
