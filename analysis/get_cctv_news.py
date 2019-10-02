# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd
import datetime
import os
import time

import config
from collector.tushare_util import get_pro_client

# 获取指定时间区间内的所有日期
def get_day_list(day_start,day_end):
    '''
    获取指定时间区间内的所有日期
    '''
    day_start = datetime.datetime.strptime(day_start, '%Y%m%d')
    day_end = datetime.datetime.strptime(day_end, '%Y%m%d')
    daylist = []
    while day_start <= day_end:
        day = day_start.strftime('%Y%m%d')  # 转为字符串格式
        daylist.append(day)
        day_start += datetime.timedelta(days=1)  # 下一个日期
    day_amount = len(daylist)  # 总共天数
    print(daylist)
    return daylist

# 获取CCTV新闻
def get_ccTV(daylist):
    pro = get_pro_client()
    dayindex = 0
    counter = 0
    for day in daylist:  # 开始遍历每一个日期
        dayindex += 1
        df = pro.cctv_news(date=day)  # CCTV新闻联播
        counter += 1
        df.to_sql(name="stock_cctv_news", con=config.engine, schema=config.db, index=True, if_exists='append',
                  chunksize=1000)
        time.sleep(0.001)

        if counter == 99:
            print("- 等待45s...")
            time.sleep(45)
            counter = 0

    # if not os.path.exists(tablefolder):  # 如果不存在这个文件夹路径，新建
    # os.mkdir(tablefolder)
def main():
    day_start = r'20190101'  # 起始日期
    day_end = r'20190923'  # 结束日期
    day_list=get_day_list(day_start, day_end)
    get_ccTV(day_list)


if __name__ == '__main__':
    main()