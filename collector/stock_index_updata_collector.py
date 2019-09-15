import datetime
import config
from collector.tushare_util import get_pro_client
import pandas as pd


# 获取指数
def update_stock_index(ts_code, start_date, end_date):
    pro = get_pro_client()
    df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    print(df)
    # 存入数据
    return df


def main():
    start = '2010101'
    end = '20191001'
    stock_index = ['000001.SH', '000300.SH ', '000905.SH', '399001.SZ ', '399005.SZ ', '399006.SZ ', '399016.SZ',
                   '399300.SZ']
    stock_index_df = pd.DataFrame()
    for x in range(0, len(stock_index)):
        df = update_stock_index(stock_index[x], start, end)
        stock_index_df = stock_index_df.append(df)
    print(stock_index_df)
    stock_index_df.to_sql(name="stock_index", con=config.engine, schema=config.db, index=False, if_exists='replace',
                          chunksize=1000)

    print("指数已更新存入数据库")


if __name__ == "__main__":
    main()
