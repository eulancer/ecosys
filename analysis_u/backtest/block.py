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


class Deal(object):
    cur_capital = 0.00
    cur_money_lock = 0.00
    cur_money_rest = 0.00
    stock_pool = []
    stock_map1 = {}
    stock_map2 = {}
    stock_map3 = {}
    stock_all = []
    ban_list = []

    def __init__(self, state_dt):
        try:
            done_set = []  ######  sql_select = 'select * from my_capital a order by seq desc limit 1'
            self.cur_capital = 0.00
            self.cur_money_lock = 0.00
            self.cur_money_rest = 0.00
            if len(done_set) > 0:
                self.cur_capital = float(done_set[0][0])
                self.cur_money_rest = float(done_set[0][2])

            done_set2 = []  ########
            self.stock_pool = []
            self.stock_all = []
            self.stock_map1 = []
            self.stock_map2 = []
            self.stock_map3 = []
            self.ban_list = []
            if len(done_set2) > 0:
                self.stock_pool = [x[0] for x in done_set2 if x[2] > 0]
                self.stock_all = [x[0] for x in done_set2]
            self.stock_map1 = {x[0]: float(x[1]) for x in done_set2}
            self.stock_map2 = {x[0]: int(x[2]) for x in done_set2}
            self.stock_map3 = {x[0]: int(x[3]) for x in done_set2}
            for i in range(len(done_set2)):
                done_temp = []  #####
                sql = "select * from stock_info a where a.stock_code = '%s' and a.state_dt = '%s'" % (
                    done_set2[i][0], state_dt)
                self.cur_money_lock += float(done_temp[0][3]) * float(done_set2[i][2])
        except Exception as excp:
            # db.rollback()
            print(excp)


# 交易模块
def buy(stock_code, opdate, buy_money):
    deal_buy = Deal.Deal(opdate)
    if deal_buy.cur_money_rest + 1 >= buy_money:
        done_set_buy = []  ######
        if len(done_set_buy) == 0:
            return -1
        buy_price = float(done_set_buy[0][3])
        if buy_price >= 195:
            return 0
        vol, rest = divmod(min(deal_buy.cur_money_rest, buy_money), buy_price * 100)
        vol = vol * 100
        if vol == 0:
            return 0
        new_capital = deal_buy.cur_capital - vol * buy_price * 0.0005
        new_money_lock = deal_buy.cur_money_lock + vol * buy_price
        new_money_rest = deal_buy.cur_money_rest - vol * buy_price * 1.0005
        sql_buy_update2 = "insert into my_capital(capital,money_lock,money_rest,deal_action,stock_code,stock_vol,state_dt,deal_price)VALUES ('%.2f', '%.2f', '%.2f','%s','%s','%i','%s','%.2f')" % (
            new_capital, new_money_lock, new_money_rest, 'buy', stock_code, vol, opdate, buy_price)
        if stock_code in deal_buy.stock_all:
            new_buy_price = (deal_buy.stock_map1[stock_code] * deal_buy.stock_map2[stock_code] + vol * buy_price) / (
                    deal_buy.stock_map2[stock_code] + vol)
            new_vol = deal_buy.stock_map2[stock_code] + vol
            sql_buy_update3 = "update my_stock_pool w set w.buy_price = (select '%.2f' from dual) where w.stock_code = '%s'" % (
                new_buy_price, stock_code)
            sql_buy_update3b = "update my_stock_pool w set w.hold_vol = (select '%i' from dual) where w.stock_code = '%s'" % (
                new_vol, stock_code)
            sql_buy_update3c = "update my_stock_pool w set w.hold_days = (select '%i' from dual) where w.stock_code = '%s'" % (
                1, stock_code)
        else:
            sql_buy_update3 = "insert into my_stock_pool(stock_code,buy_price,hold_vol,hold_days) VALUES ('%s','%.2f','%i','%i')" % (
                stock_code, buy_price, vol, int(1))
    return 0


def sell(stock_code, opdate, predict):
    deal = Deal.Deal(opdate)
    init_price = deal.stock_map1[stock_code]
    hold_vol = deal.stock_map2[stock_code]
    hold_days = deal.stock_map3[stock_code]
    sql_sell_select = "select * from stock_info a where a.state_dt = '%s' and a.stock_code = '%s'" % (
        opdate, stock_code)

    done_set_sell_select = []  ##########
    if len(done_set_sell_select) == 0:
        return -1
    sell_price = float(done_set_sell_select[0][3])

    if sell_price > init_price * 1.03 and hold_vol > 0:
        new_money_lock = deal.cur_money_lock - sell_price * hold_vol
        new_money_rest = deal.cur_money_rest + sell_price * hold_vol
        new_capital = deal.cur_capital + (sell_price - init_price) * hold_vol
        new_profit = (sell_price - init_price) * hold_vol
        new_profit_rate = sell_price / init_price
        sql_sell_insert = "insert into my_capital(capital,money_lock,money_rest,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
            new_capital, new_money_lock, new_money_rest, 'SELL', stock_code, hold_vol, new_profit, new_profit_rate,
            'GOODSELL', opdate, sell_price)
        sql_sell_update = "delete from my_stock_pool where stock_code = '%s'" % (stock_code)
        return 1

    elif sell_price < init_price * 0.97 and hold_vol > 0:
        new_money_lock = deal.cur_money_lock - sell_price * hold_vol
        new_money_rest = deal.cur_money_rest + sell_price * hold_vol
        new_capital = deal.cur_capital + (sell_price - init_price) * hold_vol
        new_profit = (sell_price - init_price) * hold_vol
        new_profit_rate = sell_price / init_price
        sql_sell_insert2 = "insert into my_capital(capital,money_lock,money_rest,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
            new_capital, new_money_lock, new_money_rest, 'SELL', stock_code, hold_vol, new_profit, new_profit_rate,
            'BADSELL', opdate, sell_price)

        sql_sell_update2 = "delete from my_stock_pool where stock_code = '%s'" % (stock_code)

        # sql_ban_insert = "insert into ban_list(stock_code) values ('%s')" %(stock_code)
        # cursor.execute(sql_ban_insert)
        # db.commit()

        return 1

    elif hold_days >= 4 and hold_vol > 0:
        new_money_lock = deal.cur_money_lock - sell_price * hold_vol
        new_money_rest = deal.cur_money_rest + sell_price * hold_vol
        new_capital = deal.cur_capital + (sell_price - init_price) * hold_vol
        new_profit = (sell_price - init_price) * hold_vol
        new_profit_rate = sell_price / init_price
        sql_sell_insert3 = "insert into my_capital(capital,money_lock,money_rest,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
            new_capital, new_money_lock, new_money_rest, 'OVERTIME', stock_code, hold_vol, new_profit, new_profit_rate,
            'OVERTIMESELL', opdate, sell_price)

        sql_sell_update3 = "delete from my_stock_pool where stock_code = '%s'" % (stock_code)

        return 1

    elif predict == -1:
        new_money_lock = deal.cur_money_lock - sell_price * hold_vol
        new_money_rest = deal.cur_money_rest + sell_price * hold_vol
        new_capital = deal.cur_capital + (sell_price - init_price) * hold_vol
        new_profit = (sell_price - init_price) * hold_vol
        new_profit_rate = sell_price / init_price
        sql_sell_insert4 = "insert into my_capital(capital,money_lock,money_rest,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
            new_capital, new_money_lock, new_money_rest, 'Predict', stock_code, hold_vol, new_profit, new_profit_rate,
            'PredictSell', opdate, sell_price)
        sql_sell_update3 = "delete from my_stock_pool where stock_code = '%s'" % (stock_code)

        return 1
    return 0


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
        print(stock_list)
        stock_list = list(set(stock_list))
        return stock_list


def main():
    pro = get_pro_client()

    start_day = 20211018
    end_day = 20211022
    trade_cal = pro.trade_cal(start_date=start_day, end_date=end_day)

    cur_capital = 10000.00
    cur_money_lock = 0.00
    cur_money_rest = 0.00
    stock_pool = []  # 买入股票池
    stock_map1 = {}  # 买入股票信息
    stock_map2 = {}
    stock_map3 = {}
    stock_all = []
    ban_list = []

    cal_date = trade_cal.cal_date
    for day in cal_date:
        # 选股初始化模块
        print(day)
        stock_pool = get_stock_list(pro, day)
        next_day = cal_date[cal_date.index(day) + 1]
        # 获取第二天的日线数据，用于买入
        df_next_day = pro.daily(trade_date=next_day)

        # 交易预警模块
        num = len(stock_pool)
        for stock in stock_pool:
            num_capital = cur_capital / num  # 购买资金
            buy_price = df_next_day[df_next_day['ts_code'] == stock].open  # 购买价格
            buy_num = num_capital / buy_price  # 购买数量


            print(stock)

        # 模型训练模块

        # 买卖点判断模块（包括但不限于模型的预测结果）

        # 仓位管理

        # 交易执行模块

        # 结果数据可视化模块


if __name__ == "__main__":
    main()
