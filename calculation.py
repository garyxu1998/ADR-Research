import datetime
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# Read Stock list and filter
stock_list = pd.read_excel('US Chinese Stocks.xlsx')
stock_list = stock_list[stock_list.ISIN.notna()]
stock_list['Ticker'] = stock_list['RIC'].str.split('.').str[0]
stock_list = stock_list[stock_list['Type of Equity'] == 'American Depository Receipt']

short_list = stock_list.head(10)
stocks = yf.Tickers(list(short_list.Ticker))
stocks.history(period='1mo', interval='1d')

yf.download(prepost=True, tickers=list(short_list.Ticker), period='1d', interval='1h')

# fig = go.Figure(data=go.Scatter(x=jd_hist.index, y=jd_hist['Close'], mode='lines'))
# fig.show()


data = yf.download(tickers='JD', start='2022-01-01', end='2022-06-30', interval='1h')

data_9am = data.iloc[::7]
data_9am['rate'] = (data_9am['Close'] - data_9am['Open']) / data_9am['Open']

data_10am = data.iloc[1::7]
# data_10am['rate'] = (data_10am['Close'] - data_10am['Open'])/data_10am['Open']
data_10am.loc[:, 'rate'] = data_10am.apply(lambda row: (row.Close - row.Open) / row.Open, axis=1)

abs(data_10am.rate).mean()
# Test if the market overreact during the pre-market and the first hour

data_3pm = data.iloc[6::7]

# 重新开始！

# 取JD分时数据，包括premarket

# jd = yf.Ticker('JD')
# jd_hist = jd.history(prepost=True, period='3mo', interval='1h')


data = yf.download(tickers='JD', start='2022-01-01', end='2022-06-30', interval='1h', prepost=True)
jd_hist = data
#
# 算9: 30
# 之前(premarket)
# 的return

# 复制一下
jd_hist_calc_premarket = jd_hist.copy()

jd_hist_calc_premarket['time'] = jd_hist_calc_premarket.index.time

jd_hist_calc_premarket['date'] = jd_hist_calc_premarket.index.date

jd_930_4 = jd_hist_calc_premarket[(jd_hist_calc_premarket.time == datetime.time(hour=4)) | (
        jd_hist_calc_premarket.time == datetime.time(hour=9, minute=0))]

temp = dict()
for each_date in jd_930_4.date.unique():
    pre_open = float(jd_930_4[(jd_930_4.time == datetime.time(hour=4)) & (jd_930_4.date == each_date)]['Open'])
    pre_close = float(
        jd_930_4[(jd_930_4.time == datetime.time(hour=9, minute=0)) & (jd_930_4.date == each_date)]['Close'])
    temp[each_date] = (pre_close - pre_open) / pre_open

jd_premarket_ret = pd.DataFrame.from_dict(data=temp, orient='index', columns=['Premarket Return'])

jd_premarket_movement = jd_premarket_ret[abs(jd_premarket_ret['Premarket Return']) > 0.05].copy()

# 算9: 30 - 10:30
# 的收益

jd_1030_930 = jd_hist_calc_premarket[jd_hist_calc_premarket.time == datetime.time(hour=9, minute=30)].copy()

jd_1030_930['return'] = (jd_1030_930['Close'] - jd_1030_930['Open']) / jd_1030_930['Open']

jd_first_hour = jd_1030_930[abs(jd_1030_930['return']) > 0.05][['date', 'return']]

jd_first_hour.set_index('date')

# ↑ 上面算完了pre - market和9: 30 - 10:30
# 的，接下来算第二天卖掉的收益
# 1.
# 拿到第二天的日期（要一个日期list）
# 2.
# 把
# premarket
# 和第一个小时的分开
# 3.

# trading days list
trading_days = list(yf.download('^GSPC', start='2018-01-01', interval='1d').index.date)


def get_next_trading_date(curr_date):
    return trading_days[trading_days.index(curr_date) + 1]


print(get_next_trading_date(datetime.date(2018, 1, 3)))

jd_first_hour['next_trading_date'] = jd_first_hour.apply(lambda d: get_next_trading_date(d.name.date()), axis=1)

jd_first_hour['this_1030'] = jd_first_hour.apply(lambda row: jd_hist_calc_premarket[
    (jd_hist_calc_premarket['date'] == row['date']) & (
            jd_hist_calc_premarket['time'] == datetime.time(hour=10, minute=30))].iloc[0, 0], axis=1)
# iloc[0,0]: 取10:30的open

# 取10:30的open
jd_first_hour['next_1030'] = jd_first_hour.apply(lambda row: jd_hist_calc_premarket[
    (jd_hist_calc_premarket['date'] == row['next_trading_date']) & (
            jd_hist_calc_premarket['time'] == datetime.time(hour=10, minute=30))].iloc[0, 0], axis=1)

jd_first_hour['strategy_return'] = (jd_first_hour.next_1030 - jd_first_hour.this_1030) / jd_first_hour.this_1030

# 只看前一天跌了的
jd_first_hour[jd_first_hour['return'] < 0]

# premarket重复一遍类似的
jd_premarket_movement[jd_premarket_movement['Premarket Return'] < 0]

jd_premarket_movement['next_trading_date'] = jd_premarket_movement.apply(lambda d: get_next_trading_date(d.name),
                                                                         axis=1)
jd_premarket_movement['this_1030'] = jd_premarket_movement.apply(lambda row: jd_hist_calc_premarket[
    (jd_hist_calc_premarket['date'] == row.name) &
    (jd_hist_calc_premarket['time'] == datetime.time(hour=10, minute=30))
    ].iloc[0, 0], axis=1)
jd_premarket_movement['next_1030'] = jd_premarket_movement.apply(lambda row: jd_hist_calc_premarket[
    (jd_hist_calc_premarket['date'] == row['next_trading_date']) & (
            jd_hist_calc_premarket['time'] == datetime.time(hour=10, minute=30))].iloc[0, 0], axis=1)

jd_premarket_movement['strategy_return'] = (jd_premarket_movement.next_1030 - jd_premarket_movement.this_1030) \
                                           / jd_premarket_movement.this_1030

# 准备批量处理数据
# call一次API，拆分数据，存到一个dict

tickers = list(stock_list['Ticker'].head(10))

temp = yf.download(tickers, start='2022-11-14', end='2022-11-18', interval='1h')

test_name_dict = dict()
for each_stock in list(stock_list['Ticker']):
    temp = yf.download(each_stock, period="1d", interval="1d", progress=False)
    test_name_dict[each_stock] = temp.iloc[0, 3] if len(temp) > 0 else -1

[k for k, v in test_name_dict.items() if v == -1]

len(list(stock_list['Ticker']))

'''
QNIU
LDOC
ATHM
HLG
LDOC
QNIU
'''
