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


def get_stock_forcast_data(code, period):
    pro = get_pro_client()
    stock_forcast_data = pro.forecast(ts_code=code, period=period,
                                      fields='ts_code,ann_date,end_date,type,p_change_min,p_change_max,net_profit_min')
    # print(stock_forcast_data)

    stock_forcast_increase = []
    if len(stock_forcast_data['type']) > 0:
        print(stock_forcast_data['ts_code'][0] + stock_forcast_data['type'][0])
        if stock_forcast_data['type'][0] == '预增':
            stock_forcast_increase = stock_forcast_data
            stock_hold.append(stock_forcast_data)
            print(stock_forcast_data)
    return stock_forcast_increase


def main():
    stock_list = pd.DataFrame(get_stock_list())
    ann_date = '20190731'
    period = '20190930'
    i = 0
    for index, row in stock_list.iterrows():
        i += 1
        get_stock_forcast_data(row["ts_code"], period)
        print(i)
        time.sleep(0.2)
    print("下载结束")
    stock_hold.to_sql(name="stock_forecast", con=config.engine, schema=config.db, index=False, if_exists='append',
                      chunksize=1000)


if __name__ == '__main__':
    main()
