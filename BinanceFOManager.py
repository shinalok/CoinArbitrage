import time

import pyupbit
import ccxt
from apscheduler.schedulers.background import BackgroundScheduler

from APIManager import *
import pandas as pd
from multipledispatch import dispatch

from BinanceManager import BinanceManager


class BinanceFOManager(BinanceManager):

    def __init__(self):
        print("__load BinanceFOManager__")
        # 업비트 키 로드
        with open("keys/binance_key.txt") as f:
            lines = f.readlines()
            access_key = lines[0].strip()
            secret_key = lines[1].strip()

        self.api = ccxt.binance({
            'apiKey': access_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            }

        })
        self.leverage = 1

    def set_leverage(self, leverage):
        self.leverage = leverage

    def _set_leverage(self, ticker):
        markets = self.api.load_markets()
        market = self.api.market(ticker)
        resp = self.api.fapiPrivate_post_leverage({
            'symbol': market['id'],
            'leverage': self.leverage
        })
        return resp

    def get_balance_amt(self, ticker):
        bal = self.api.fetch_balance()
        positions = bal['info']['positions']
        conv_ticker = ticker.replace("/",'')
        res_bal = next((item for item in positions if item['symbol'] == conv_ticker), None)
        return res_bal['positionAmt']

    @dispatch(str)
    def sell(self, ticker):
        self._set_leverage(ticker)
        unit = self.get_balance_amt(ticker)
        return self.api.create_market_sell_order(ticker, unit)

    @dispatch(str, float)
    def sell(self, ticker, unit):
        self._set_leverage(ticker)
        return self.api.create_market_sell_order(ticker, unit)  # unit: 수량

    @dispatch(str, float, float)
    def sell(self, ticker, price, unit):
        self._set_leverage(ticker)
        return self.api.create_limit_sell_order(ticker, price, unit)

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
        # if(self.count is not None):
        hoga = self.get_orderbook(ticker)
        market_price = hoga["sell"][0]["price"]
        unit = price / market_price
        if hasattr(self, 'count'):
            self.count += 1
            print(self.count)
        self._set_leverage(ticker)
        return self.buy(ticker, market_price, unit)

    @dispatch(str, float)
    def buy(self, ticker, unit):
        print(ticker, unit)
        # if(self.count is not None):
        if hasattr(self, 'count'):
            self.count += 1
            print(self.count)
        self._set_leverage(ticker)
        return self.api.create_market_buy_order(ticker, unit)  # unit: 수량. Upbit의 경우 금액이 들어감

    @dispatch(str, float, float)
    def buy(self, ticker, price, unit):
        print(ticker, price, unit)
        self._set_leverage(ticker)
        return self.api.create_limit_buy_order(symbol=ticker, price=price, amount=unit)

    @dispatch(str, float, int, int)
    def buy(self, ticker, price, term, count):
        _div_price = (price / count)
        print(_div_price)
        self._set_leverage(ticker)
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


if __name__ == '__main__':
    api = BinanceFOManager()
    print(api.get_current_price("XRP/USDT"))
    exit()
    order = api.get_orderbook("XRP/USDT")
    print(order)
    bal = api.get_balances()
    print(bal)
    bal = api.get_balance_amt("XRP/USDT")
    print(bal)
    exit()
    df = api.get_ohlcv("XRP/USDT")
    print(df)