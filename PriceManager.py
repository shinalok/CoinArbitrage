import threading
import time
import random
import queue

from BinanceFOManager import BinanceFOManager
from UpbitManager import UpbitManager


class PriceManager(threading.Thread):

    def initialize(self, api, ticker, queue, condition):
        self.set_api(api)
        self.set_ticker(ticker)
        self.set_queue(queue)
        self.set_condition(condition)

    def set_condition(self, condition):
        self.condition = condition

    def get_condition(self):
        return self.condition

    def set_queue(self, queue):
        self.queue = queue

    def get_queue(self):
        return self.queue

    def set_api(self, api):
        self.api = api

    def set_ticker(self, ticker):
        self.ticker = ticker

    def run(self):
        while True:
            #print(self.ticker)
            #print(threading.currentThread().getName())
            #self.api.get_orderbook("XRP/USDT")
            hoga = self.api.get_orderbook(self.ticker)
            #randNum = random.randint(1,9)
            self.queue.put(hoga)
            print("[queue] size: ", self.queue.qsize())
            print('notify : ', hoga)
            with self.condition:
                self.condition.notifyAll()
            # print('[sender]time...')
            time.sleep(1)
            if (self.queue.qsize() > 10):
                break
            # print(buffer)


if __name__ == '__main__':

    upbit = UpbitManager()
    binance = BinanceFOManager()
    priceManager = PriceManager(name="UPBIT Price[XRP]")
    priceManager.set_api(upbit)
    priceManager.set_ticker("KRW-XRP")


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