import akshare as ak
import pandas as pd

"""
避免打印时出现省略号
"""
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)


def main():
    stock__df = ak.stock_dzjy_mrmx(symbol='A股', start_date='2021-11-12', end_date='2021-11-12')
    stock__df.sort_values(by='成交额', ascending=False, inplace=True)
    print(stock__df)

    # stock__df_result = stock__df[(stock__df['成交价'] > stock__df['收盘价'])]
    # print(stock__df_result)

    stock__df_result_O = stock__df[stock__df['买方营业部'] == '机构专用']

    print(stock__df_result_O)


if __name__ == "__main__":
    main()
