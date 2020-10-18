# encoding=utf-8
from collector.tushare_util import get_pro_client
import time
import pandas as pd
import config

stock_hold = pd.DataFrame()


def get_stock_list():
    pro = get_pro_client()
    # 获取正常上市交易的股票列表，主要用股票代码
    data = pro.stock_basic()
    # 返回一个数据对象，索引列就是股票代码
    return data


def get_stock_forcast_data(period):
    pro = get_pro_client()
    stock_holds = pd.DataFrame()
    stock_list = pd.DataFrame(get_stock_list())
    i = 0
    for index, row in stock_list.iterrows():
        i = i + 1
        print(i)
        stock_forecast_data = pro.forecast(ts_code=row["ts_code"], period=period)
        if len(stock_forecast_data['type']) > 0:
            print(stock_forecast_data['ts_code'][0] + stock_forecast_data['type'][0])
            if stock_forecast_data['type'][0] == '预增':
                print(type(stock_forecast_data))
                # 合并预增的数组
                stock_holds = pd.concat([stock_holds, stock_forecast_data])
                print(stock_holds)
                # break
        time.sleep(0.2)
    stock_holds.to_sql(name="stock_forecast", con=config.engine, schema=config.db, index=False, if_exists='append')


def main():
    ann_date = '20190731'
    period = '20190930'
    read()
    print("下载结束")


def read():
    sql = "SELECT * FROM stock_forecast "  # SQL query
    df = pd.read_sql(sql=sql, con=config.engine)  # read data to DataFrame 'df'
    df.to_csv("cs.csv", encoding="GBk")
    print(df)


if __name__ == '__main__':
    main()
