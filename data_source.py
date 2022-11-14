import yfinance as yf


def fetch_data(data_source, stock_list, start_date, end_date, interval):
    """

    :param data_source:
    :param stock_list:
    :param start_date:
    :param end_date:
    :param interval:
    :return:
    """
    out_data = dict()
    if data_source == 'yahoo':
        for each_stock in stock_list:
            stock = yf.Tickers()