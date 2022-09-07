import math
import pyupbit
import time

import requests
from multipledispatch import dispatch
from APIManager import APIManager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

class UpbitManager(APIManager):

    def __init__(self):
        # 업비트 키 로드
        with open("keys/upbit_key.txt") as f:
            lines = f.readlines()
            access_key = lines[0].strip()
            secret_key = lines[1].strip()
        self.api = pyupbit.Upbit(access_key, secret_key)

    def get_ohlcv(self, ticker):
        return pyupbit.get_ohlcv(ticker)

    def get_balances(self):
        bals = self.api.get_balances()
        conv_bal = {}
        for bal in bals:
            conv_bal[bal['currency']] = float(bal['balance'])
        return conv_bal

    def get_balance_amt(self, ticker):
        return self.api.get_balance(ticker)

    def get_orderbook(self, ticker):
        orderbook = pyupbit.get_orderbook(ticker)
        orderbook_units = orderbook['orderbook_units']
        #print(orderbook_units)
        sell = []
        buy = []
        for order in orderbook_units:
            sell.append({"price": order["ask_price"], "vol": order["ask_size"]})
            buy.append({"price": order["bid_price"], "vol": order["bid_size"]})
        return {"sell": sell, "buy": buy}
    def get_current_price(self, ticker):
        return pyupbit.get_current_price(ticker)

    def get_usd_krw(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
        exchange = requests.get(url, headers=headers).json()
        return exchange[0]['basePrice']

    @dispatch(str)
    def sell(self, ticker):
        unit = self.get_balance_amt(ticker)
        return self.api.sell_market_order(ticker, unit)

    @dispatch(str, float)
    def sell(self, ticker, unit):
        return self.api.sell_market_order(ticker, unit)  # unit: 수량

    @dispatch(str, float, float)
    def sell(self, ticker, price, unit):
        return self.api.sell_limit_order(ticker, price, unit)

    @dispatch(str, float, int, int)
    def sell(self, ticker, unit, term, count):
        _div_unit = (unit / count)
        print(_div_unit)
        self.count = 0
        self.sell(ticker, _div_unit)
        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(self.sell, 'interval', seconds=term, id="sell_upbit", args=[ticker, _div_unit])
        while True:
            print("Running...............")
            time.sleep(1)
            if self.count == count:
                sched.remove_job("sell_upbit")
                break

    @dispatch(str, float)
    def buy_target(self, ticker, price):
        print(ticker, price)
        #if(self.count is not None):
        if hasattr(self, 'count'):
            self.count += 1
            print(self.count)
        return self.api.buy_market_order(ticker, price) #unit: 금액

    @dispatch(str, float)
    def buy(self, ticker, unit):
        print(ticker, unit)
        hoga = self.get_orderbook(ticker)
        price = hoga["sell"][0]["price"]
        # if(self.count is not None):
        if hasattr(self, 'count'):
            self.count += 1
            print(self.count)
        return self.buy(ticker, price, unit)  # unit: 금액

    @dispatch(str, float, float)
    def buy(self, ticker, price, unit):
        print(ticker,price,unit)
        return self.api.buy_limit_order(ticker, price, unit)

    @dispatch(str, float, int, int)
    def buy(self, ticker, price, term, count):
        _div_price = (price / count)
        print(_div_price)
        self.count = 0
        self.buy_target(ticker, _div_price)
        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(self.buy_target, 'interval', seconds=term, id="buy_upbit", args=[ticker, _div_price])
        while True:
            print("Running...............")
            time.sleep(1)
            if self.count == count:
                sched.remove_job("buy_upbit")
                break

    '''
    def buy_all(self, ticker):
        #사용중지
        return
        unit = self.get_balances()['KRW']
        response = self.api.buy_market_order(ticker, unit)
        time.sleep(0.2)
        remain_vol = float(response['remaining_volume'])
        while(remain_vol > 0):
            response = self.api.buy_market_order(ticker, remain_vol)
            time.sleep(0.2)
            remain_vol = float(response['remaining_volume'])
    '''

if __name__ == '__main__':
    api = UpbitManager()
    #res = api.buy_target('KRW-XLM', 10000.0) #10000원 매수
    res = api.buy('KRW-XLM', 50.0)  # 시장가 15주 매수
    #res = api.buy('KRW-XRP', 451.0, 15.0) #451원, 15주 매수
    #res = api.sell('KRW-XRP', 450.0, 15.0) #450원, 15주 매도
    #res = api.sell('KRW-XRP', 22.172949) #22.172949주 매도
    #res = api.buy('KRW-XRP', 30000.0, 60, 3) #3만원, 1분, 3번 나눠서 매수
    #res = api.sell('KRW-XRP') #해당티커 전부 매도
    #print(res)
    #res = api.sell('KRW-XRP', 60.0, 60, 3) #60개, 1분, 3번 나눠서 매도
    bal = api.get_balances()
    print(bal)
    bal = api.get_balance_amt('KRW-XRP')
    print(bal)

    #10만원을 10초에한번 10번
    #api.buy('KRW-XRP', 100000.0, 10.0, 10.0)

    exit()
    #res = api.sell('KRW-XRP')
    #print(res)
    exit()
    bal = api.get_balances()
    print(bal)
    ohlcv = api.get_ohlcv('KRW-XRP')
    print(ohlcv)
    print(api.get_balance_amt('KRW-XRP'))
    print(api.get_orderbook('KRW-XRP'))
    print(api.get_current_price('KRW-XRP'))
