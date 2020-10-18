from collector.tushare_util import get_pro_client
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
plt.rcParams['axes.unicode_minus'] = False


# 获取业绩预告信息
def stock_incr_report(date, incr_type):
    pro = get_pro_client()
    incr_type = incr_type

    print(incr_type)
    for value in date:
        ann_date = value.strftime('%Y%m%d')
        print(ann_date)
        df = pro.forecast(ann_date=ann_date, type=incr_type,
                          fields='ts_code,ann_date,type,p_change_min,p_change_max,net_profit_min')
        df.append(df)
    print(df)


def stock_quik_report():
    plt.rcParams['savefig.dpi'] = 300  # 图片像素
    plt.rcParams['figure.dpi'] = 300  # 分辨率
    # plt.style.use('ggplot')
    pro = get_pro_client()
    df = pro.express(ts_code='600000.SH')
    print(df.columns)

    print(df)
    df = df[len(df):None:-1]
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.set_title(df.ts_code[0], fontsize=18, backgroundcolor='000000',
                 fontweight='bold', color='white', verticalalignment="baseline")
    ax.set_xlabel('利润', fontsize=18, fontfamily='sans-serif', fontstyle='italic', color='r')
    ax.set_ylabel('报告日期', fontsize='x-large', fontstyle='oblique', color='r')
    ax.plot(df.ann_date, df.n_income, 'g--', label="利润")
    ax.legend(loc=3, labelspacing=2, handlelength=3, fontsize=14, shadow=True)

    ax2 = ax.twinx()  # this is the important function
    ax2.plot(df.ann_date, df.yoy_net_profit, 'r', label="盈利利润")
    ax2.set_ylabel('Y values for ln(x)')
    ax2.set_xlabel('Same X for both exp(-x) and ln(x)')
    ax2.legend(loc=3, labelspacing=2, handlelength=3, fontsize=14, shadow=True)
    ax.grid(linestyle="--", alpha=0.2)  # 网格线
    ax.tick_params("x", labelrotation=40)
    sns.set(style='darkgrid', font_scale=1.5)
    # plt.table(cellText=[['%1.2f' % xxx for xxx in xx] for xx in df.ann_date],  loc='bottom')

    plt.show()


def main():
    date = pd.date_range('20200930', '20201030')
    incr_type = '略增'
    # stock_incr_report(date, incr_type)
    stock_quik_report()


if __name__ == "__main__":
    main()
