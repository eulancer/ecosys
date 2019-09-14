import datetime
import config
from collector.tushare_util import get_pro_client


# 获取上涨放量股票
def update_stocks_data(last_day):
    pro = get_pro_client()
    # 获取当日股票信息
    df = pro.daily(trade_date=last_day, start_date=last_day, end_date=last_day)
    # 存入数据
    df.to_sql(name="stock_his_data", con=config.engine, schema="test", index=True, if_exists='append',
              chunksize=1000)


# 获取交易日
def get_recent_tradingdate():
    pro = get_pro_client()
    # 获取交易日
    alldays = pro.trade_cal()
    # print(alldays)
    tradingdays = alldays[alldays["is_open"] == 1]  # 开盘日
    today = datetime.datetime.today().strftime('%Y%m%d')
    last_day = today
    # 如果当天不是交易日，时间往前提
    i = 0
    while last_day not in tradingdays["cal_date"].values:
        i = +1
        last_day = datetime.datetime.today() - datetime.timedelta(days=-i)
        last_day = last_day.strftime('%Y%m%d')
    return last_day


def check_the_update(last_day):
    print("shuju")


def main():
    # 获取最近2个交易日
    last_day = get_recent_tradingdate()
    print(last_day)
    # update_stocks_data(last_day)


if __name__ == "__main__":
    main()
