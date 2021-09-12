from datetime import datetime

import tushare
import config


# tushare连接方式
def get_pro_client():
    return tushare.pro_api(config.tushare_token)


def get_ts_code(stock_number):
    for i in config.ts_code_pattern:
        for n in i.get('pattern'):
            if stock_number.startswith(n):
                return stock_number + i.get('code_postfix')


def get_all_code():
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    # 去除ST股票
    df = df[~df.name.str.contains('ST')]
    # 去除2020101以后的新股
    df['list_date'] = df['list_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
    df = df[(df['list_date'] < datetime(2021, 1, 1))]

    codes = df.ts_code.values
    names = df.name.values
    stock = dict(zip(names, codes))
    return stock


def get_all_code_df():
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    # 去除ST股票
    df = df[~df.name.str.contains('ST')]
    # 去除2020101以后的新股
    df['list_date'] = df['list_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
    df = df[(df['list_date'] < datetime(2021, 1, 1))]
    stocks = df[['ts_code', 'name']]
    return stocks


# 获取当前国企企业代码
def get_Ne_code():
    codes = []
    names = []
    with open(config.Ne_path) as f:
        raw_line = f.readlines()
        for i in raw_line:
            line = i.strip('')
            # print(line)
            if line.startswith('#'):
                continue
            (code, name) = line.split('\t')
            codes.append(code.strip('\t'))  # .strip('\t') 去空格
            names.append(name.strip('\n'))  # .strip('\n') 去除换行符
    f.close()
    stock = dict(zip(names, codes))
    # print(stock)
    return stock

# 获取去重的股票
def get_stock_list():
    stocks = get_all_code()
    all_stocks = get_all_code()
    Ne_stocks = get_Ne_code()
    print(Ne_stocks)
    # 去除国企
    try:
        for j in all_stocks:
            print(j)
            if j in Ne_stocks:
                print(j)
                print(stocks[j])
                del stocks[j]
    except IOError:
        print
        "Error: 没有找到文件或读取文件失败"
    else:
        print
        "内容写入文件成功"

    return stocks