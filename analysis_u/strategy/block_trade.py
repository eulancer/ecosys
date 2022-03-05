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
    '''
    today = datetime.datetime.now().strftime('%Y%m%d')

    trade_cal = pro.trade_cal()
    while today not in trade_cal[trade_cal['is_open'] == 1]['cal_date'].values:
        today = datetime.datetime.strptime(today, '%Y%m%d').date()
        today = (today + datetime.timedelta(days=-1)).strftime('%Y%m%d')
        print(today)

    print(today)
    '''
    today = 20220304
    df_block = pro.block_trade(trade_date=today)
    print(df_block)
    # df_block.sort_values(by='amount', ascending=False, inplace=True)

    df_daily = pro.daily(trade_date=today)
    print(df_daily)
    df_result = pd.merge(df_block, df_daily, how='left', on=['ts_code', 'trade_date'])

    df_result_stock_org = df_result[(df_result['buyer'] == '机构专用')].copy()
    df_result_stock_org.sort_values(by='amount_x', ascending=False, inplace=True)
    print('机构专用')
    print(df_result_stock_org[['ts_code', 'trade_date', 'price', 'close', 'vol_x', 'amount_x', 'buyer', 'seller']])

    df_result_stock_price = df_result[(df_result['price'] > df_result['close'])].copy()
    df_result_stock_price.sort_values(by='amount_x', ascending=False, inplace=True)
    print('溢价')
    print(df_result_stock_price[['ts_code', 'trade_date', 'price', 'close', 'vol_x', 'amount_x', 'buyer', 'seller']])

    df_result_stock = df_result[(df_result['buyer'] == '机构专用') & (df_result['price'] >= df_result['close'])].copy()
    df_result_stock.sort_values(by=['ts_code', 'amount_x'], ascending=(False, False),
                                inplace=True)
    print('溢价及机构')
    print(df_result_stock[['ts_code', 'trade_date', 'price', 'close', 'vol_x', 'amount_x', 'buyer', 'seller']])

    stock_list = df_result_stock['ts_code'].values
    stock_list = list(set(stock_list))

    print(stock_list)
    '''
    # 取某日
    df = pro.repurchase(ann_date='2021108')
    print(df)
    '''


if __name__ == "__main__":
    main()