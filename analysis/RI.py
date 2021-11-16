import tushare as ts
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import talib as tb

today = datetime.datetime.today().strftime('%Y%m%d')    #获取今天的年月日
lastday = datetime.datetime.today() - datetime.timedelta(days=1)  #获取前一天数据
lastday = lastday.strftime('%Y%m%d')
last_year = datetime.datetime.today() - relativedelta(months=12)   #获取前一年的日期
last_year = last_year.strftime('%Y%m%d')   # 转换成STR
Lastweek = datetime.datetime.today() - datetime.timedelta(days=7)   #获取前一周的日期
Lastweek = Lastweek.strftime('%Y%m%d')    # 转换成STR
last_mon = datetime.datetime.today() - relativedelta(months=1)   #获取前一月的日期
last_mon = last_mon.strftime('%Y%m%d')   # 转换成STR
ts.set_token('you token')
pro=ts.pro_api()

df = pro.index_weight(index_code = '399005.SZ', start_date = last_year, end_date = today)

zxb_list = df.con_code.values
print(len(zxb_list))

ATR_Value = []

# 获取ATR的值
for stock in zxb_list:
    df1 = pro.daily(ts_code=stock, start_date=last_mon, end_date= today)
    df1 = df1.set_index('trade_date')   # 将最近的日期放到最后
    df1 = df1.sort_index(ascending = False)   # 将最近的日期放到最后
    ATRs = tb.ATR(df1.high.values,df1.low.values,df1.close.values, timeperiod=14)
    ATR = ATRs[-1]
    ATR_Value.append(ATR)
df['ATR_Value'] = ATR_Value
df2 = df.sort_values(by = 'ATR_Value',ascending = False).head(33)

df2 = df2.reset_index()
df2 = df2.drop(columns = ['index'])
df1_list = df2.con_code.values

# 检测5日均线与10日均线的大小关系
label = []
for t in df1_list:
    df3 = pro.daily(ts_code= t , start_date=last_year, end_date= today)
    df3 = df3.set_index('trade_date')
    df3 = df3.sort_index(ascending = True)
    SMA5 = tb.SMA(df3[['close'][0]], timeperiod=5)
    SMA10 = tb.SMA(df3[['close'][0]], timeperiod=10)
    if SMA5[-1] > SMA10[-1]:
        label.append(1)
    else :
        label.append(0)
df2['label'] = label

df4 = df2.loc[df2['label'] == 1]  #只获取标签为1的股票
df4 = df4.reset_index()
df4_list = df4.con_code.values

# 根据MACD指标信号筛选股票
buy_list = []
for s in df4_list:
    df5 = pro.daily(ts_code = s , start_date=last_year, end_date= today)  #获取平安银行一年的行情数据
    df5 = df5.set_index('trade_date')
    df5 = df5.sort_index(ascending = True)
    # 参数设置为12 26 9
    dif, dea, bar = tb.MACD(df5.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
    if dif[-1] < 0 and dif[-1] > dea[-1]:
        buy_list.append(s)
    else:
        Continue

print(buy_list )