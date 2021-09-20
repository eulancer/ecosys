import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import CHAR, INT


class DB(object):
    connect_info = 'mysql+pymysql://root@host:3306/test?charset=utf8'

    def __init__(self):
        self.pd = pd.DataFrame()
        return self

    def connect(self):
        engine = create_engine(self.connect_info)  # use sqlalchemy to build link-engine
        con = engine.connect()
        return con

    def stock_to_read(self, sql):
        engine = self.connect()
        df = pd.read_sql(sql=sql, con=engine)  # read data to DataFrame 'df'
        return df

    def stock_to_sql(self, db):
        engine = self.connect()
        # write df to table 'test1'
        table = "test"
        db.to_sql(name=table,
                  con=engine,
                  if_exists='append',
                  index=False,
                  )

    if __name__ == '__main__':
        print("main")
