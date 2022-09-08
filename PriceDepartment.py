import requests

import APIS
from PairPriceManager import PairPriceManager
from PriceManager import *
import threading
import queue
import time
from bs4 import BeautifulSoup
import yfinance as yf
import datetime

class PriceDepartment:
    UPBIT = 1
    BINANCE = 2
    PARE = 50
    def __init__(self):
        self.queue = queue.Queue()
        self.condition = threading.Condition()
        self.workers = {}
        self.upbit = UpbitManager()
        self.binance = BinanceFOManager()

    def get_condition(self):
        return self.condition

    def get_queue(self):
        return self.queue

    def add_price(self, api, ticker):
        if (ticker not in self.workers.keys()):
            priceManager = PriceManager(name=("[" + ticker + "] PriceManager"))
            if(api == APIS.UPBIT):
                _api = self.upbit
            elif (api == APIS.BINANCE):
                _api = self.binance
            else:
                _api = self.upbit
            priceManager.initialize(_api, ticker, self.queue, self.condition)
            priceManager.start()
            self.workers[ticker] = priceManager

    def add_pair(self, apis, ticker):
        if (ticker not in self.workers.keys()):
            priceManager = PairPriceManager(name=("[" + ticker + "] PriceManager"))
            _api = []
            for api in apis:
                if(api == APIS.UPBIT):
                    _api.append(self.upbit)
                elif (api == APIS.BINANCE):
                    _api.append(self.binance)
                else:
                    _api.append(self.upbit)
            priceManager.initialize(_api, ticker, self.queue, self.condition)
            priceManager.start()
            self.workers[ticker] = priceManager

    def join(self):
        for ticker in self.workers:
            self.workers[ticker].join()


    def get_usd_krw(self):
        return self.upbit.get_usd_krw()

    def get_currency(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        data = yf.download(['USDKRW=X'], start=now)
        return data['Close'][-1]


if __name__ == '__main__':
    priceDep = PriceDepartment()
    krw = priceDep.get_usd_krw()
    print("==KRW==")
    print(krw)
    krw = priceDep.get_currency()
    print("==KRW==")
    print(krw)
    exit()
    #priceDep.add_price(PriceDepartment.UPBIT, "KRW-XRP")
    #priceDep.add_price(PriceDepartment.UPBIT, "KRW-BTC")
    priceDep.add_pair([APIS.UPBIT, APIS.BINANCE], "XRP")
    priceDep.add_pair([APIS.UPBIT, APIS.BINANCE], "BTC")
    priceDep.join()

    for i in range(3):
        print("I'm main Thread")
        time.sleep(1)
    print("----the end----")