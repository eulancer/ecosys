import config
import pandas as pd
from collector.tushare_util import get_pro_client
import datetime
from datetime import datetime, timedelta


def get_Ne_code():
    dataset = open('D:/Work/git/ecosys/data/holder_list.txt', "r")
    line = dataset.read().replace('[', '')
    line = line.replace(']', '')
    line = line.replace('\'', '')
    codes = line.split(',')
    print("读取的数据为: %s" % line)
    dataset.close()
    print(codes[0])
    return codes


def get_ALL_code():
    dataset = open('D:/Work/git/ecosys/data/holder_list_25.txt', "r")
    line = dataset.read()
    # 目标股票清单
    codes_list = line.split('\n')
    print("读取的数据为: %s" % codes_list)
    dataset.close()
    print(codes_list[0])

    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    # 去除ST股票
    df = df[df.name.str.contains('ST')]
    print(df)

    # 股票清单
    codes = df.ts_code.values
    names = df.name.values
    stocks = dict(zip(names, codes))
    codes_end_list = codes_list
    # stocks 和 codes 合集
    try:
        for j in codes_list:
            print(j)
            if j in codes:
                print(j)
                codes_end_list.remove(j)
    except IOError:
        print
        "Error: 没有找到文件或读取文件失败"
    else:
        print
        "内容写入文件成功"

    with open('D:/Work/git/ecosys/data/holder_list_20_ST_20200101.txt', 'w') as f:
        f.write(str(codes_end_list))
        f.close()


# 获取股票的市值
def get_total_mv(code, date):
    pro = get_pro_client()
    df = pro.query('daily_basic', ts_code=code, trade_date=date,
                   fields='ts_code,trade_date,total_mv')
    print(df)
    return df


def main():
    get_ALL_code()


""""
def main():
    t = datetime.now()
    end = 20201023
    d = get_Ne_code()
    stock_list = []
    try:
        for i in d:
            daily_basic = get_total_mv(i, end)
            print(daily_basic)
            if daily_basic['total_mv'][0] < 2000000:
                stock_list.append(i)
                print(i)
    except Exception as re:
        print(re)
    with open('D:/Work/git/ecosys/data/holder_list_200.txt', 'w') as f:
        f.write(str(stock_list))
        f.close()
    # print(d)
"""

if __name__ == "__main__":
    main()
