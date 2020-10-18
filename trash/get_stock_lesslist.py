import time
import tushare
import pandas as pd
from collector.tushare_util import get_pro_client
import config


def get_stock_list():
    pro = get_pro_client()
    # 获取正常上市交易的股票列表，主要用股票代码
    data = pro.stock_basic()
    # 返回一个数据对象，索引列就是股票代码
    return data


def get_stock_number_data(code, start, end):
    pro = get_pro_client()
    start = start
    end = end
    data = pro.stk_holdernumber(ts_code=code, start_date=start, end_date=end)
    stock_data = pd.DataFrame(data)
    print(stock_data['holder_num'][0])
    stock_data.to_sql(name="stock_number_data", con=config.engine, schema=config.db, index=True,
                      if_exists='append', chunksize=1000)
    print(code + "已存入mysql")


def main():
    stock_list = pd.DataFrame(get_stock_list())
    start = '20190901'
    end = '20191212'
    for index, row in stock_list.iterrows():
        if index > 3697:
            get_stock_number_data(row["ts_code"], start, end)
            print(index)
            time.sleep(0.1)
    print("下载结束")


if __name__ == '__main__':
    main()
