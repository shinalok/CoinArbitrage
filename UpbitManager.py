import math
import pyupbit
import time

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
        print(orderbook_units)
        sell = []
        buy = []
        for order in orderbook_units:
            sell.append({"price": order["ask_price"], "vol": order["ask_size"]})
            buy.append({"price": order["bid_price"], "vol": order["bid_size"]})
        return {"sell": sell, "buy": buy}
    def get_current_price(self, ticker):
        return pyupbit.get_current_price(ticker)

    @dispatch(str)
    def sell(self, ticker):
        unit = self.get_balance_amt(ticker)
        response = self.api.sell_market_order(ticker, unit)
        print(response)
        time.sleep(0.2)
        remain_vol = self.get_balance_amt(ticker)
        #remain_vol = float(response['remaining_volume'])
        print(remain_vol)

    @dispatch(str, float)
    def sell(self, ticker, price):
        return self.api.sell_market_order(ticker, price)  # unit: 수량

    @dispatch(str, float, float)
    def sell(self, ticker, price, unit):
        return self.api.sell_limit_order(ticker, price, unit)


    @dispatch(str, float)
    def buy(self, ticker, price):
        print(ticker, price)
        if(self.count is not None):
            self.count += 1
        return self.api.buy_market_order(ticker, price) #unit: 금액

    @dispatch(str, float, float)
    def buy(self, ticker, price, unit):
        print(ticker,price,unit)
        return self.api.buy_limit_order(ticker, price, unit)

    @dispatch(str, float, float, float)
    def buy(self, ticker, price, term, count):
        _div_price = math.floor(price / count)
        print(_div_price)
        self.count = 0
        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(self.buy, 'interval', seconds=term, id="buy_upbit", args=[ticker, _div_price])
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
    #10만원을 10초에한번 10번
    api.buy('KRW-XRP', 100000.0, 10.0, 10.0)

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
