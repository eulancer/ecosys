import akshare as ak
import pandas as pd

"""
避免打印时出现省略号
"""
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)
pd.set_option('display.max_rows', None)


def main():
    stock_dzjy_mrtj_df = ak.stock_dzjy_mrtj(start_date='2021-11-16', end_date='2021-11-16')
    print(stock_dzjy_mrtj_df[['证券代码', '证券简称', '收盘价', '成交均价', '成交总额']])
    df_result_stock = stock_dzjy_mrtj_df[stock_dzjy_mrtj_df['成交均价'] > stock_dzjy_mrtj_df['收盘价']]
    df_result_stock.sort_values(by='成交总额', ascending=False, inplace=True)
    print(df_result_stock[['证券代码', '证券简称', '收盘价', '成交均价', '成交总额']])


if __name__ == "__main__":
    main()
