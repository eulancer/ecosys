from datetime import datetime

import tushare
import config


# tushare连接方式
def get_pro_client():
    return tushare.pro_api(config.tushare_token)


def get_ts_code(stock_number):
    for i in config.ts_code_pattern:
        for n in i.get('pattern'):
            if stock_number.startswith(n):
                return stock_number + i.get('code_postfix')


def get_all_code():
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    # 去除ST股票
    df = df[~df.name.str.contains('ST')]
    # 去除2020101以后的新股
    df['list_date'] = df['list_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
    df = df[(df['list_date'] < datetime(2021, 1, 1))]

    codes = df.ts_code.values
    names = df.name.values
    stock = dict(zip(names, codes))
    return stock
