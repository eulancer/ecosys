import os
import time
from strategy.tushare_util import get_pro_client
import pandas as pd


def main():
    trade_date = '20210903'
    last_year = '20190101'
    start_date = '20210907'

    pro = get_pro_client()
    df = pro.daily_basic(ts_code='', trade_date=start_date,
                         fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb')

    print("获股票名单")
    # 筛选PE为15以下的，PB为1以下的股票
    PE_T = 15
    PB_T = 1
    df_choose = df[(df.pe <= PE_T) & (df.pb <= PB_T)]
    i = 0
    income = []
    for c in df_choose.ts_code:
        df_income = pro.income(ts_code=c, start_date=last_year, end_date=start_date,
                               fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps')
        income.append(df_income['basic_eps'].iloc[0])
        i = i + 1
        print("股票~~~~~~~~~~~~~~~~~~~~~~~~~~~~" + str(i))
        print(c)
        time.sleep(1.2)
    df_choose['basic_eps'] = income
    df_choose_good = df_choose[df_choose.basic_eps > 1.0]
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(df_choose_good)
    print(len(df_choose_good))

    data_path = './data/'
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    csv_name = f'allname_data.csv'
    csv_path = os.path.join(data_path, csv_name)
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    data.to_csv(csv_path, index=False)
    data = data[data.ts_code.isin(df_choose_good.ts_code)]
    print(data)
    # 显示所有行业


if __name__ == "__main__":
    main()
