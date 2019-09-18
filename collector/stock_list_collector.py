# encoding=utf-8
import config
from collector.tushare_util import get_pro_client
import pandas as pd
import sys


# 获取股票基本信息
def get_stock_basic():
    pro = get_pro_client()
    # 获取股票信息
    data = pro.stock_basic(exchange='', list_status='L')
    print(data)
    data = data.fillna('NAN')
    df = pd.DataFrame(data)
    # 存入数据
    df.to_sql(name="stock_basic", con=config.engine, schema=config.db, index=True, if_exists='replace',
              chunksize=1000)
    print("股票基本信息已存入")


def read_stock_basic():
    sql = "SELECT * FROM stock_basic "  # SQL query
    df = pd.read_sql(sql=sql, con=config.engine)  # read data to DataFrame 'df'
    print(df)
    print("股票基本信息已读取")


def main():
    get_stock_basic()
    read_stock_basic()


if __name__ == '__main__':
    main()

"""
# 读取股票嘻嘻
sql = "SELECT * FROM stock_basic "  # SQL query
df = pd.read_sql(sql=sql, con=engine)  # read data to DataFrame 'df'
"""
