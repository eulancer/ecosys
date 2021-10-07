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


# 获取最近交易日当日大宗交易数据

def main():
    pro = get_pro_client()
    today = datetime.datetime.now().strftime('%Y%m%d')

    trade_cal = pro.trade_cal()
    while today not in trade_cal[trade_cal['is_open'] == 1]['cal_date'].values:
        today = datetime.datetime.strptime(today, '%Y%m%d').date()
        today = (today + datetime.timedelta(days=-1)).strftime('%Y%m%d')
        print(today)

    print(today)
    df = pro.block_trade(trade_date=today)
    df.sort_values(by='amount', ascending=False, inplace=True)
    print(df)


if __name__ == "__main__":
    main()
