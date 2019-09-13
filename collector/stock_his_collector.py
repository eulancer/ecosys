import tushare as ts
from tushare_util import get_pro_client
import pandas as pd

import config


def get_5min_tick(code):
    pro = get_pro_client()
    return pro.get_k_data(code, ktype='5')


def main():
    pro = get_pro_client()
    stock_list = pro.stock_basic()
    print(stock_list)
    stock_his_data = pd.DataFrame()
    for code, info in stock_list.iterrows():
        for i in range(5):
            try:
                # stock_his_data = get_5min_tick(code)
            finally:
                print("Error: 没有找到文件或读取文件失败")
        stock_his_data.to_sql(name="stock_his_all", con=config.engine, schema="test", index=True, if_exists='append',
                              chunksize=1000)


if __name__ == '__main__':
    main()
