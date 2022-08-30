#!/usr/bin/env python
# coding: utf-8

# In[53]:


import ccxt
import pyupbit
import requests
import json
import time
import datetime
import pandas as pd

binance = ccxt.binance()
upbit = pyupbit.get_tickers()
#markets = binance.fetch_tickers()

l_logtime = []
l_ticker =[]
l_gimp = []
l_data=[]

#환율
def upbit_get_usd_krw():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    exchange =requests.get(url, headers=headers).json()
    return exchange[0]['basePrice']

#티커매핑
def ticker_listmapping(ticker,exchange):
    result = []
    
    if exchange =='upbit':
        for s in ticker:
            result.append("KRW-"+s)
    elif exchange == 'binance':
        for s in ticker:
            result.append(s+'/USDT')
    return result

#김프체크
def gimpcheck(ticker_binance,ticker_upbit):
    while True:
        try:

            now = datetime.datetime.now()
            l_now=[]
            p_binance =[]
            p_upbit=[]
        
        
        
            currency = upbit_get_usd_krw()    
            
            for b_ticker in ticker_binance:
                binance_price = binance.fetch_ticker(b_ticker)
                p_binance.append(binance_price['close'])

        
            
            if len(p_binance)>1:
                p_upbit = pyupbit.get_current_price(ticker_upbit)
                p_upbit = list(p_upbit.values())
                gimp = [(x/(y*currency) -1)*100 for x,y in zip(p_upbit,p_binance)]
            else:
                p_upbit.append(pyupbit.get_current_price(ticker_upbit))
                gimp = [(x/(y*currency) -1)*100 for x,y in zip(p_upbit,p_binance)]
            
            
            l_now.append(now)
            l_now = l_now*len(ticker_binance)
            l_data.append(list(zip(l_now,tickerlist,gimp)))
        
            df = pd.DataFrame(data = list(zip(l_now,tickerlist,gimp)),columns=['date','ticker','gimp'])
            print(df)    
            
            time.sleep(0.2)

        except:
            print("에러 발생")        
        time.sleep(1)

        

if __name__ == '__main__':
    tickerlist = ['ETC','XRP','EOS'] #여기에 모니터링할 티커 넣어주면 됨
    bi = ticker_listmapping(tickerlist,'binance')
    up = ticker_listmapping(tickerlist,'upbit')
    gimpcheck(bi,up)

# import itertools
# l_data2 = list(itertools.chain.from_iterable(l_data))
# df2 = pd.DataFrame(data = l_data2,columns=['date','ticker','gimp'])
# print(df2)


# In[85]:



import pyupbit
import time
import datetime
import ccxt 

#업비트 키 로드
with open("upbit_api.txt") as f:
    lines = f.readlines()
    access_key = lines[0].strip()
    secret_key  = lines[1].strip()

upbit = pyupbit.Upbit(access_key, secret_key)      


#바이낸스 키 로드
with open("binance_api.txt") as f:
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




def ticker_listmapping(c_ticker,c_exchange):
    result = []
    
    if c_exchange =='upbit':
        for s in c_ticker:
            result.append("KRW-"+s)
    elif c_exchange == 'binance':
        for s in c_ticker:
            result.append(s+'/USDT')
    return result


def get_bal():
    #upbit = pyupbit.Upbit(access_key, secret_key)
    bals = upbit.get_balances()
    for bal in bals:
         if bal['currency']=='KRW':
                balance = bal['balance']
    return balance




#청산
def exit(ticker):
    '''
    동시 전액 청산
    '''
    bi = ticker_listmapping(ticker,'binance')[0]
    up = ticker_listmapping(ticker,'upbit')[0]
    upcnt = upbit.get_balance(ticker=up)
    #upbit.sell_market_order(up, upcnt)
    print(up,upcnt)
    
    
    #바낸청산
    
    balance = binance.fetch_balance()
    positions = balance['info']['positions']


    for position in positions:
        if position["symbol"] == bi.replace("/",''):
            c_position = position['positionAmt']
            bicnt = c_position
    
    print(bi,c_position)
#     order = binance.create_market_buy_order(
#          symbol=bi,
#          amount=bicnt
#      )

#진입
def entry(ticker,ratio):
    '''
    업비트는 시장가매수할때 금액으로 해야함.
    바이낸스 숏은 수량으로
    
    '''
    
    bi = ticker_listmapping(ticker,'binance')[0]
    up = ticker_listmapping(ticker,'upbit')[0]
    
    
    krw = get_bal()
    krw = float(krw)/float(ratio)  #들어갈 비율을 설정함  
    
    beforecnt =upbit.get_balance(ticker=up)
    
    #ret = upbit.buy_market_order(up, krw)
    
    bicnt = round(upbit.get_balance(ticker=up)-beforecnt,4) #따로 체결완료 수량 조회방법이없어서 전과 후 차이를구해야함
    #print(upbit.get_order("KRW-XRP", state="cancel")[0])에서 state를 cancel로하면 시장가주문도 보임. done은 지정가주문만보임
    
    
    print(bicnt)
#     order = binance.create_market_sell_order(
#          symbol=bi,
#          amount=bicnt
#      )


        

if __name__ == '__main__':
    
    L_holding=['XRP']
    exit(L_holding)
    #entry(L_holding,50)


# In[81]:


print(upbit.get_order("KRW-XRP", state="cancel")[0])

