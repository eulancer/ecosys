import pandas as pd
import numpy as np
from datetime import datetime
import scipy.stats as stats
import seaborn as sns
import mplfinance as mpf
import matplotlib.pyplot as plt

from collector.tushare_util import get_pro_client

# 正常显示画图时出现的中文和负号
from pylab import mpl
from pyecharts import Kline, Gauge, Bar

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
plt.rcParams['axes.unicode_minus'] = False


# 获取数据函数

# 获取股票数据
def get_stock_data(ts_code, start_date, end_date):
    pro = get_pro_client()
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df.index = pd.to_datetime(df.trade_date)
    print(df)
    return df


# 获取指数数据
def index_data(ts_code, start_date, end_date):
    df = get_index_data(ts_code, start_date, end_date)
    df.index = range(len(df))
    df = df[len(df):None:-1]
    return df


def get_index_data(ts_code, start_date, end_date):
    pro = get_pro_client()
    ts_code = ts_code
    start_date = start_date
    end_date = end_date
    df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df.index = pd.to_datetime(df.trade_date)
    return df


# 计算日对数收益率
def log_ret(df):
    loges = np.log(df / df.shift(1))[1:]
    return loges


# 将日收益率转换为月收益率
def month_rate(loges):
    date = []
    d = list(loges.index)
    for i in range(0, np.size(loges)):
        t = ''.join([d[i].strftime("%Y"), d[i].strftime("%m"), "01"])
        date.append(datetime.strptime(t, "%Y%m%d"))
    y = pd.DataFrame(loges.values, date, columns=['月收益率'])
    ret_M = y.groupby(y.index).sum()
    return ret_M


# 将日收益率转换为年收益率
def annual_rate(loges):
    year = []
    d = list(loges.index)
    for i in range(0, np.size(loges)):
        year.append(d[i].strftime("%Y"))
    y = pd.DataFrame(loges.values, year, columns=['年收益率'])
    ret_Y = np.exp(y.groupby(y.index).sum()) - 1
    return ret_Y


# ### 查看K线图
def plot_K(df):
    df = df
    data = pd.DataFrame()
    data['Open'] = df['open']
    data['High'] = df['high']
    data['Low'] = df['low']
    data['Close'] = df['close']
    data['Volume'] = df['vol']
    data['low'] = df['low']
    data.index = pd.DatetimeIndex(df.trade_date)
    mpf.plot(data, type='candle', style='charles', mav=(2, 5, 10), volume=True,
             show_nontrading=False)


# 月份效应检验

# 相关性检验
def T_analyse(df, df_m):
    df = df
    df.index = pd.to_datetime(df.trade_date)
    lret = log_ret(df.close)
    ret_M = month_rate(lret)
    # 每年不同月份收益率
    df_m = pd.DataFrame()
    for i in range(1, 13):
        ret0 = ret_M[ret_M.index.month == i]
        df_m[str(i) + '月份'] = ret0['月收益率'].values
    df_m.describe().round(3)
    # 除了某一年剩余年份收益率
    df_exm = pd.DataFrame()
    for i in range(1, 13):
        ret1 = ret_M[ret_M.index.month != i]
        df_exm['ex' + str(i)] = ret1['月收益率'].values
    print(df_exm)

    t1, p1 = stats.ttest_1samp(df_m, 0.0)
    t2, p2 = stats.ttest_ind(df_m, df_exm, equal_var=False)
    l = np.array([t1, p1, t2, p2]).T
    df_t = pd.DataFrame(l, index=range(1, 13), columns=['单样本t检验_t值',
                                                        '单样本t检验_p值', '双样本t检验_t值', '双样本t检验_p值'])
    # 绘制热力相关图
    print(df_t)
    plot_corr(df_t)


def month_view(df):
    df = df
    df.index = pd.to_datetime(df.trade_date)
    lret = log_ret(df.close)
    # 月收益率
    ret_M = month_rate(lret)
    print(ret_M)

    # 每年不同月份收益率
    df_m = pd.DataFrame()
    for i in range(1, 13):
        ret0 = ret_M[ret_M.index.month == i]
        df_m[str(i) + '月份'] = ret0['月收益率'].values
    df_m.describe().round(3)
    print("dfm")
    print(df_m.describe().round(3))
    # 计算每个上周概率
    pro = []
    al = len(df_m)
    for i in df_m.columns:
        up = df_m[df_m[i] > 0][i].count()
        r = round((up / al) * 100, 2)
        pro.append(r)
    v1 = pro

    # 绘制个月份上涨概率
    plt.bar(range(1, 13), v1, align='center')
    plt.title('year bar')
    plt.ylabel('Up rate')
    plt.xlabel('month')
    # 标注标签值
    for i in range(1, 13):
        plt.text(i, v1[i - 1], v1[i - 1],
                 fontsize=10, color="black", style="italic", weight="light",
                 verticalalignment='center', horizontalalignment='right', rotation=0)
    plt.show()


# 年度收益率
def year_view(df):
    df = df
    df.index = pd.to_datetime(df.trade_date)
    # 对数收益率
    lret = log_ret(df.close)
    # 年收益率
    ret_Y = annual_rate(lret)
    ret_Y.describe().T
    ret_Y.sort_values('年收益率')[:5].T
    ret_Y.sort_values('年收益率', ascending=False)[:5].T
    ratio = int(ret_Y[ret_Y['年收益率'] > 0].count()) / len(ret_Y)
    print(f'上涨年份占比{ratio * 100}%')

    attr = list(ret_Y.index)
    v = list((ret_Y['年收益率'] * 100).round(2))
    plt.bar(x=attr, height=v, label='年度收益率', color='steelblue', alpha=0.8)
    # 在柱状图上显示具体数值, ha参数控制水平对齐方式, va控制垂直对齐方式
    for x1, yy in zip(attr, v):
        plt.text(x1, yy + 1, str(yy), ha='center', va='bottom', fontsize=8, rotation=0)
    # 设置标题
    plt.title("年度收益")
    # 为两条坐标轴设置名称
    plt.xlabel("年份")
    plt.ylabel("收益率")
    # 显示图例
    plt.legend()
    plt.show()


# 指数分析
def index_ana_analyst(codes, start_date, end_date):
    for value in codes:
        zs = get_index_data(value, start_date, end_date)
        zs = zs[len(zs):None:-1]
        # 对数收益率
        lret = log_ret(zs.close)
        # 年收益率
        ret_Y = annual_rate(lret)
        attr = list(ret_Y.index)
        print(zs)
        plt.plot(attr, ret_Y, marker='o', markersize=3)
        plt.xlabel('时间')  # x轴标题
        plt.ylabel('收益率')  # Y轴标题
    plt.legend(codes)
    plt.show()


def index_month_analyst(codes, start_date, end_date):
    for value in codes:
        df = get_index_data(value, start_date, end_date)
        df.index = pd.to_datetime(df.trade_date)
        df = df[len(df):None:-1]
        lret = log_ret(df.close)
        # 月收益率
        ret_M = month_rate(lret)
        attr = list(ret_M.index)
        plt.plot(attr, ret_M, marker='o', markersize=3)
        plt.xlabel('时间')  # x轴标题
        plt.ylabel('收益率')  # Y轴标题
    plt.legend(codes)
    plt.show()


# 绘制热力图
def plot_corr(df):
    dfData = df.corr()
    plt.subplots(figsize=(9, 9))
    sns.heatmap(dfData, annot=True, vmax=1, square=True, cmap='Reds')
    plt.savefig('相关系数热力图.png')
    plt.show()


def date_trans(date):
    d = []
    for i in range(0, len(date)):
        d.append(''.join([date[i].strftime("%Y"),
                          date[i].strftime("%m")
                             , date[i].strftime("%d")]))
    return d


def main():
    ts_code = '000001.SH'
    start_date = 20110101
    end_date = 20200101
    df = index_data(ts_code, start_date, end_date)
    # plot_K(df)
    month_view(df)
    year_view(df)

    # 其他指数
    #codes = ['000001.SH', '000300.SH', '399005.SZ', '399006.SZ', '399005.SZ', '399006.SZ']
    codes = ['000001.SH']
    index_ana_analyst(codes, start_date, end_date)
    index_month_analyst(codes, start_date, end_date)
    # 上证指数 000001.SH;
    # 上证300 000300.SH;
    # 深圳指数 ：399005.SZ
    # 深圳指数 ：399006.SZ
    # 中小板：399005.SZ;
    # 创业板：399006.SZ;


if __name__ == "__main__":
    main()
