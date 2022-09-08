import datetime
import threading
import time
import random
import queue

import APIS
from PriceDepartment import PriceDepartment


class GimpStrategy(threading.Thread):
    def initialize(self, price_dept):
        self.price_dept = price_dept
        self._init()
        #self.set_queue(queue)
        #self.set_condition(condition)

    def _init(self):
        self.set_queue(self.price_dept.get_queue())
        self.set_condition(self.price_dept.get_condition())

    def set_condition(self, condition):
        self.condition = condition

    def get_condition(self):
        return self.condition

    def set_queue(self, queue):
        self.queue = queue

    def get_queue(self):
        return self.queue

    def set_watch(self, watch_list, pair_list):
        self.watch_list = watch_list
        self.pair_list = pair_list
        self._make_ticker()

    def _make_ticker(self):
        self.tickers = {}
        for ticker in self.watch_list:
            self.tickers[ticker] = { "UPBIT": "KRW-"+ticker, "BINANCE": ticker+"/USDT" }
        print(self.tickers)


    def run(self):
        for ticker in self.watch_list:
            self.price_dept.add_pair(self.pair_list, ticker)
        while True:
            with self.condition:
                self.condition.wait(1)
            try:
                now = datetime.datetime.now()
                #currency = self.price_dept.get_usd_krw()
                currency = self.price_dept.get_currency()

                hoga = self.queue.get_nowait()
                #print(self.queue.qsize())
                #print(hoga.keys())
                print(hoga)
                buy = []
                sell = []
                tickers = []
                for ticker in hoga.keys():
                    buy.append(hoga[ticker]["buy"][0]['price'])
                    sell.append(hoga[ticker]["sell"][0]['price'])
                    #print(hoga[ticker]["sell"])
                    #print(hoga[ticker]["buy"])
                    #print("[{}] buy: {} / sell: {} / USD: {}".format(ticker, hoga[ticker]["buy"][0]['price'], hoga[ticker]["sell"][0]['price'], currency))
                    tickers.append(ticker)

                entry = ((sell[0] / (buy[1] * currency)) - 1) * 100
                exit = ((buy[0] / (sell[1] * currency)) - 1) * 100
                diff = entry - exit
                print("[{}/{}]entry: {} / exit: {} / diff {}".format(now, (tickers[0]+"|"+tickers[1]), entry, exit, diff))
                #time.sleep(0.2)

            except queue.Empty as ex:
                print("Queue Empty ", ex)
            except Exception as ex:
                print("Exception ", ex)
            except Exception as e:
                print("에러 발생", e)
            #time.sleep(1)

if __name__ == '__main__':
    #tickerlist = ['BTC', 'ETC', 'ETH', 'EOS', 'XRP']  # 여기에 모니터링할 티커 넣어주면 됨
    tickerlist = ['ETC']  # 여기에 모니터링할 티커 넣어주면 됨
    pairlist = [APIS.UPBIT, APIS.BINANCE]
    priceDep = PriceDepartment()
    gimp = GimpStrategy()
    gimp.initialize(priceDep)
    gimp.set_watch(tickerlist, pairlist)
    gimp.start()