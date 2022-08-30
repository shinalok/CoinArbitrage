#!/usr/bin/env python
# coding: utf-8

# In[28]:


import ccxt
import time
import datetime
import pandas as pd

with open("keys/binance_key.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret  = lines[1].strip()

binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})



def get_target_price(ticker):
    ohlcvs = binance.fetch_ohlcv(ticker,'1d')
    #print(datetime.fromtimestamp(ohlcvs[0][0]/1000).strftime('%Y-%m-%d %H:%M:%S'))
    today_open = ohlcvs[0][1]
    yesterday_high = ohlcvs[0][2]
    yesterday_low = ohlcvs[0][3]
    target = today_open + (yesterday_high - yesterday_low) * 0.5
    return target

def get_bal():
    bal = binance.fetch_balance()
    #print(bal['USDT']['free'], bal['XRP']['free'], bal['XRP']['total'])
    balance = bal['USDT']['free']
    return balance

def get_yesterday_ma5(ticker):
    binance = ccxt.binance()
    ohlcvs = binance.fetch_ohlcv(ticker,'1d')

    df = pd.DataFrame(ohlcvs, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    close = df['close']
    ma = close.rolling(5).mean()
    return ma[-2]



def volatility_breakout(ticker):
    print("변동성돌파 시작")
    now = datetime.datetime.now()
    mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
    target_price = get_target_price(ticker)
    ma5 = get_yesterday_ma5(ticker)
    
    while True:
        try:
            now = datetime.datetime.now()
            if mid < now < mid + datetime.timedelta(seconds=10) : 
                target_price = get_target_price(ticker)
                mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
                ma5 = get_yesterday_ma5(ticker)
                print("targetprice 갱신")
                #sell_crypto_currency(ticker)


            current_price = binance.fetch_ticker(ticker)['close']
            
            print(now,"current_price",current_price,"target_price",target_price,"ma5",ma5)
            time.sleep(0.2)

            if (current_price > target_price) and (current_price > ma5):
                buy_crypto_currency(ticker)
                
                
                


            def buy_crypto_currency(ticker):
                usdt = get_bal()
                buycnt=0
                orderbook = binance.fetch_order_book(ticker)
                bids = orderbook['bids']
                sell_price = float(bids[0][0])
                buycnt = float(usdt)/float(sell_price)


                if buycnt >0:
                    print("매수",ticker,buycnt)   
#                     order = binance.create_market_buy_order(
#                          symbol=ticker,
#                          amount=buycnt
#                      )


            def sell_crypto_currency(ticker):

                balance = binance.fetch_balance()
                positions = balance['info']['positions']
                sellcnt=0

                for position in positions:
                    if position["symbol"] == ticker.replace("/",''):
                        c_position = position['positionAmt']
                        sellcnt = c_position


                if float(sellcnt)>0:
                    print("매도",ticker,sellcnt)
#                     order = binance.create_market_sell_order(
#                              symbol=ticker,
#                              amount=sellcnt
#                     )


            
        except:
            print("에러 발생")        
        time.sleep(1)

if __name__ == '__main__':
    volatility_breakout("EOS/USDT")
    #buy_crypto_currency('EOS/USDT')

# import ccxt

# binance = ccxt.binance()
# orderbook = binance.fetch_order_book('ETH/BTC')
# print(orderbook['asks'][0][0],orderbook['asks'][0][1])
# for ask in orderbook['asks']:
#     print(ask[0], ask[1])

