import pymysql
import config

# 封装函数，用于在回测过程中，每日更新资产表中相关数据。
# 更新仓位数据，获取最新股票数据，更新价格及仓位
def cap_update_daily(state_dt):
    para_norisk = (1.0 + 0.04 / 365)
    db = pymysql.connect(host=config.host, user=config.user, passwd='', db=config.db, charset=config.unicode)
    cursor = db.cursor()
    sql_pool = "select * from my_stock_pool"
    cursor.execute(sql_pool)
    done_set = cursor.fetchall()
    db.commit()
    new_lock_cap = 0.00
    print("开始仓位管理")
    for i in range(len(done_set)):
        stock_code = str(done_set[i][0])
        stock_vol = float(done_set[i][2])
        # stock info 表交易数据表
        sql = "select * from stock_info a where a.ts_code = '%s' and a.trade_date<= '%s' order by a.trade_date desc limit 1" % (
            stock_code, state_dt)
        cursor.execute(sql)
        done_temp = cursor.fetchall()
        db.commit()
        if len(done_temp) > 0:
            cur_close_price = float(done_temp[0][6])
            new_lock_cap += cur_close_price * stock_vol
        else:
            print('Cap_Update_daily Err!!')
            raise Exception
    sql_cap = "select * from my_capital order by seq asc"
    cursor.execute(sql_cap)
    done_cap = cursor.fetchall()
    print("done_cap"+str(done_cap))
    db.commit()

    new_cash_cap = float(done_cap[-1][2]) * para_norisk
    # -对Python来说，负数索引表示从右边往左数，最右边的元素的索引为-1，倒数第二个元素为-2.，。。
    print("new_cash_cap"+str(new_cash_cap))
    new_total_cap = new_cash_cap + new_lock_cap
    sql_insert = "insert into my_capital(capital,money_lock,money_rest,bz,trade_date)values('%.2f','%.2f','%.2f','%s','%s')" % (
        new_total_cap, new_lock_cap, new_cash_cap, str('Daily_Update'), state_dt)
    cursor.execute(sql_insert)
    db.commit()
    return 1
