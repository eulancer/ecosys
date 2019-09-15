import tushare as ts
import MySQLdb
import pandas as p
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import pymysql
from sqlalchemy.orm import sessionmaker
import pymysql
import config
from collector.tushare_util import get_pro_client

ts.set_token('1b61e563de958fab5733a11103409224a50673ca4857b20b1669b016')

engine = create_engine('mysql+pymysql://root@127.0.0.1:3306/test?charset=utf8')
host = '127.0.0.1'
port = 3306
db = 'test'
user = 'root'
password = ''


def main():
    ts.get_hist_data('600848')
    # ts.get_stock_basics()
    # ts.get_cpi()
    # pro = ts.pro_api()
    # data_frame = ts.get_hist_data('600848',start='2016-01-01',end='2016-02-01')

    con = engine.connect()  # 创建连接
    df = ts.get_hist_data('600848')
    df.to_sql(name='hist_data', con=con, if_exists='append', index=False)
    # print(ts.get_cpi())
    print(ts.get_hist_data('600848'))
    # Session = sessionmaker(bind=engine)


def read_data():
    pro = get_pro_client()
    # 获取当日股票信息
    start = '2010101'
    end = '20191001'
    df = pro.index_dailybasic(ts_code='000001.SH',start_date='20010101', end_date='20191018')
    print(df)


if __name__ == '__main__':
    read_data()
