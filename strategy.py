import datetime
import pandas as pd
import yfinance as yf

valid_stocks = None
try:
    valid_stocks = list(pd.read_csv('valid_stocks.csv', index_col=0).iloc[:, 0])
except:
    # get the list of valid Chinese ADR stocks
    stock_list = pd.read_excel('US Chinese Stocks.xlsx')
    stock_list = stock_list[stock_list.ISIN.notna()]
    stock_list['Ticker'] = stock_list['RIC'].str.split('.').str[0]
    stock_list = stock_list[stock_list['Type of Equity'] == 'American Depository Receipt']

    test_name_dict = dict()
    for each_stock in list(stock_list['Ticker']):
        temp = yf.download(each_stock, period="1d", interval="1d", progress=False)
        test_name_dict[each_stock] = temp.iloc[0, 3] if len(temp) > 0 else -1
    valid_stocks = [k for k, v in test_name_dict.items() if v != -1]
    pd.DataFrame(valid_stocks).to_csv('valid_stocks.csv')

print(valid_stocks)
