import tushare as ts
from sqlalchemy import create_engine
import pandas as pd

ts.set_token('1b61e563de958fab5733a11103409224a50673ca4857b20b1669b016')
pro = ts.pro_api()

connect_info = 'mysql+pymysql://root@127.0.0.1:3306/test?charset=utf8'
engine = create_engine(connect_info)  # use sqlalchemy to build link-engine

# 存储取所有股票信息
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
ds = pd.DataFrame(data)
ds.to_sql(name="stock_basic", con=engine, schema="test", index=True, if_exists='replace', chunksize=1000)

# 读取股票嘻嘻
sql = "SELECT * FROM stock_basic "  # SQL query
df = pd.read_sql(sql=sql, con=engine)  # read data to DataFrame 'df'

if __name__ == '__main__':
    print(df)
