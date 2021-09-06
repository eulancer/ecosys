import tushare as ts
from collector.tushare_util import get_pro_client


def main():
    pro = get_pro_client()
    df = pro.stock_basic(exchange='', list_status='L')
    name = df[df['ts_code'] == '000835.SZ']
    print( name)


if __name__ == '__main__':
    main()
