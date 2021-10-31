import datetime
from analysis_u.strategy.tushare_util import get_pro_client
import pandas as pd
from loguru import logger
from tqdm import tqdm

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

@logger.catch()
def get_stock_list(pro, day):
    # 获取大宗交易数据
    df_block = pro.block_trade(trade_date=day)
    df_block.sort_values(by='amount', ascending=False, inplace=True)

    # 获取日常数据
    df_daily = pro.daily(trade_date=day)
    df_result = pd.merge(df_block, df_daily, how='left', on=['ts_code', 'trade_date'])
    # print(df_result)

    # 大宗交易溢价
    # df_result_stock = df_result[df_result['price'] >= df_result['close'] & df_result['buyer'] == '机构专用']
    # df_result_stock = df_result[df_result['buyer'] == '机构专用']
    if not df_result[(df_result['price'] < df_result['close'])].empty:
        df_result_stock_c = df_result[(df_result['price'] < df_result['close'])]
        # print("机构交易及溢价")
        # print(df_result_stock)
        df_result_stock = df_result_stock_c.copy()
        # df_result_stock.sort_values(by='ts_code', ascending=False, inplace=True)
        stock_list = df_result_stock['ts_code'].values
        if len(df_result_stock['ts_code']) > 1:
            stock_list = df_result_stock['ts_code'].values
            stock_list = list(set(stock_list))
            # print(stock_list)
        return stock_list
    else:
        df_result_stock = None
        # print(df_result_stock)
        return df_result_stock


@logger.catch()
def main():
    pro = get_pro_client()

    # 交易时间
    start_day = 20201018
    end_day = 20211022
    trade_cal = pro.trade_cal(start_date=start_day, end_date=end_day)
    cal_date = trade_cal['cal_date'].values.tolist()
    print(cal_date)

    # 交易账户
    cur_capital = 10000.00
    print("the initial cur_capital")
    print(cur_capital)
    cur_money_lock = 0.00
    cur_money_rest = cur_capital - cur_money_lock
    stock_pool = []  # 买入股票池
    stock_map1 = pd.DataFrame(columns=['ts_code', 'buy_price', 'buy_num', 'day'])  # 买入股票信息
    stock_map2 = pd.DataFrame()  # 卖出入股票信息
    stock_map3 = pd.DataFrame()
    stock_all = []
    ban_list = []

    for day in tqdm(cal_date):
        # 选股初始化模块
        # 获取股票池及日线数据，得考虑股票池为空的情况
        stock_pool = get_stock_list(pro, day)
        df_today = pro.daily(trade_date=day)

        # 获取第二天的日线数据，用于买入
        if len(cal_date) > cal_date.index(day) + 2:
            next_day = cal_date[cal_date.index(day) + 1]
            df_next_day = pro.daily(trade_date=next_day)

        # 交易预警模块 卖出，如果有持仓，先卖出
        if len(stock_map1) >= 1:
            for stock in tqdm(stock_map1['ts_code'].values):
                print("卖出")
                print(stock)
                if not (df_next_day[df_next_day['ts_code'] == stock]['open']).empty:
                    sell_price = df_next_day[df_next_day['ts_code'] == stock]['open'].values[0]  # 卖出价格
                    print(sell_price)

                    buy_price = stock_map1[stock_map1['ts_code'] == stock]['buy_price'].values[0]

                    buy_num = stock_map1[stock_map1['ts_code'] == stock]['buy_num'].values[0]

                    stock_sell = [stock, buy_price, buy_num, next_day, sell_price]
                    stock_map2 = stock_map2.append(
                        pd.DataFrame([stock_sell], columns=['ts_code', 'buy_price', 'buy_num', 'day', 'sell_price']),
                        ignore_index=True)

                    print("buy_num")
                    print(buy_num)
                    print("sell_price")
                    print(sell_price)
                    cur_capital = (sell_price * buy_num)
                    print("卖出后当前资金")
                    print(cur_capital)
                    print(stock_map2)

                    stock_map1.drop(stock_map1.index, inplace=True)
                    stock_map1 = stock_map1.drop(index=stock_map1.index)  # 清空
                else:
                    print("该股票停牌")
                    break
        else:
            print('没有持仓')

        # 交易预警模块 买入
        if stock_pool is not None:
            num = len(stock_pool)
            print("stock_pool")
            print(stock_pool)

        else:
            num = 0

        if num >= 1 and len(cal_date) >= cal_date.index(day) + 2:
            print('开始买入')
            for stock in tqdm(stock_pool):

                print(stock)
                # num_capital = cur_capital / num  # 购买资金
                if not (df_next_day[df_next_day['ts_code'] == stock]).empty:
                    buy_price = df_next_day[df_next_day['ts_code'] == stock]['open'].values[0]  # 购买价格
                    print("买入价格")
                    print(buy_price)
                    buy_num = cur_capital / buy_price  # 购买数量

                    stock_info = [stock, buy_price, buy_num, day]
                    stock_info_index = ['ts_code', 'buy_price', 'buy_num', 'day']
                    stock_buy_info = pd.Series(stock_info, index=stock_info_index)
                    stock_map1 = stock_map1.append(stock_buy_info, ignore_index=True)

                    cur_capital = 0
                    print("买入后当前资金")
                    print(cur_capital)
                    print(stock_map1)
                else:
                    print("该股票停牌")
                    break

                break
            else:
                print("~~~~~")

        #

        # 模型训练模块

        # 买卖点判断模块（包括但不限于模型的预测结果）

        # 仓位管理

        # 交易执行模块

        # 结果数据可视化模块


if __name__ == "__main__":
    main()
