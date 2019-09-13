import time
import tushare
import pandas as pd
from tushare_util import get_pro_client


def get_stock_list():
    pro = get_pro_client()
    # 获取正常上市交易的股票列表，主要用股票代码
    data = pro.stock_basic()
    # 返回一个数据对象，索引列就是股票代码
    return data


def get_stock_hist_data(code, start='2010-01-01',
                        end=time.strftime('%Y-%m-%d', time.localtime())):
    # 获取股票历史数据
    # 调用tushare的get_hist_data()方法
    # 从中选取如下返回值：
    # date: 日期
    # code: 股票代码
    # open: 开盘价
    # high: 最高价
    # close: 收盘价
    # low: 最低价
    pro = get_pro_client()
    data = pro.get_hist_data(code, start, end)
    stock_data = pd.DataFrame(data)

    stock_data.to_sql(name="stock_his_data", con=config.engine, schema="test", index=True, if_exists='append',
                      chunksize=1000)
    """ 
    # 存放数据的列表
    stock_list = []
    # 组合所需元素(日期-股票代码-开盘价-收盘价-最高价-最低价)
    temp = zip(data.index, [code for x in range(len(data.index))], data.open,
               data.close, data.high, data.low)
    for i in temp:
        stock_list.append(i)
    # 默认股票数据是最新日期在前的，想按日期生序排列，倒着返回
    """


def main():
    stock_list = get_stock_list()
    print(stock_list)
    pro = get_pro_client()
    alldays = pro.trade_cal()
    print(alldays)
    #for row in stock_list.iterrows():
        #print(row["symbol"][0])
        # get_stock_hist_data(row["symbol"].values)
    # get_stock_hist_data()


if __name__ == '__main__':
    main()
