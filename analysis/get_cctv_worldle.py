# -*- coding: utf-8 -*-
import pandas as pd
import os
import time
from wordcloud import WordCloud
import re
import matplotlib.pyplot as plt
import pylab  # matplotlib下的模块pyplot和pylab
import config


def main():
    content_string=worldle_content(20190101, 20190922)
    show_wordcloud(content_string)


def worldle_content(start_day,end_day):
    sql="select * from stock_cctv_news where date>='%s' and date<='%s'"% (start_day, end_day)
    data = pd.read_sql(sql=sql, con=config.engine)
    series_content = data['content']
    content_all_list = []  # 存放分词后的词汇
    content_string = ''

    for content in series_content:  # 遍历Series中的每一行congtent（每一天的content）
        content_ = str(content)  # 转为字符
        content = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "",content)  # 去除标点符号
        content_string = content_string + content  # 汇总

    return content_string


def show_wordcloud(content_string):
    # 为了让 wordcloud 支持显示中文，需指定Windows7汉字字体
    font = r'C:\Windows\Fonts\simfang.ttf'
    wordcloud_cctvnews = WordCloud(collocations = False,
                                   font_path = font,
                                   width = 1400,
                                   height = 1400,
                                   margin = 2,
                                   background_color = 'white',
                                   stopwords = ['1'],  # 高频，不显示的词汇列表
                                   ).generate(content_string)

    wordcloud_cctvnews.to_file(r'.\\tables\\cctvnews_2019.jpg')
    plt.imshow(wordcloud_cctvnews, interpolation='bilinear')
    plt.axis("off")
    pylab.show()

if __name__ == '__main__':
    main()