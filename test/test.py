import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import datetime as dt


def main():
    fig = plt.figure()
    ax2 = fig.add_subplot(212)
    date2_1 = dt.datetime(2008, 9, 23)
    date2_2 = dt.datetime(2008, 10, 3)
    delta2 = dt.timedelta(days=1)
    dates2 = mpl.dates.drange(date2_1, date2_2, delta2)
    y2 = np.random.rand(len(dates2))
    ax2.plot_date(dates2, y2, linestyle='-')
    dateFmt = mpl.dates.DateFormatter('%Y-%m-%d')
    ax2.xaxis.set_major_formatter(dateFmt)

    daysLoc = mpl.dates.DayLocator()
    hoursLoc = mpl.dates.HourLocator(interval=6)
    ax2.xaxis.set_major_locator(daysLoc)
    ax2.xaxis.set_minor_locator(hoursLoc)

    fig.autofmt_xdate(bottom=0.18)
    fig.subplots_adjust(left=0.18)

    ax1 = fig.add_subplot(211)
    date1_1 = dt.datetime(2008, 9, 23)
    date1_2 = dt.datetime(2009, 2, 16)
    delta1 = dt.timedelta(days=10)
    dates1 = mpl.dates.drange(date1_1, date1_2, delta1)
    y1 = np.random.rand(len(dates1))
    ax1.plot_date(dates1, y1, linestyle='--')
    monthsLoc = mpl.dates.MonthLocator()
    weeksLoc = mpl.dates.WeekdayLocator()
    ax1.xaxis.set_major_locator(monthsLoc)
    ax1.xaxis.set_minor_locator(weeksLoc)
    monthsFmt = mpl.dates.DateFormatter('%b')
    ax1.xaxis.set_major_formatter(monthsFmt)

    plt.show()


if __name__ == '__main__':
    main()
