import pandas_datareader.data  as web
import datetime
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
from matplotlib.font_manager
import FontProperties
import mpl_finance as mpf
import matplotlib
import numpy as np
matplotlib.style.use('ggplot')
matplotlib inline






def main():
    start = datetime.datetime(1980, 1, 1)
    end = datetime.datetime(2018, 8, 3)
    prices = web.get_data_yahoo('AAPL', start, end)

    # 预览股价趋势图
    prices['Close'].plot()
    plt.show()

if __name__ == '__main__':
    main()
