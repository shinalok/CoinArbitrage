import threading
import time
import random
import queue

from BinanceFOManager import BinanceFOManager
from BinanceManager import BinanceManager
from PriceManager import PriceManager
from UpbitManager import UpbitManager


class PairPriceManager(PriceManager):

    def _set_pare(self):
        self.tickers = []
        for _api in self.api:
            if(isinstance(_api, UpbitManager)):
                self.tickers.append("KRW-"+self.ticker)
            elif (isinstance(_api, BinanceManager)):
                self.tickers.append(self.ticker+"/USDT")
            elif(isinstance(_api, BinanceFOManager)):
                self.tickers.append(self.ticker + "/USDT")

        self.watch = list(zip(self.api, self.tickers))

    def run(self):
        self._set_pare()
        while True:
            #print(self.ticker)
            #print(threading.currentThread().getName())
            #self.api.get_orderbook("XRP/USDT")
            hoga = {}
            for api, ticker in self.watch:
                hoga[ticker] = api.get_orderbook(ticker)
            #hoga["TICKER"] = self.ticker
            self.queue.put(hoga)
            #print("[queue] size: ", self.queue.qsize())
            #print('notify : ', hoga)
            with self.condition:
                self.condition.notifyAll()
            # print('[sender]time...')
            time.sleep(1)
            if (self.queue.qsize() > 10):
                break
            # print(buffer)


if __name__ == '__main__':
    '''
    a = ["A", "B", "C"]
    b = [1, 2, 3]
    z = list(zip(a, b))
    print(z)
    for _a, _b in z:
        print(_a + "/" + str(_b))
    upbit = UpbitManager()
    binance = BinanceFOManager()
    print(isinstance(upbit, UpbitManager))
    print(isinstance(binance, UpbitManager))
    exit()
    '''
    upbit = UpbitManager()
    binance = BinanceFOManager()
    priceManager = PairPriceManager(name="UPBIT/BINANCE Price[XRP]")
    priceManager.set_api([upbit, binance])
    priceManager.set_ticker("XRP")


    #receive = Receiver(name="Receiving Messages")
    #receive2 = Receiver(name="Receiving Messages2")

    queue = queue.Queue()
    condition = threading.Condition()

    priceManager.set_condition(condition)
    #receive.setCondition(condition)
    #receive2.setCondition(condition)
    priceManager.set_queue(queue)
    #receive.setBuffer(buffer)
    #receive2.setBuffer(buffer)

    #receive.start()
    priceManager.start()

    #receive2.start()
    priceManager.join()
    #receive.join()
    #receive2.join()
    for i in range(3):
        print("I'm main Thread")
        time.sleep(1)
    print("----the end----")