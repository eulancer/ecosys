import datetime
from analysis_u.strategy.tushare_util import get_pro_client
import pandas as pd

"""
避免打印时出现省略号
"""
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

"""
# 获取最近交易日当日大宗交易数据

"""


# 选股函数
def get_stock_list(pro, day):
    df_block = pro.block_trade(trade_date=day)

    df_block.sort_values(by='amount', ascending=False, inplace=True)
    df_daily = pro.daily(trade_date=day)
    df_result = pd.merge(df_block, df_daily, how='left', on=['ts_code', 'trade_date'])
    df_result_stock = df_result[df_result['price'] >= df_result['close']]
    df_result_stock.sort_values(by=['ts_code', 'amount_x'], ascending=(False, False),
                                inplace=True)
    #    print(df_result_stocks)
    if len(df_result_stock['ts_code']) > 1:
        stock_list = df_result_stock['ts_code'].values
        stock_list = list(set(stock_list))

        print(stock_list)
        return stock_list


def main():
    pro = get_pro_client()

    start_day = 20211018
    end_day = 20211022
    trade_cal = pro.trade_cal(start_date=start_day, end_date=end_day)

    cur_capital = 10000.00
    print(cur_capital)
    cur_money_lock = 0.00
    cur_money_rest = 0.00
    # stock_pool = []  # 买入股票池
    stock_map1 = pd.DataFrame(columns=['ts_code', 'buy_price', 'buy_num', 'day'])  # 买入股票信息
    stock_map2 = pd.DataFrame(columns=['ts_code', 'buy_price', 'buy_num', 'day', 'sell_price'])  # 卖出入股票信息
    stock_map3 = pd.DataFrame()
    stock_all = []
    ban_list = []

    cal_date = trade_cal['cal_date'].values.tolist()
    print(cal_date)
    for day in cal_date:
        # 选股初始化模块
        # 获取股票池及日线数据
        stock_pool = get_stock_list(pro, day)
        df_today = pro.daily(trade_date=day)

        # 获取第二天的日线数据，用于买入
        if len(cal_date) > cal_date.index(day) + 1:
            next_day = cal_date[cal_date.index(day) + 1]
            df_next_day = pro.daily(trade_date=next_day)

        # 交易预警模块 买入
        print(cur_capital)
        num = len(stock_pool)
        if num >= 1 and len(cal_date) >= cal_date.index(day) + 1:
            for stock in stock_pool:
                num_capital = cur_capital / num  # 购买资金
                buy_price = df_next_day[df_next_day['ts_code'] == stock].open  # 购买价格
                buy_num = num_capital / buy_price  # 购买数量
                stock_buy_info = pd.Series([stock, buy_price, buy_num, day],
                                           index=['ts_code', 'buy_price', 'buy_num', 'day'])
                stock_map1.append(stock_buy_info, ignore_index=True)
                cur_capital += int(buy_price) * int(buy_num)
                # print("cur_money_lock")
                # cur_capital -= cur_money_lock
            else:
                print()

            print(cur_capital)

        # 交易预警模块 卖出，如果有持仓，先卖出
        if len(stock_map1) >= 1:
            for stock in stock_map1['ts_code'].values:
                sell_price = df_today[df_today['ts_code'] == stock].open  # 卖出价格
                sell_price = stock_map1[stock_map1[['ts_code'] == stock]].buy_price
                buy_num = stock_map1[stock_map1[['ts_code'] == stock]].buy_num
                stock_sell_info = pd.Series([stock, buy_price, buy_num, day, sell_price],
                                            index=['ts_code', 'buy_price', 'buy_num', 'day', 'sell_price'])
                stock_map2.append(stock_sell_info, ignore_index=True)
                cur_capital += int(sell_price) * int(buy_num)
            # cur_capital = cur_money_rest
            stock_map1.drop(index=stock_map1.index)
        else:
            print()

        #

        # 模型训练模块

        # 买卖点判断模块（包括但不限于模型的预测结果）

        # 仓位管理

        # 交易执行模块

        # 结果数据可视化模块


if __name__ == "__main__":
    main()
