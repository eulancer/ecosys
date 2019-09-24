# -*- coding: utf-8 -*-
# Author: 微信公众号：whichnameisavailable
import pandas as pd
import os
import time
from wordcloud import WordCloud
import re
import matplotlib.pyplot as plt
import pylab  # matplotlib下的模块pyplot和pylab

tablefolder = './tables/'

def main():

    dflist = []
    for csv in os.listdir(tablefolder):
        if csv.startswith('cctvnews') and csv.endswith('.csv'):
            csv_path = tablefolder +'\\'+ csv  # 文件路径
            # =====导入数据=====
            df = pd.read_csv(filepath_or_buffer = csv_path,)  # DataFrame
            # print(df.shape[0])  # 行数
            dflist.append(df)  # 放到列表里
            # time.sleep(6)
    df_all = pd.concat(dflist)  # 连接函数concat
    df_all = df_all.reset_index()  # 重置索引
    print('')
    # print(df_all.shape[0])
    # print(df_all)

    series_content = df_all['content']
    # print(series_content)


    content_all_list = []  # 存放分词后的词汇
    content_string = ''

    for content_csv in series_content:  # 遍历Series中的每一行congtent（每一天的content）
        content_csv = str(content_csv)  # 转为字符串
        content_csv = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "",content_csv)  # 去除标点符号
        content_string = content_string + content_csv  # 汇总

    font = r'C:\Windows\Fonts\simfang.ttf'  # 为了让 wordcloud 支持显示中文，需指定Windows7汉字字体

    wordcloud_cctvnews = WordCloud(collocations = False,
                                   font_path = font,
                                   width = 1400,
                                   height = 1400,
                                   margin = 2,
                                   background_color = 'white',
                                   stopwords = ['1','2','3'],  # 高频，不显示的词汇列表
                                   ).generate(content_string)

    wordcloud_cctvnews.to_file(r'.\\tables\\cctvnews_2019.jpg')
    plt.imshow(wordcloud_cctvnews, interpolation='bilinear')
    plt.axis("off")
    pylab.show()

if __name__ == '__main__':
    main()