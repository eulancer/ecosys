# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd
import datetime
import os
import time
from collector.tushare_util import get_pro_client

def main():
    '''
    获取指定时间区间内的所有日期
    '''
    day_start = r'20190101'  # 起始日期
    day_end = r'20190923'  # 结束日期
    day_start = datetime.datetime.strptime(day_start,'%Y%m%d')
    day_end = datetime.datetime.strptime(day_end,'%Y%m%d')
    daylist = []
    while day_start <= day_end:
        day = day_start.strftime('%Y%m%d')  # 转为字符串格式
        daylist.append(day)
        day_start += datetime.timedelta(days=1)  # 下一个日期
    day_amount = len(daylist)  # 总共天数
    print(daylist)

    tablefolder = './tables'  # 存储表格的文件夹路径
    if not os.path.exists(tablefolder):  # 如果不存在这个文件夹路径，新建
        os.mkdir(tablefolder)

    '''
    使用tushare的pro版本接口
    pro = ts.pro_api(token_pro)
    '''
    token_pro = r'?' # ？更换为注册后获取的token
    pro = get_pro_client()  # pro 版本

    dayindex = 0
    counter = 0
    for day in daylist:  # 开始遍历每一个日期
        dayindex += 1
        print('- {}/{} now is getting the news of {}...'.format(dayindex,day_amount,day))
        cctvnews_file = tablefolder +'\\'+ r'cctvnews_{}.csv'.format(day)
        df = pro.cctv_news(date = day)  # CCTV新闻联播
        counter += 1
        df.to_csv(cctvnews_file,encoding='utf-8-sig')
        time.sleep(0.001)

        if counter == 99:
            print("- 等待60s...")
            time.sleep(45)
            counter = 0

if __name__ == '__main__':
    main()