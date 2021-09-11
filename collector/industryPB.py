from tqdm import tqdm

from collector.tushare_util import get_pro_client
import pandas as pd

"""
# 构建各行业的最低值矩阵
# 获取各行业符合要求的股票
# 获取所有行业股票清单
# 获取股票PB
"""


#  获取各行业符合要求的股票
def get_candidates(trade_date, IndustryPE):
    j = 0
    for industry in IndustryPE['行业']:
        get_candidate_stock(industry, trade_date, IndustryPE['最低PB'][j])
        j = j + 1


# 获取股票清单
def get_candidate_stock(industry, trade_date, Low_pb):
    stocks = get_stock(industry)
    stocks_p = []
    i = 0
    # 证券股的PB小于1.3 可以考虑买入
    # tqdm 按进度条显示
    print("~~~~~~~~~~~~~~~~~" + str(industry) + "~~~~~~~~~~~~~~~~~")
    for code in tqdm(stocks['ts_code'].values):
        try:
            if get_PB(code, trade_date)['pb'][0] < Low_pb:
                stocks_p.append(code)
                print("该代码放入股票池 ")
                print(stocks[stocks['ts_code'] == code].values[0])
            else:
                print("不符合条件")
        except Exception as re:
            print(re)

    # 按照PB值排序
    df = pd.DataFrame()
    try:
        for code in stocks_p:
            df = df.append(get_PB(code, trade_date))
    except Exception as re:
        print(re)
    # 按照列值排序
    df.sort_values("pb", inplace=True)

    # 获取股票名称
    pro = get_pro_client()
    df_stock_basic = pro.stock_basic()
    df = pd.merge(df_stock_basic[['ts_code', 'name']], df, how='inner', on='ts_code')

    print("符合要求的股票")
    print(df)
    # 到处文件
    """"
       with open('D:/Work/git/ecosys/data/holder70.txt', 'w') as f:
           for i in stocks_p:
               f.write(i)
       f.close()
    """


# 获取所有行业股票清单
def get_stock(industry):
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    stocks = df[df['industry'] == industry]

    return stocks[['ts_code', 'name']]


# 获取PB
def get_PB(code, trade_date):
    pro = get_pro_client()
    df = pro.daily_basic(ts_code=code, trade_date=trade_date,
                         fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb')
    return df


def main():
    trade_date = '20210910'
    # 构建各行业的最低值矩阵
    IndustryPE = {'行业': ['银行', '保险', '证券'],
                  '最低PB': [0.8, 0.8, 1.2]}
    # 显示所有行业
    get_candidates(trade_date, IndustryPE)


if __name__ == "__main__":
    main()
