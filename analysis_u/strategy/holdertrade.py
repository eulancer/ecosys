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
G高管
P个人
C公司
"""


@logger.catch()
def main():
    pro = get_pro_client()
    today = 20210107
    df = pro.stk_holdertrade(ann_date=today, trade_type='IN', holder_type='G')
    df.sort_values(by='total_share', ascending=False, inplace=True)
    print(df)


if __name__ == "__main__":
    main()
