import datetime
import os
import time
from analysis_u.strategy.tushare_util import get_pro_client
import pandas as pd
from tqdm import tqdm
import json
from pyecharts.charts import Line
import pyecharts.options as opts
from loguru import logger
"""
避免打印时出现省略号
"""
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)


# 按照估值在选股一次，给出最合理的结论
# 获取当日涨停股票清单
# 由于无法直接获取指定日期涨停股票清单，通过pro.stk_limit和pro.daily两个接口的信息获取当日涨停股票信息
# 调用2次接口

def limit_list(trade_date):
    #  待添加时间变量
    today = trade_date
    # today = '20210909'
    pro = get_pro_client()
    # 获取当日涨停跌停价格
    limit_df = pro.stk_limit(trade_date=today)
    # 获取当日股价
    daily_df = pro.daily(trade_date=today)

    """
    # 将代码作为索引列
    limit_df = limit_df.set_index("ts_code")
    # 将代码作为索引列
    daily_df = daily_df.set_index("ts_code")
    # 获得涨停股票信息
    df = pd.concat([daily_df, limit_df], axis=1, join='inner')
    df_up = df[df.up_limit == df.close]
    # 重置索引，新增ts_code列
    df_up['ts_code'] = df_up.index.tolist()
   
    df = pd.merge(limit_df, daily_df, how='inner', on=['ts_code', 'trade_date'])
    df_up = df[df.up_limit == df.close]
    df_up.index = range(len(df_up))
    print("涨停股个数")
    print(df_up.shape[0])

    同理，可以获取跌停股票清单
    df_down = df[df.up_limit == df.close]
    print("跌停股个数")
    print(df_down.shape[0])
    """

    # 通过limit_list获取股票
    limit_df = pro.limit_list(trade_date=today)
    print("涨停停股个数")
    print(limit_df[(limit_df.limit == 'U')].shape[0])

    return limit_df


#  获取当前更新股市概念清单，用户快速概念对应的股票，股票对应的概念，分析相关的信息
#  调用1次接口

def get_concept(trade_date):
    #  待添加时间变量和是否更新变量,
    # today = '20210909'
    today = trade_date
    # 设置是否更新概念清单，True 不更新；False,重新下载概念清单
    download = True

    # 概念代码、代码概念、概念清单
    concept2code_dict = {}
    code2concept_dict = {}
    concept_name_dict = {}

    # 概念列表
    pro = get_pro_client()
    concept_df = pro.concept()

    # 当日行情
    hq_df = pro.daily(trade_date=today)

    # 获取概念清单
    # tqdm 为显示当前进度的库，非必要
    # download 为false 重新下载，True 不更新
    if not download:
        # 1、生成概念对应股票列表字典
        print('Generate concept2code~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        for ts in tqdm(concept_df.code.to_list()):
            for _ in range(3):
                try:
                    # 获取概念下的股票信息
                    code_df = pro.concept_detail(id=ts, fields='ts_code')
                except:
                    print('retry')
                else:
                    # 生成概念股票字典
                    code_list = code_df.ts_code.to_list()
                    concept2code_dict[ts] = code_list
                    time.sleep(0.5)
                    break
        #     with open("concept2code.json","r") as f:
        #     concept2code_dict=json.load(f)

        print('Generate code2concept~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # 2、生成股票代码对应概念字典
        for ts_code in tqdm(hq_df.ts_code):
            #     print(1)
            code2concept_dict[ts_code] = []
            for k, v in concept2code_dict.items():
                if ts_code in v:
                    code2concept_dict[ts_code].append(k)

        print('Generate concept_name_dict~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # 生成概念对应中文名字典
        # 应用dataframe的apply 函数和匿名行数 获取概念字段
        concept_name_dict = concept_df.groupby('code')['name'].apply(lambda x: x.iat[0]).to_dict()
        print(concept_name_dict)
        # 将上述字典存入json文件以备后用
        with open("concept2code.json", "w") as f:
            json.dump(concept2code_dict, f)

        with open("code2concept.json", "w") as f:
            json.dump(code2concept_dict, f)

        with open("concept_name_dict.json", "w") as f:
            json.dump(concept_name_dict, f)
    else:
        # download为False，直接加载字典
        with open("concept2code.json", "r") as f:
            concept2code_dict = json.load(f)
            # print(concept2code_dict)
        with open("code2concept.json", "r") as f:
            code2concept_dict = json.load(f)
            # print(code2concept_dict)
        with open("concept_name_dict.json", "r") as f:
            concept_name_dict = json.load(f)
            # print(concept_name_dict)
    # 形成概念清单，概念股票字典、股票对应概念字段，概念清单
    concept_list = [concept2code_dict, code2concept_dict, concept_name_dict]

    return concept_list


# 获取市场所有概念强度信息
# 调用1次接口
def get_total_concept_strength(today, concept_list):
    pro = get_pro_client()
    # 当日行情
    hq_df = pro.daily(trade_date=today)
    # 涨停榜
    limit_df = limit_list(trade_date=today)

    # limit_up_df = limit_df[(limit_df.limit == 'U') & (limit_df.name.str.contains('ST') == False)]

    #  概念代码、代码概念、概念清单
    # concept_list = get_concept(today)
    concept2code_dict = concept_list[0]
    code2concept_dict = concept_list[1]
    concept_name_dict = concept_list[2]
    concept_discount_num = 6  # 当概念股票数少于6，则需要打折热点强度；

    '''
    计算全市场概念强度 
    '''
    concept_pct_mean = []
    print("概念~~~~~~~~~~~~~~")
    for ts in tqdm(concept2code_dict.keys()):
        # 获取当前概念板块的股票涨停数据
        code_df = pd.DataFrame(concept2code_dict[ts], columns=['ts_code'])
        # 与当天的日线行情表合并
        temp1 = pd.merge(code_df, hq_df, how='left', on='ts_code')

        # 后续还要去除ST股票
        limitup_df = pd.merge(limit_df[(limit_df.limit == 'U') & (limit_df.name.str.contains('ST') == False)], code_df,
                              how='inner', on='ts_code')
        # 求出该板块涨停股票数
        limitup_num = len(limitup_df)

        if limitup_num > 0:
            print(ts)
            print("该板块涨停的股票个数及股票名单")
            print(limitup_num)
            print(limitup_df)

        # 计算龙头涨幅
        dragon_list = []
        if limitup_num >= 3:
            # 如果该板块涨停数大于3，取封板时间前3的股票作为龙一龙二龙三
            # 缺失开始涨停时间，暂时取得前3个股票的时间，后续可以优化
            # dragon_list = limitup_df.ts_code.head(3).to_list()

            dragon_list = limitup_df.sort_values(by='first_time').ts_code.head(3).to_list()
            print("涨停大于3个的版本龙头股票")
            print(dragon_list)
        else:
            # 如果该板块涨停数小于3，取涨停的股票和涨停股票之外最高涨幅的共3只股票作为龙一龙二龙三
            # dragon_list = limitup_df["ts_code"].to_list()
            dragon_list = limitup_df.sort_values(by='first_time').ts_code.to_list()
            nolimitup_dragon_num = 3 - limitup_num
            nolimitup_df_temp = temp1[~temp1["ts_code"].isin(limitup_df.ts_code)]
            # 按照涨幅对非涨停板的股票排序，

            ## 昨天的数据可能这里有问题,直接使用会导致错误
            nolimitup_df = nolimitup_df_temp.copy()
            nolimitup_df.sort_values("pct_chg", inplace=True)
            dragon_list += nolimitup_df.ts_code.head(nolimitup_dragon_num).to_list()
            # print("涨停小于3个的版本龙头股票")
            # print(dragon_list)
        # 计算龙头平均涨幅
        dragon_mean = temp1[temp1["ts_code"].isin(dragon_list)].pct_chg.mean()
        # 循环添加概念的强度信息
        concept_pct_mean.append({
            'code': ts,
            'num': len(temp1),
            'pct_mean': temp1.pct_chg.mean(),
            'limitup_num': limitup_num,
            'dragon': dragon_list,
            'dragon_mean': dragon_mean
        })

    concept_strength_df = pd.DataFrame(concept_pct_mean)
    # 增加1列concept_name，利用code在概念名单里取数据
    concept_strength_df['concept_name'] = concept_strength_df.code.apply(lambda x: concept_name_dict[x])

    def get_concept_strength(df):
        '''''
        计算每个概念的概念强度
        '''
        if df.pct_mean >= 0:
            try:
                # 若概念涨幅大于0，则考虑龙头的涨幅
                strength = round((df.pct_mean + df.dragon_mean) / 2)
                # 热点强度打折
                strength *= df.num / max(df.num, concept_discount_num)
                return strength
            except Exception as re:
                print(re)
        else:
            # 若概念涨幅小于0，则以概念涨幅作为其概念强度
            return df.pct_mean

    concept_strength_df['strength'] = concept_strength_df.apply(get_concept_strength, axis=1)
    return concept_strength_df


# 获取各个股概念强度
def get_one_code_concept_strength(today, code, concept_list, concept_strength_df):
    # today = '20210909'
    # concept_strength_df = get_total_concept_strength(today, concept_list)
    concept_strength_df = concept_strength_df
    # concept_list = get_concept(today)
    code2concept_dict = concept_list[1]
    ''''' 
    获取每个股票的所有概念强度总和 
    '''
    # 如果代码在代码概念字典里
    if code in code2concept_dict.keys():
        concept_listx = code2concept_dict[code]
        # 获取所有的概念及嘉
        return concept_strength_df[concept_strength_df.code.isin(concept_listx)].strength.sum()
    else:
        return pd.np.nan


def get_sta(concept_list, limit_up_df):
    concept_name_dict = concept_list[2]
    code2concept_dict = concept_list[1]
    concept2code_dict = concept_list[0]

    print("~~~~~~~~~~~~统计数据~~~~~~~~~~~~~~")
    result = []
    for k, v in concept2code_dict.items():
        limit_up_num = len(limit_up_df[limit_up_df.ts_code.isin(v)])
        concept_name = concept_name_dict[k]
        result.append({
            'code': k,
            '概念名称': concept_name,
            '涨停数': limit_up_num,
        })
    res_df = pd.DataFrame(result)

    print(res_df.sort_values('涨停数', ascending=False).head(20))


# today 时间，例：20210808
# concept_list 嵌套的字段
def get_Market_result(today, concept_list):
    pro = get_pro_client()

    # 参数
    today = today  # 开始时间
    dt = datetime.datetime.strptime(today, "%Y%m%d")  # 结束时间
    next_day = (dt + datetime.timedelta(days=1)).strftime("%Y%m%d")
    limit_up_df = limit_list(today)  # 涨停清单

    # 显示板块涨停数量统计
    get_sta(concept_list, limit_up_df)

    # 显示版块概念强度
    concept_strength_df = get_total_concept_strength(today, concept_list)
    concept_strength_df.sort_values("strength", inplace=True, ascending=False)
    print('查看所有版块概念强度')
    print(concept_strength_df)

    # 查看所有的个股强度
    hq_df = pro.daily(trade_date=today)  # 当日概念列表
    concept_name_dict = concept_list[2]
    code2concept_dict = concept_list[1]
    hq_df['strength'] = 0
    for ts in range(len(hq_df)):
        hq_df['strength'].iloc[ts] = get_one_code_concept_strength(today, hq_df['ts_code'].iloc[ts], concept_list,
                                                                   concept_strength_df)

    get_concept_name_list = lambda x: [concept_name_dict[code] for code in
                                       code2concept_dict[x]] if x in code2concept_dict.keys() else []
    hq_df['concept'] = hq_df.ts_code.apply(get_concept_name_list)
    print('查看所有个股概念强度')
    print(hq_df)

    # 查看概念强度前20个股
    strength_head20 = hq_df.copy()
    strength_head20 = strength_head20.sort_values(by='strength', ascending=False).head(20)
    strength_head20['concept'] = strength_head20.ts_code.apply(get_concept_name_list)
    print('查看概念强度前20个股')
    print(strength_head20.loc[:, ['ts_code', 'trade_date', 'pct_chg', 'strength', 'concept']])

    # 概念强度前20个股次日表现
    next_day_hq_df = pro.daily(trade_date=next_day)
    next_day_hq = pd.merge(strength_head20['ts_code'], next_day_hq_df, how='inner', on=['ts_code'])
    print('查看概念强度前20个股次日表现')
    print(next_day_hq.loc[:, ['ts_code', 'trade_date', 'pct_chg']])


def get_concept_trend(start_date, end_date, concept_list, concept_code_list):
    pro = get_pro_client()

    concept_name_dict = concept_list[2]
    concept2code_dict = concept_list[0]

    da_trade = pro.trade_cal(start_date=start_date, end_date=end_date, is_open=1)  # 获取交易日期

    x_data = da_trade["cal_date"].values
    # x_data = ['20210906', '20210907', '20210908', '20210909', '20210910']
    y_data_dict = {}

    print("开始趋势展示")
    concept_code_list = concept_code_list
    # concept_code_list = ['TS4', 'TS35']  # 军工 光伏
    for code in tqdm(concept_code_list):
        y_data_dict[concept_name_dict[code]] = []
    for trade_date in tqdm(x_data):
        hq_df = pro.daily(trade_date=trade_date)
        limit_price_df = pro.limit_list(trade_date=trade_date)
        """
        try:
            limit_price_df = pro.limit_list(**{
                "ts_code": "",
                "trade_date": trade_date,
                "start_date": "",
                "end_date": "",
                "offset": "",
                "limit": ""
            }, fields=[
                "trade_date",
                "ts_code",
                "up_limit",
                "down_limit"
            ])
        except Exception as re:
            print(re)
        """
        hq_df = pd.merge(hq_df, limit_price_df, how='inner', on=['ts_code', 'trade_date'])
        limit_up_df = hq_df[hq_df.limit == "U"]

        for code in concept_code_list:
            y_data_dict[concept_name_dict[code]].append(
                len(limit_up_df[limit_up_df.ts_code.isin(concept2code_dict[code])])
            )

    plot_name = '板块涨停可视化'
    # line = Line("900px", "1200px")
    line = Line().add_xaxis(xaxis_data=x_data)
    # line.width = 120
    #
    for k, v in y_data_dict.items():
        line.add_yaxis(
            series_name=k,
            y_axis=v,
            label_opts=opts.LabelOpts(is_show=False),
        )

    line.set_global_opts(
        title_opts=opts.TitleOpts(title=plot_name),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
        xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
    ).render_notebook()
    line.render()


def get_concept_trend_top10(start_date, end_date, concept_list):
    concept_strength_df = get_total_concept_strength(end_date, concept_list)
    concept_strength_df_top20 = concept_strength_df.sort_values(by='strength', ascending=False).head(6)
    concept_code_list_top20 = concept_strength_df_top20.code.tolist()
    get_concept_trend(start_date, end_date, concept_list, concept_code_list_top20)


# 如何获取龙头股，概念不清晰
def get_concept_stock_by_tm(trade_date):
    pro = get_pro_client()
    # 获取股票清单
    df_TS = pro.concept_detail(id='TS2', fields='ts_code,name')
    df = pro.daily_basic(trade_date=trade_date)
    concept_stock = pd.merge(df_TS, df, how='inner', on='ts_code')
    concept_stock.sort_values(by='total_mv', ascending=True)
    print(concept_stock.head(3))


def main():
    today = '20210930'  # 指定的日期

    concept_list = get_concept(today)  # 概念清单(为了避免多次调用接口，所以采用传参的方式)
    # 指定日期市场强度分析
    """ 
    get_Market_result(today, concept_list)     
    """
    start_date = 20210801  # 板块股票分析时间及结束时间
    # end_date = datetime.datetime.now().strftime('%Y%m%d')
    # concept_code_list = ['TS4', 'TS35']  # 军工 光伏
    get_concept_trend_top10(start_date, today, concept_list)


if __name__ == "__main__":
    main()
