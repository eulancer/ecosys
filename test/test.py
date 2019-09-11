import tushare as ts
import MySQLdb
import pandas as p
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ts.set_token('1b61e563de958fab5733a11103409224a50673ca4857b20b1669b016')

engine = create_engine('mysql+pymysql://root@127.0.0.1:3306/test?charset=utf8')
host = '127.0.0.1'
port = 3306
db = 'test'
user = 'root'
password = ''

def main():
    ts.get_hist_data('600848')
    #ts.get_stock_basics()
    #ts.get_cpi()
    #pro = ts.pro_api()
    #data_frame = ts.get_hist_data('600848',start='2016-01-01',end='2016-02-01')

    con = engine.connect()  # 创建连接
    df = ts.get_hist_data('600848')
    df.to_sql(name='hist_data', con=con, if_exists='append', index=False)
    #print(ts.get_cpi())
    print(ts.get_hist_data('600848'))
    #Session = sessionmaker(bind=engine)

def read_data():
    sql = ' select * from hist_data; '
    # read_sql_query的两个参数: sql语句， 数据库连接
    dh = p.read_sql_query(sql, engine)
    print(dh)

if __name__ == '__main__':
    read_data()