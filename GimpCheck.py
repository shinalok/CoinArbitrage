import ccxt
import pyupbit
import requests
import json
import time
import datetime
import pandas as pd

binance = ccxt.binance()
upbit = pyupbit.get_tickers()
# markets = binance.fetch_tickers()

l_logtime = []
l_ticker = []
l_gimp = []
l_data = []


# 환율
def upbit_get_usd_krw():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    exchange = requests.get(url, headers=headers).json()
    return exchange[0]['basePrice']


# 티커매핑
def ticker_listmapping(ticker, exchange):
    result = []

    if exchange == 'upbit':
        for s in ticker:
            result.append("KRW-" + s)
    elif exchange == 'binance':
        for s in ticker:
            result.append(s + '/USDT')
    return result


# 김프체크
def gimpcheck(ticker_binance, ticker_upbit):
    while True:
        try:

            now = datetime.datetime.now()
            l_now = []
            p_binance = []
            p_upbit = []

            currency = upbit_get_usd_krw()

            for b_ticker in ticker_binance:
                binance_price = binance.fetch_ticker(b_ticker)
                p_binance.append(binance_price['close'])

            if len(p_binance) > 1:
                p_upbit = pyupbit.get_current_price(ticker_upbit)
                p_upbit = list(p_upbit.values())
                gimp = [(x / (y * currency) - 1) * 100 for x, y in zip(p_upbit, p_binance)]
            else:
                p_upbit.append(pyupbit.get_current_price(ticker_upbit))
                gimp = [(x / (y * currency) - 1) * 100 for x, y in zip(p_upbit, p_binance)]

            l_now.append(now)
            l_now = l_now * len(ticker_binance)
            l_data.append(list(zip(l_now, tickerlist, gimp)))

            df = pd.DataFrame(data=list(zip(l_now, tickerlist, gimp)), columns=['date', 'ticker', 'gimp'])
            print(df,currency)

            time.sleep(0.2)

        except:
            print("에러 발생")
        time.sleep(1)


if __name__ == '__main__':
    tickerlist = ['ETC', 'XRP', 'EOS']  # 여기에 모니터링할 티커 넣어주면 됨
    bi = ticker_listmapping(tickerlist, 'binance')
    up = ticker_listmapping(tickerlist, 'upbit')
    gimpcheck(bi, up)

# import itertools
# l_data2 = list(itertools.chain.from_iterable(l_data))
# df2 = pd.DataFrame(data = l_data2,columns=['date','ticker','gimp'])
# print(df2)