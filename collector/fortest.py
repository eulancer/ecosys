import os
import time
from collector.tushare_util import get_pro_client
import pandas as pd
from tqdm import tqdm
import json


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



def concept():
    concept2code_dict = {}
    code2concept_dict = {}
    concept_name_dict = {}

    # 当日概念列表
    pro = get_pro_client()
    concept_df = pro.concept()

    # 当日行情
    today = '20210908'
    hq_df = pro.daily(trade_date=today)

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


    print(concept_name_dict)


def test():
    pro = get_pro_client()
    # 涨停榜
    today = '20210908'
    # 获取当日涨停跌停价格
    limit_df = pro.stk_limit(trade_date=today)
    limit_df = limit_df.set_index("ts_code")
    # 获取当日股价
    daily_df = pro.daily(trade_date=today)
    daily_df = daily_df.set_index("ts_code")

    # 获得股票列表
    df = pd.concat([daily_df, limit_df], axis=1, join='inner')
    # print(df)
    df_up = df[df.down_limit == df.close]
    # 当日概念列表
    print("涨停股个数")
    print(df_up.shape[0])
    df_down = df[df.up_limit == df.close]
    print("跌停股个数")
    print(df_down.shape[0])

    concept_df = pro.concept()
    print(concept_df)

def main():
    concept()

if __name__ == "__main__":
    main()
