import datetime
import config
from collector.tushare_util import get_pro_client
import pandas as pd


# 获取上涨放量股票
def update_stocks_data(last_day):
    pro = get_pro_client()
    # 获取当日股票信息
    df = pro.daily(trade_date=last_day, start_date=last_day, end_date=last_day)
    # 存入数据
    df.to_sql(name="stock_his_data", con=config.engine, schema="test", index=True, if_exists='append',
              chunksize=1000)
    up_data = {"up_date": last_day}
    df_update = pd.DataFrame(up_data)
    df_update.to_sql(name="stock_history_update", con=config.engine, schema="test", index=True, if_exists='append')


# 获取交易日
def get_recent_trading_date():
    pro = get_pro_client()
    # 获取交易日
    alldays = pro.trade_cal()
    #print(alldays)
    tradingdays = alldays[alldays["is_open"] == 1]  # 开盘日
    today = datetime.datetime.today().strftime('%Y%m%d')
    last_day = today
    # 如果当天不是交易日，时间往前提
    i = 0
    while last_day not in tradingdays["cal_date"].values:
        i = i + 1
        last_day = datetime.datetime.today() + datetime.timedelta(days=-i)
        last_day = last_day.strftime('%Y%m%d')
        #print(last_day)
    return last_day


# 验证数据是否更新
def check_the_update(last_day):
    sql_cmd = "SELECT * FROM stock_history_update"
    df = pd.read_sql(sql=sql_cmd, con=config.engine)
    if last_day in df["up_date"].values:
        print("数据已更新")
    return last_day in df["up_date"].values


def main():
    print("开始更新")
    last_day = get_recent_trading_date()
    if not check_the_update(last_day):
        update_stocks_data(last_day)
        print("正在更新"+last_day+"数据")


if __name__ == "__main__":
    main()
