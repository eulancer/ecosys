import pandas as pd
from tqdm import tqdm
import tushare as ts
import time
from datetime import datetime
import numpy as np
import json

from collector.tushare_util import get_pro_client
# 请更换为自己的token

pro = get_pro_client()

# today = datetime.today().strftime('%Y%m%d')
today = '20201203'
next_day = '20201204'
download = True  # 当需要更新概念-股票代码字典、股票代码-概念字典、概念-中文名称字典时，将其改为True
concept_discount_num = 6  # 当概念股票数少于6，则需要打折热点强度

# 当日行情
hq_df = pro.daily(trade_date=today)
# 涨停榜
limit_df = pro.limit_list(trade_date=today)
# 当日概念列表
concept_df = pro.concept()

concept2code_dict = {}
code2concept_dict = {}
concept_name_dict = {}

if download == False:
    # 下载每个概念对应的股票列表，不一定每天更新，一可段时间更新一次
    # 生成概念对应股票列表字典
    print('Generate concept2code')
    for ts in tqdm(concept_df.code.to_list()):
        for _ in range(3):
            try:
                code_df = pro.concept_detail(id=ts, fields='ts_code')
            except:
                print('retry')
            else:
                code_list = code_df.ts_code.to_list()
                concept2code_dict[ts] = code_list
                time.sleep(0.5)
                break
            #     with open("concept2code.json","r") as f:
    #         concept2code_dict=json.load(f)

    print('Generate code2concept')
    # 生成股票代码对应概念字典
    for ts_code in tqdm(hq_df.ts_code):
        #     print(1)
        code2concept_dict[ts_code] = []
        for k, v in concept2code_dict.items():
            if ts_code in v:
                code2concept_dict[ts_code].append(k)

    print('Generate concept_name_dict')
    # 生成概念对应中文名字典
    concept_name_dict = concept_df.groupby('code')['name'].apply(lambda x: x.iat[0]).to_dict()
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

    with open("code2concept.json", "r") as f:
        code2concept_dict = json.load(f)

    with open("concept_name_dict.json", "r") as f:
        concept_name_dict = json.load(f)


def get_total_concept_strength(today, download=False):
    '''''
    计算全市场概念强度
    '''
    concept_pct_mean = []
    for ts in tqdm(concept2code_dict.keys()):
        # 取出每个概念对应股票列表
        code_df = pd.DataFrame(concept2code_dict[ts], columns=['ts_code'])

        # 与当天的日线行情表合并
        temp1 = pd.merge(code_df, hq_df, how='left', on='ts_code')

        # 提取该概念当天非st股的涨停股票
        limitup_df = pd.merge(limit_df[(limit_df.limit == 'U') & (limit_df.name.str.contains('ST') == False)], code_df,
                              how='inner', on='ts_code')

        # 求出该板块涨停股票数
        limitup_num = len(limitup_df)

        # 计算龙头涨幅
        dragon_list = []
        if limitup_num >= 3:
            # 如果该板块涨停数大于3，取封板时间前3的股票作为龙一龙二龙三
            dragon_list = limitup_df.sort_values(by='first_time').ts_code.head(3).to_list()
        else:
            # 如果该板块涨停数大于3，取涨停的股票和涨停股票之外最高涨幅的共3只股票作为龙一龙二龙三
            dragon_list = limitup_df.sort_values(by='first_time').ts_code.to_list()
            nolimitup_dragon_num = 3 - limitup_num
            nolimitup_df = temp1[~temp1.ts_code.isin(limitup_df.ts_code)]
            dragon_list += nolimitup_df.ts_code.head(nolimitup_dragon_num).to_list()

            # 计算龙头平均涨幅
        dragon_mean = temp1[temp1.ts_code.isin(dragon_list)].pct_chg.mean()

        concept_pct_mean.append({
            'code': ts,
            'num': len(temp1),
            'pct_mean': temp1.pct_chg.mean(),
            'limitup_num': limitup_num,
            'dragon': dragon_list,
            'dragon_mean': dragon_mean
        })

    concept_strength_df = pd.DataFrame(concept_pct_mean)
    concept_strength_df['concept_name'] = concept_strength_df.code.apply(lambda x: concept_name_dict[x])

    def get_concept_strength(df):
        '''''
        计算每个概念的概念强度
        '''
        if df.pct_mean >= 0:
            # 若概念涨幅大于0，则考虑龙头的涨幅
            strength = round((df.pct_mean + df.dragon_mean) / 2)
            # 热点强度打折
            strength *= df.num / max(df.num, concept_discount_num)
            return strength
        else:
            # 若概念涨幅小于0，则以概念涨幅作为其概念强度
            return df.pct_mean

    concept_strength_df['strength'] = concept_strength_df.apply(get_concept_strength, axis=1)
    return concept_strength_df


def get_one_code_concept_strength(code):
    '''''
    获取每个股票的所有概念强度总和
    '''
    if code in code2concept_dict.keys():
        concept_list = code2concept_dict[code]
        return concept_strength_df[concept_strength_df.code.isin(concept_list)].strength.sum()
    else:
        return np.nan


if __name__ == '__main__':
    concept_strength_df = get_total_concept_strength(today)
    print('查看所有版块概念强度')
    print(concept_strength_df)

    hq_df['strength'] = hq_df.ts_code.apply(get_one_code_concept_strength)
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