import pandas as pd
from collector.tushare_util import get_pro_client

from matplotlib import pyplot as plt
from matplotlib.daet import DateFormatter
from matplotlib.finance import date2num, candlestick_ohlc


def get_stock_index():
    pro = get_pro_client()
    df = pro.get_k_data("300104")


def candlePlot(data, title=""):
    data["date"] = [date2num(pd.to_datetime(x)) for x in data.index]
    dataList = [tuple(x) for x in data[["date", "open", "high", "low", "close"]].values]

    ax = plt.subplot()
    ax.set_title(title)
    ax.xaxis.set_major_formatter(DateFormatter("%y-%m-%d"))
    candlestick_ohlc(ax, dataList, width=0.7, colorup="r", colordown="g")
    plt.setp(plt.gca().get_xticklabels(), rotation=50,
             horizontalalignment="center")
    fig = plt.gcf()
    fig.set_size_inches(20, 15)
    plt.grid(True)


def main():
    get_stock_index()


if __name__ == "__main__":
    main()
