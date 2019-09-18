from CAL.PyCAL import *
from pandas import Series, DataFrame, concat
import pandas as pd
import numpy as np
import seaborn as sns

sns.set_style('white')
from matplotlib import pylab
import time
import math
from collector.tushare_util import get_pro_client
#来源于以下地址 https://uqer.io/community/share/55b4b34bf9f06c91f818c5e9


def getHistDayOptions(var, date):
    # 使用DataAPI.OptGet，拿到已退市和上市的所有期权的基本信息；
    # pro = ts.pro_api('your token')
    # df = pro.opt_basic(exchange='DCE', fields='ts_code,name,exercise_type,list_date,delist_date')

    # 同时使用DataAPI.MktOptdGet，拿到历史上某一天的期权成交信息；
    # pro = ts.pro_api('your token')
    # df = pro.opt_daily(trade_date='20181212')

    # 返回历史上指定日期交易的所有期权信息，包括：
    # optID  varSecID  contractType  strikePrice  expDate  tradeDate  closePrice
    # 以optID为index。
    vixDateStr = date.toISO().replace('-', '')
    optionsMkt = DataAPI.MktOptdGet(tradeDate=vixDateStr, field=[u"optID", "tradeDate", "closePrice"], pandas="1")
    optionsMkt = optionsMkt.set_index(u"optID")
    optionsMkt.closePrice.name = u"price"

    optionsID = map(str, optionsMkt.index.values.tolist())
    fieldNeeded = ["optID", u"varSecID", u'contractType', u'strikePrice', u'expDate']
    optionsInfo = DataAPI.OptGet(optID=optionsID, contractStatus=[u"DE", u"L"], field=fieldNeeded, pandas="1")
    optionsInfo = optionsInfo.set_index(u"optID")
    options = concat([optionsInfo, optionsMkt], axis=1, join='inner').sort_index()
    return options[options.varSecID == var]


def getNearNextOptExpDate(options, vixDate):
    # 找到options中的当月和次月期权到期日；
    # 用这两个期权隐含的未来波动率来插值计算未来30隐含波动率，是为市场恐慌指数VIX；
    # 如果options中的最近到期期权离到期日仅剩1天以内，则抛弃这一期权，改
    # 选择次月期权和次月期权之后第一个到期的期权来计算。
    # 返回的near和next就是用来计算VIX的两个期权的到期日
    optionsExpDate = Series(options.expDate.values.ravel()).unique().tolist()
    near = min(optionsExpDate)
    optionsExpDate.remove(near)
    if Date.parseISO(near) - vixDate < 1:
        near = min(optionsExpDate)
        optionsExpDate.remove(near)
    next = min(optionsExpDate)
    return near, next


def getStrikeMinCallMinusPutClosePrice(options):
    # options 中包括计算某日VIX的call和put两种期权，
    # 对每个行权价，计算相应的call和put的价格差的绝对值，
    # 返回这一价格差的绝对值最小的那个行权价，
    # 并返回该行权价对应的call和put期权价格的差
    call = options[options.contractType == u"CO"].set_index(u"strikePrice").sort_index()
    put = options[options.contractType == u"PO"].set_index(u"strikePrice").sort_index()
    callMinusPut = call.closePrice - put.closePrice
    strike = abs(callMinusPut).idxmin()
    priceDiff = callMinusPut[strike]
    return strike, priceDiff


def calSigmaSquare(options, FF, R, T):
    # 计算某个到期日期权对于VIX的贡献sigma；
    # 输入为期权数据options，FF为forward index price，
    # R为无风险利率， T为期权剩余到期时间
    callAll = options[options.contractType == u"CO"].set_index(u"strikePrice").sort_index()
    putAll = options[options.contractType == u"PO"].set_index(u"strikePrice").sort_index()
    callAll['deltaK'] = 0.05
    putAll['deltaK'] = 0.05

    # Interval between strike prices
    index = callAll.index
    if len(index) < 3:
        callAll['deltaK'] = index[-1] - index[0]
    else:
        for i in range(1, len(index) - 1):
            callAll['deltaK'].ix[index[i]] = (index[i + 1] - index[i - 1]) / 2.0
        callAll['deltaK'].ix[index[0]] = index[1] - index[0]
        callAll['deltaK'].ix[index[-1]] = index[-1] - index[-2]
    index = putAll.index
    if len(index) < 3:
        putAll['deltaK'] = index[-1] - index[0]
    else:
        for i in range(1, len(index) - 1):
            putAll['deltaK'].ix[index[i]] = (index[i + 1] - index[i - 1]) / 2.0
        putAll['deltaK'].ix[index[0]] = index[1] - index[0]
        putAll['deltaK'].ix[index[-1]] = index[-1] - index[-2]

    call = callAll[callAll.index > FF]
    put = putAll[putAll.index < FF]
    FF_idx = FF
    if not put.empty:
        FF_idx = put.index[-1]
        put['closePrice'].iloc[-1] = (putAll.ix[FF_idx].closePrice + callAll.ix[FF_idx].closePrice) / 2.0

    callComponent = call.closePrice * call.deltaK / call.index / call.index
    putComponent = put.closePrice * put.deltaK / put.index / put.index
    sigma = (sum(callComponent) + sum(putComponent)) * np.exp(T * R) * 2 / T
    sigma = sigma - (FF / FF_idx - 1) ** 2 / T
    return sigma


def calDayVIX(optionVarSecID, vixDate):
    # 利用CBOE的计算方法，计算历史某一日的未来30日期权波动率指数VIX

    # The risk-free interest rates
    R_near = 0.06
    R_next = 0.06
    # 拿取所需期权信息
    options = getHistDayOptions(optionVarSecID, vixDate)
    termNearNext = getNearNextOptExpDate(options, vixDate)
    optionsNearTerm = options[options.expDate == termNearNext[0]]
    optionsNextTerm = options[options.expDate == termNearNext[1]]
    # time to expiration
    T_near = (Date.parseISO(termNearNext[0]) - vixDate) / 365.0
    T_next = (Date.parseISO(termNearNext[1]) - vixDate) / 365.0
    # the forward index prices
    nearPriceDiff = getStrikeMinCallMinusPutClosePrice(optionsNearTerm)
    nextPriceDiff = getStrikeMinCallMinusPutClosePrice(optionsNextTerm)
    near_F = nearPriceDiff[0] + np.exp(T_near * R_near) * nearPriceDiff[1]
    next_F = nextPriceDiff[0] + np.exp(T_next * R_next) * nextPriceDiff[1]
    # 计算不同到期日期权对于VIX的贡献
    near_sigma = calSigmaSquare(optionsNearTerm, near_F, R_near, T_near)
    next_sigma = calSigmaSquare(optionsNextTerm, next_F, R_next, T_next)

    # 利用两个不同到期日的期权对VIX的贡献sig1和sig2，
    # 已经相应的期权剩余到期时间T1和T2；
    # 差值得到并返回VIX指数(%)
    w = (T_next - 30.0 / 365.0) / (T_next - T_near)
    vix = T_near * w * near_sigma + T_next * (1 - w) * next_sigma
    return 100 * np.sqrt(vix * 365.0 / 30.0)


def getHistVIX(beginDate, endDate):
    # 计算历史一段时间内的VIX指数并返回
    optionVarSecID = u"510050.XSHG"
    cal = Calendar('China.SSE')
    dates = cal.bizDatesList(beginDate, endDate)
    histVIX = pd.DataFrame(0.0, index=dates, columns=['VIX'])
    histVIX.index.name = 'date'
    for date in histVIX.index:
        histVIX['VIX'][date] = calDayVIX(optionVarSecID, date)
    return histVIX


def getDayVIX(date):
    optionVarSecID = u"510050.XSHG"
    return calDayVIX(optionVarSecID, date)
