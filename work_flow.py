# -*- encoding: UTF-8 -*-

import logging
import datetime
import analysis_u.trash.stock_increase_stratigy

from analysis_u.trash import get_cctv_news
from analysis_u.notices import stock_email


def process():
    logging.info("************************ process start ***************************************")
    get_cctv_news.update_cctv()
    stock_list = analysis_u.trash.stock_increase_stratigy.stock_increase()
    mail_title = datetime.datetime.today().strftime('%Y%m%d') + "选股策略"
    stock_list_html = stock_list.to_html(escape=True, index=False, sparsify=True, border=1, index_names=False,
                                         header=True)
    stock_email.send_mail(mail_title, stock_list_html)

    """
    try:
        all_data = ts.get_today_all()
        subset = all_data[['code', 'name', 'nmc']]
        subset.to_csv(settings.STOCKS_FILE, index=None, header=True)
        stocks = [tuple(x) for x in subset.values]
        statistics(all_data, stocks)
    except urllib.error.URLError as e:
        subset = pd.read_csv(settings.STOCKS_FILE)
        subset['code'] = subset['code'].astype(str)
        stocks = [tuple(x) for x in subset.values]

    if utils.need_update_data():
        utils.prepare()
        data_fetcher.run(stocks)
        check_exit()

    strategies = {
        '海龟交易法则': turtle_trade.check_enter,
        '放量上涨': enter.check_volume,
        # '突破平台': breakthrough_platform.check,
        # '均线多头': keep_increasing.check,
        # '停机坪': parking_apron.check,
        # '回踩年线': backtrace_ma250.check,
    }

    if datetime.datetime.now().weekday() == 0:
        strategies['均线多头'] = keep_increasing.check

    for strategy, strategy_func in strategies.items():
        check(stocks, strategy, strategy_func)
        time.sleep(2)
    """
    logging.info("************************ process   end ***************************************")


def main():
    process()


if __name__ == '__main__':
    main()
