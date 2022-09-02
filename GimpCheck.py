import ccxt
import pyupbit
import requests
import time
import datetime
import pandas as pd
from sqlalchemy import create_engine


engine = create_engine("mssql+pyodbc://192.168.0.28/coin?driver=SQL+Server", echo=False)
engine.connect()
#db안하려면 이거 막으면됨

binance = ccxt.binance()
upbit = pyupbit.get_tickers()


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
            p_binance_ask = []
            p_binance_bid = []
            p_upbit_ask = []
            p_upbit_bid = []

            currency = upbit_get_usd_krw()

            for b_ticker in ticker_binance:
                binance_price = binance.fetch_ticker(b_ticker)
                #p_binance.append(binance_price['close'])
                p_binance_bid.append(binance_price['bid'])#숏을 해야하니까 매수1호가
                p_binance_ask.append(binance_price['ask'])  # 숏을 해야하니까 매수1호가



            for u_ticker in ticker_upbit: #롱은 매도1호가
                orderbook = pyupbit.get_orderbook(u_ticker)
                ob = orderbook['orderbook_units'][0]
                p_upbit_ask.append(ob['ask_price'])
                p_upbit_bid.append(ob['bid_price'])

            buygimp = [(x / (y * currency) - 1) * 100 for x, y in zip(p_upbit_ask, p_binance_bid)]
            sellgimp = [(x / (y * currency) - 1) * 100 for x, y in zip(p_upbit_bid, p_binance_ask)]

            tickerlist.append('currency')
            buygimp.append(currency)
            sellgimp.append(currency)


            l_now.append(now)
            l_now =l_now * (len(ticker_binance)+1)
            l_data.append(list(zip(l_now, tickerlist, buygimp,sellgimp)))

            df = pd.DataFrame(data=list(zip(l_now, tickerlist, buygimp,sellgimp)), columns=['logdate', 'ticker', 'entrygimp','exitgimp'])
            df.to_sql(name='td_Gimpdaily', con=engine, if_exists='append', index=False)
            print(df)
            time.sleep(0.2)

        except Exception as e:
            print("에러 발생",e)
        time.sleep(1)


if __name__ == '__main__':
    tickerlist = ['BTC','ETC','XLM','EOS','XRP']  # 여기에 모니터링할 티커 넣어주면 됨
    bi = ticker_listmapping(tickerlist, 'binance')
    up = ticker_listmapping(tickerlist, 'upbit')
    gimpcheck(bi, up)

# import itertools
# l_data2 = list(itertools.chain.from_iterable(l_data))
# df2 = pd.DataFrame(data = l_data2,columns=['date','ticker','gimp'])
# print(df2)