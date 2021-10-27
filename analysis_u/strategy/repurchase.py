import datetime
from analysis_u.strategy.tushare_util import get_pro_client
import pandas as pd
from loguru import logger

"""
避免打印时出现省略号
"""
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

"""
# 获取最近交易日当日大宗交易数据
"""


@logger.catch()
def main():
    pro = get_pro_client()
    today = 20211027
    """
    today = datetime.datetime.now().strftime('%Y%m%d')

    # 获取交易数据
    trade_cal = pro.trade_cal()
    while today not in trade_cal[trade_cal['is_open'] == 1]['cal_date'].values:
        today = datetime.datetime.strptime(today, '%Y%m%d').date()
        today = (today + datetime.timedelta(days=-1)).strftime('%Y%m%d')
    """

    Repurchase = pro.repurchase(ann_date=today)
    Repurchase.sort_values(by='amount', ascending=False, inplace=True)
    print(Repurchase)


if __name__ == "__main__":
    main()
