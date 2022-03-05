# encoding=utf-8
import tushare as ts
# import MySQLdb
import pandas as p
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

tushare_token = '1b61e563de958fab5733a11103409224a50673ca4857b20b1669b016'
# engine = create_engine('mysql+pymysql://root@127.0.0.1:3306/stock_trade?charset=utf8')
host = '127.0.0.1'
port = 3306
db = 'stock_trade'
user = 'root'
password = ''
unicode = 'utf8'
Ne_path = '//Ne.txt'

#  邮件名单
email_list = ['lingssh@126.com', 'tokttt@gmail.com']
