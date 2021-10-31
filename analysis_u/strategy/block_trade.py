import datetime
from analysis_u.strategy.tushare_util import get_pro_client
import pandas as pd

"""
避免打印时出现省略号
"""
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

"""
# 获取最近交易日当日大宗交易数据
"""


def main():
    pro = get_pro_client()
    today = 20211029
    """
    today = datetime.datetime.now().strftime('%Y%m%d')

    # 获取交易数据
    trade_cal = pro.trade_cal()
    while today not in trade_cal[trade_cal['is_open'] == 1]['cal_date'].values:
        today = datetime.datetime.strptime(today, '%Y%m%d').date()
        today = (today + datetime.timedelta(days=-1)).strftime('%Y%m%d')
    """

    df_block = pro.block_trade(trade_date=today)
    df_block.sort_values(by='amount', ascending=False, inplace=True)
    print(df_block)

    df_daily = pro.daily(trade_date=today)
    print(df_daily)
    df_result = pd.merge(df_block, df_daily, how='left', on=['ts_code', 'trade_date'])
    print(df_result)

    df_result_stock = df_result[df_result['price'] > df_result['close']]
    df_result_stock.sort_values(by='amount_x', ascending=False, inplace=True)
    print(df_result_stock[['ts_code', 'trade_date', 'price', 'vol_x', 'amount_x', 'close', 'buyer']])

    df_result_O = df_result[df_result['buyer'] == '机构专用']
    df_result_O.sort_values(by='amount_x', ascending=False, inplace=True)
    print(df_result_O[['ts_code', 'trade_date', 'price', 'vol_x', 'amount_x', 'close', 'buyer']])


if __name__ == "__main__":
    main()
