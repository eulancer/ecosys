import tushare as ts
import datetime
from tushare_util import get_pro_client

pro = get_pro_client()
alldays = pro .trade_cal()
print(alldays)

tradingdays = alldays[alldays["is_open"] == 1]  # 开盘日

today = datetime.datetime.today().strftime('%Y%m%d')
print(today)
if today in tradingdays["cal_date"].values:
   tradingdays_list = tradingdays["cal_date"].tolist()
   today_index = tradingdays_list.index(today)
   last_day = tradingdays_list[int(today_index) - 1]
   print(last_day)
