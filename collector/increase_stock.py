import datetime

import pandas as pd
from tushare_util import get_pro_client

import config


def increase_stocks(currentday, lastday):
    pro = get_pro_client()
    # 获取当日股票信息
    df1 = pro.daily(trade_date=currentday, start_date=currentday, end_date=currentday)
    dft = pro.daily(trade_date=lastday, start_date=lastday, end_date=lastday)
    # stock列表
    stockList = pd.DataFrame(columns=df1.columns)
    stockList["rate"] = None
    rates = []
    for index, row in df1.iterrows():
        if len(row) > 0:
            ts_codeT = row["ts_code"]
            if len(dft[dft.ts_code == ts_codeT]["vol"]) > 0:
                vol1 = row["vol"]
                vol2 = dft[dft.ts_code == ts_codeT]["vol"].values[0]
                rate = vol1 / vol2
                if rate > 4 and row["pct_chg"] > 0:
                    print(rate)
                    stockList = stockList.append(row)
                    rates.append(rate)
                    stockList["rate"] = rates
    print(stockList)
    # 导出为csv
    stockList.to_csv("std.csv", encoding="gbk", index=False)
    # 存入数据
    stockList.to_sql(name="stock_history", con=config.engine, schema="test", index=True, if_exists='append',
                     chunksize=1000)


def get_recent_two_tradingdates():
    pro = get_pro_client()
    # 获取交易日
    alldays = pro.trade_cal()
    tradingdays = alldays[alldays["is_open"] == 1]  # 开盘日
    today = datetime.datetime.today().strftime('%Y%m%d')
    # 获取最近利康哥交易日
    last_day = today
    last_second_day = ""
    while last_day not in tradingdays["cal_date"].values:
        last_day = last_day - 1
    tradingdays_list = tradingdays["cal_date"].tolist()
    last_day_index = tradingdays_list.index(last_day)
    last_second_day = tradingdays_list[int(last_day_index) - 1]
    recent_two_tradingdates = [last_day, last_second_day]
    return recent_two_tradingdates


def main():
    # 获取最近2个交易日
    days = get_recent_two_tradingdates()
    increase_stocks(days[0], days[1])


if __name__ == "__main__":
    main()
