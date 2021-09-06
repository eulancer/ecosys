from collector.tushare_util import get_pro_client
import pandas as pd
import numpy as np

"""
使用投资人常用的几个指标，总营业额，扣非净利润，ROE，负债比，现金流，毛利率。
并且试图把这些指标集中到一个表格当中，其中有些数据是需要自己计算的。这样就能清晰直观地看出公司的增长情况
"""

# An highlighted block
string = '002555.SZ'
sdate = '20130101'
edate = '20210831'
this_year = 2020
next_year_of_start_year = 2014
n = 7


# 获取资产负宅表


def get_balance_sheet():
    pro = get_pro_client()
    # 负债表的数据
    df = pro.balancesheet(ts_code=string, start_date=sdate, end_date=edate, period='20131231',
                          fields='ann_date,report_type,total_liab,total_assets')
    for i in range(next_year_of_start_year, this_year):
        p = str(i) + '1231'
        df_next = pro.balancesheet(ts_code=string, start_date=sdate, end_date=edate, period=p,
                                   fields='ann_date,report_type,total_liab,total_assets')
        df = pd.concat([df, df_next])
    # 总资产 总负债
    print("try ..............")
    print(df)
    try:
        df = df.drop([1])
    except:
        pass
    print("try later.")
    print(df)
    df['index'] = range(0, n)
    df = df.set_index('index')
    print(df)
    return df


# 收益表数据
def get_income():
    # 收益表数据
    pro = get_pro_client()
    ining = pro.income(ts_code=string, start_date=sdate, end_date=edate, period='20131231',
                       fields='ann_date,report_type,total_revenue,revenue,total_cogs')
    for i in range(next_year_of_start_year, this_year):
        p = str(i) + '1231'
        ining_next = pro.income(ts_code=string, start_date=sdate, end_date=edate, period=p,
                                fields='ann_date,report_type,total_revenue,revenue,total_cogs')
        ining = pd.concat([ining, ining_next])
    # 时间 类型 全营业额 营业额 全成本
    try:
        ining = ining.drop([1])
    except:
        pass
    n = 7
    # Tushare提供的数据有时候有重复的部分，需要去掉
    ining['index'] = range(0, n)
    ining = ining.set_index('index')
    print(ining)
    return ining

# 财务指标数据fina_indicator
def get_fina_indicator():
    pro = get_pro_client()
    fina = pro.fina_indicator(ts_code=string, start_date=sdate, end_date=edate, period='20131231',
                              fields='ann_date,profit_dedt,grossprofit_margin,roe')
    # 时间 扣非  销售毛利率 ROE
    for i in range(next_year_of_start_year, this_year):
        p = str(i) + '1231'
        fina_next = pro.fina_indicator(ts_code=string, start_date=sdate, end_date=edate, period=p,
                                       fields='ann_date,profit_dedt,grossprofit_margin,roe_waa')
        fina = pd.concat([fina, fina_next])

    try:
        # 去除重复数据
        fina = fina.drop([1])
    except:
        pass
    # Tushare提供的数据有时候有重复的部分，需要去掉
    fina['index'] = range(0, n)
    fina = fina.set_index('index')
    print(fina)
    return fina


def get_cash():
    pro = get_pro_client()
    cash = pro.cashflow(ts_code=string, start_date=sdate, end_date=edate, period='20131231',
                        fields='ann_date,report_type,n_cashflow_act')
    for i in range(next_year_of_start_year, this_year):
        p = str(i) + '1231'
        cash_next = pro.cashflow(ts_code=string, start_date=sdate, end_date=edate, period=p,
                                 fields='ann_date,report_type,n_cashflow_act')
        cash = pd.concat([cash, cash_next])

    try:

        cash = cash.drop([1])
    except:
        pass
    ###
    # Tushare提供的数据有时候有重复的部分，需要去掉

    cash['index'] = range(0, n)
    cash = cash.set_index('index')
    print(cash)
    return cash


def get_ROE():
    df = get_balance_sheet()
    cash = get_cash()
    fina = get_fina_indicator()
    ining = get_income()


    data = pd.DataFrame({'Year': np.zeros(n),
                         'Revenue': np.zeros(n),
                         'Growth rate of revenue ': np.zeros(n),
                         'profit_dedt': np.zeros(n),
                         'Growth rate of profit_dedt': np.zeros(n),
                         'Grossprofit_margin': np.zeros(n),
                         'Cash': np.zeros(n),
                         'Rate of Cash and profit_dedt': np.zeros(n),
                         'Asset liability ratio': np.zeros(n),
                         'ROE': np.zeros(n)})
    print(data)

    j = 0
    for i in range(next_year_of_start_year - 1, this_year):
        data['Year'][j] = i
        data['Revenue'][j] = ining['total_revenue'][j]
        if j == 0:
            pass
        else:
            # data['Growth rate of revenue'][j] = (data['Revenue'][j] - data['Revenue'][j - 1]) / data['Revenue'][j - 1]
            pass
        data['profit_dedt'][j] = fina['profit_dedt'][j]
        if j == 0:
            pass
        else:
            data['Growth rate of profit_dedt'][j] = (data['profit_dedt'][j] - data['profit_dedt'][j - 1]) / \
                                                    data['profit_dedt'][j - 1]

        data['Grossprofit_margin'][j] = fina['grossprofit_margin'][j]
        data['Cash'][j] = cash['n_cashflow_act'][j]
        data['Rate of Cash and profit_dedt'][j] = data['Cash'][j] / data['profit_dedt'][j]
        data['Asset liability ratio'][j] = df['total_liab'][j] / df['total_assets'][j]
        data['ROE'][j] = fina['roe_waa'][j]
        j = j + 1
    print(data)

def main():
    trade_date = '20210903'
    get_ROE()


if __name__ == "__main__":
    main()
