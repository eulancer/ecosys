import os
import time
from collector.tushare_util import get_pro_client
import pandas as pd
from tqdm import tqdm
import json

"""
避免打印时出现省略号
"""
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)


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
    """
    df = pd.merge(limit_df, daily_df, how='inner', on=['ts_code', 'trade_date'])
    df_up = df[df.up_limit == df.close]
    df_up.index = range(len(df_up))
    print("涨停股个数")
    print(df_up.shape[0])

    """
    同理，可以获取跌停股票清单
    df_down = df[df.up_limit == df.close]
    print("跌停股个数")
    print(df_down.shape[0])
    """
    return df_up


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

    #  概念代码、代码概念、概念清单
    concept2code_dict = concept_list[0]
    code2concept_dict = concept_list[1]
    concept_name_dict = concept_list[2]
    concept_discount_num = 6  # 当概念股票数少于6，则需要打折热点强度；

    '''
    计算全市场概念强度 
    '''

    concept_pct_mean = []

    for ts in tqdm(concept2code_dict.keys()):
        print("概念~~~~~~~~~~~~~~")
        print(concept_name_dict[ts])

        # 获取当前概念板块的股票涨停数据
        ## 取出每个概念对应股票列表
        code_df = pd.DataFrame(concept2code_dict[ts], columns=['ts_code'])
        # 与当天的日线行情表合并
        temp1 = pd.merge(code_df, hq_df, how='left', on='ts_code')
        ##提取该概念当天股的涨停股票
        ## ~~~~~~~~~~后续还要去除ST股票
        limitup_df = pd.merge(limit_df, code_df, how='inner', on='ts_code')

        ## 求出该板块涨停股票数
        limitup_num = len(limitup_df)
        print("该板块涨停的股票个数及股票名单")
        print(limitup_num)
        print(limitup_df)

        # 计算龙头涨幅
        dragon_list = []
        if limitup_num >= 3:
            # 如果该板块涨停数大于3，取封板时间前3的股票作为龙一龙二龙三
            # 缺失开始涨停时间，暂时取得前3个股票的时间，后续可以优化
            dragon_list = limitup_df.ts_code.head(3).to_list()
            print("涨停大于3个的版本龙头股票")
            print(dragon_list)
        else:
            # 如果该板块涨停数小于3，取涨停的股票和涨停股票之外最高涨幅的共3只股票作为龙一龙二龙三
            dragon_list = limitup_df["ts_code"].to_list()
            nolimitup_dragon_num = 3 - limitup_num
            nolimitup_df = temp1[~temp1["ts_code"].isin(limitup_df.ts_code)]
            # 按照涨幅对非涨停板的股票排序，
            ## 昨天的数据可能这里有问题
            nolimitup_df.sort_values("pct_chg", inplace=True)
            dragon_list += nolimitup_df.ts_code.head(nolimitup_dragon_num).to_list()
            print("涨停小于3个的版本龙头股票")
            print(dragon_list)
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
def get_one_code_concept_strength(code, concept_list, concept_strength_df):
    #
    today = '20210909'
    # concept_strength_df = get_total_concept_strength(today, concept_list)
    concept_strength_df = concept_strength_df
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

    print("concept_list[0]~~~~~~~~~~~~~~~~~~~~~")
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


#  典型板块强度跟踪
#  按照估值在选股一次，给出最合理的结论


def main():
    today = '20210910'
    next_day = '20210911'
    pro = get_pro_client()
    limit_up_df = limit_list(today)
    #  概念清单
    concept_list = get_concept(today)

    get_sta(concept_list, limit_up_df)

    concept_strength_df = get_total_concept_strength(today, concept_list)
    concept_strength_df.sort_values("strength", inplace=True, ascending=False)
    print('查看所有版块概念强度')
    print(concept_strength_df)

    # 当日概念列表

    hq_df = pro.daily(trade_date=today)
    print(hq_df)
    concept_name_dict = concept_list[2]
    code2concept_dict = concept_list[1]
    ###
    ### 调用接口次数过多，需要优化

    ##### 查看所有的个股强度
    """
    hq_df['strength'] = hq_df.ts_code.apply(
        lambda x: get_one_code_concept_strength(x, concept_list, concept_strength_df))
    """
    hq_df['strength'] = 0
    for ts in range(len(hq_df)):
        hq_df['strength'].iloc[ts] = get_one_code_concept_strength(hq_df['ts_code'].iloc[ts], concept_list,
                                                                   concept_strength_df)
        print("ts_______________________-")
        print(ts)

    get_concept_name_list = lambda x: [concept_name_dict[code] for code in
                                       code2concept_dict[x]] if x in code2concept_dict.keys() else []
    hq_df['concept'] = hq_df.ts_code.apply(get_concept_name_list)
    print('查看所有个股概念强度')
    print(hq_df)

    strength_head20 = hq_df.sort_values(by='strength', ascending=False).head(20)
    strength_head20['concept'] = strength_head20.ts_code.apply(get_concept_name_list)
    print('查看概念强度前20个股')
    print(strength_head20.loc[:, ['ts_code', 'trade_date', 'pct_chg', 'strength', 'concept']])

    next_day_hq_df = pro.daily(trade_date=next_day)
    print('查看概念强度前20个股次日表现')
    print(next_day_hq_df[next_day_hq_df.ts_code.isin(strength_head20.ts_code)].loc[:,
          ['ts_code', 'trade_date', 'pct_chg']])


if __name__ == "__main__":
    main()