from StockFilter.tushare_util import get_pro_client
from StockFilter.tushare_util import get_all_code_df
import time
from time import mktime
from datetime import datetime
from datetime import timedelta
import pandas as pd


# 公告发布时间，end_date
# 例如，20210331、20210631、20210931
def get_stock_list(End_dates):
    pro = get_pro_client()
    # 时间参数
    # 当前季度的时间范围
    print(End_dates)
    End_date = datetime.strptime(End_dates, "%Y%m%d")
    # End_date = End_date.strftime("%Y%m%d")
    # print(End_date.strftime("%Y%m%d"))
    start_date = (End_date + timedelta(days=-60)).strftime("%Y%m%d")
    print(start_date)
    # 当上一季度的时间范围
    end_date_before = (End_date + timedelta(days=-120)).strftime("%Y%m%d")
    start_date_before = (End_date + timedelta(days=-150)).strftime("%Y%m%d")
    End_date = End_date.strftime("%Y%m%d")
    # 最新的指标数据
    trade_date = datetime.now().strftime("%Y%m%d")
    df_trade_cal = pro.trade_cal(exchange='', start_date=start_date_before, end_date=End_date, is_open=1)
    # 获取最新交易时间

    while trade_date not in df_trade_cal.values:
        trade_date = datetime.strptime(trade_date, "%Y%m%d")
        trade_date = (trade_date - timedelta(days=1)).strftime("%Y%m%d")

    # 获取当前股票的股东数量并去重
    df_holder_now = pro.stk_holdernumber(ts_code='', start_date=start_date, end_date=End_date)
    df_holder_now.drop_duplicates(subset=['ts_code'], keep="first", inplace=True)
    # 获取上一季度股票的股东数量 并去重
    df_holder_before = pro.stk_holdernumber(ts_code='', start_date=start_date_before, end_date=end_date_before)
    df_holder_before.drop_duplicates(subset=['ts_code'], keep="first", inplace=True)
    # 修改列名
    df_holder_before.rename(columns={"ann_date": "ann_date_b", "end_date": "end_date_b", "holder_num": "holder_num_b"},
                            inplace=True)
    df_holder = pd.merge(df_holder_now, df_holder_before, how='inner', on='ts_code')
    # 获取当前股票数据
    df_basic = pro.daily_basic(trade_date=trade_date, fields='ts_code,trade_date,total_mv')
    df_stock = pd.merge(df_holder, df_basic, how='inner', on='ts_code')

    # 获取候选股票名单
    df_stock_list = get_all_code_df()
    # print(df_stock_list)
    # 合并本季度、上季度股东数及当日指标
    df_stock_b = pd.merge(df_stock, df_stock_list, how='inner', on='ts_code')

    # 筛选股票市值、股东数量，并计算股东下降比例，选择下降比例大于15%
    df_stock_c = df_stock_b[(df_stock_b['total_mv'] <= 20000000) & (df_stock_b['holder_num'] <= 40000)]
    df_stock_c['hold_percent_down'] = df_stock_c.apply(
        lambda x: round((x['holder_num_b'] - x['holder_num']) / x['holder_num_b'], 4), axis=1)
    df_stock_c['total_mv'] = df_stock_c.apply(
        lambda x: (x['total_mv'] / 10000), axis=1)

    stock_result = df_stock_c[df_stock_c['hold_percent_down'] >= 0.15][
        ['ts_code', 'name', 'total_mv', 'end_date', 'holder_num', 'hold_percent_down']]

    stock_result.sort_values('hold_percent_down', ascending=False, inplace=True)
    stock_result.index = range(len(stock_result))

    stock_result = stock_result.reset_index(drop=True)

    # 写入文件
    with open(r'股东小于4万市值小于200亿股东下降了15%以上非新股非ST名单.txt', 'w', encoding='utf-8')as f:
        f.write('股东小于4万市值小于200亿股东下降了15%以上非新股非ST名单\n')
        stock_result.to_csv(f, index=False)
    f.close()
    print(stock_result)

    return stock_result


if __name__ == "__main__":
    end_date = '20210930'
    get_stock_list(end_date)

    """
    # 按日期获取
    def get_holder_data(code, start, end):
        pro = get_pro_client()
        df = pro.stk_holdernumber(ts_code=code, start_date=start, end_date=end)
        return df


    # 获取市值小于200亿的股票
    def get_total_mv(code, trade_date):
        df = pro.daily_basic(ts_code=code, trade_date=trade_date,
                             fields='ts_code,trade_date,total_mv')
        return df.total_mv


    # 获取股票的市值
    def get_stock_total_mv(code, date):
        pro = get_pro_client()
        df = pro.query('daily_basic', ts_code=code, trade_date=date,
                       fields='ts_code,trade_date,total_mv')
        print(df)
        return df['total_mv'][0]



    # 获取报告周期小于2股东人数持续监测周最终股票名单
    def get_stock(trade_date):
        n = 120
        stocks = get_stock_list()
        stocks_p = []
        trade_date = trade_date
        i = 1
        for code in stocks.values():
            i = i + 1
            print("第" + str(i) + "次")
            df = get_holder_data(code, n=n)
            time.sleep(0.01)
            # 报告周期小于2周
            inner_time = datetime.strptime(df["ann_date"][0], '%Y%m%d') - datetime.strptime(df["end_date"][0], '%Y%m%d')
            print(inner_time)
            try:
                if inner_time.days <= 15 and df["holder_num"][0] < 40000:
                    num1 = df["holder_num"][0] - df["holder_num"][1]
                    num2 = df["holder_num"][1] - df["holder_num"][2]
                    # 股东人数持续监测
                    if num1 < 0 and num2 < 0:
                        if get_stock_total_mv(code, trade_date) < 2000000:
                            # 该代码放入股票池
                            stocks_p.append(code)
                            print("该代码放入股票池 ")
                            print(code)
            except Exception as re:
                print(re)
        print(stocks_p)
        with open('D:/Work/git/ecosys/data/holder_list.txt', 'w') as f:
            for i in stocks_p:
                f.write(i)
        f.close()
    """

    '''
    # 半半年和3季报股东股东15%的股票
    # 获取报告周期小于2股东人数持续监测周最终股票名单
    def get_stock(trade_date):
        pro = get_pro_client()
        df = pro.daily_basic(ts_code='', trade_date='20180726',
                             fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb')
        stocks = get_all_code()
        stocks_p = []
        trade_date = trade_date
        i = 1
        for code in stocks.values():
            i = i + 1
            try:
                if get_stock_total_mv(code, trade_date) < 2000000:
                    print("第" + str(i) + "次")
                    time.sleep(0.55)
                    df_mid = get_holder_data(code, 20210601, 20210630)
                    df_third = get_holder_data(code, 20210801, 20210902)
                    # 股东小于40000
                    if df_third["holder_num"][0] < 40000:
                        # 股东下降比例
                        num1 = df_mid["holder_num"][0] - df_third["holder_num"][0]
                        num2 = df_mid["holder_num"][0]
                        rate = num1 / num2 * 100
                        # 股东人数持续监测
                        if rate >= 15:
                            # 该代码放入股票池
                            stocks_p.append(code)
                            print("该代码放入股票池 ")
                            print(code)
            except Exception as re:
                print(re)
        print(stocks_p)
        with open('D:/Work/git/ecosys/data/holder_list_0830-15-01  .txt', 'w') as f:
            for i in stocks_p:
                f.write(i)
        f.close()
    '''
