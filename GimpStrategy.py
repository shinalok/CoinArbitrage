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
                currency = self.price_dept.get_usd_krw()

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
                    print(hoga[ticker]["sell"])
                    print(hoga[ticker]["buy"])
                    print("[{}] buy: {} / sell: {} / USD: {}".format(ticker, hoga[ticker]["buy"][0]['price'], hoga[ticker]["sell"][0]['price'], currency))
                    tickers.append(ticker)

                entry = ((sell[0] / (buy[1] * currency)) - 1) * 100
                print("entry: {} / {} / {}".format(sell[0], buy[1], currency))
                exit = ((buy[0] / (sell[1] * currency)) - 1) * 100
                diff = entry - exit
                print("[{}/{}]entry: {} / exit: {} / diff {}".format(now, (tickers[0]+"|"+tickers[1]), entry, exit, diff))

                '''
                for b_ticker in ticker_binance:
                    binance_price = binance.fetch_ticker(b_ticker)
                    # p_binance.append(binance_price['close'])
                    p_binance_bid.append(binance_price['bid'])  # 숏을 해야하니까 매수1호가
                    p_binance_ask.append(binance_price['ask'])  # 숏을 해야하니까 매수1호가

                for u_ticker in ticker_upbit:  # 롱은 매도1호가
                    orderbook = pyupbit.get_orderbook(u_ticker)
                    ob = orderbook['orderbook_units'][0]
                    p_upbit_ask.append(ob['ask_price'])
                    p_upbit_bid.append(ob['bid_price'])

                buygimp = [(x / (y * currency) - 1) * 100 for x, y in zip(p_upbit_ask, p_binance_bid)]
                sellgimp = [(x / (y * currency) - 1) * 100 for x, y in zip(p_upbit_bid, p_binance_ask)]

                tickerlist.append('currency')
                buygimp.append(currency)
                sellgimp.append(currency)
                for i, j in zip(buygimp, sellgimp):
                    diff.append(i - j)

                l_now.append(now)
                l_now = l_now * (len(ticker_binance) + 1)
                l_data.append(list(zip(l_now, tickerlist, buygimp, sellgimp, diff)))

                df = pd.DataFrame(data=list(zip(l_now, tickerlist, buygimp, sellgimp, diff)),
                                  columns=['logdate', 'ticker', 'entrygimp', 'exitgimp', 'diff'])
                # df.to_sql(name='td_Gimpdaily', con=engine, if_exists='append', index=False)
                print(df)
                '''
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
    tickerlist = ['XRP']  # 여기에 모니터링할 티커 넣어주면 됨
    pairlist = [APIS.UPBIT, APIS.BINANCE]
    priceDep = PriceDepartment()
    gimp = GimpStrategy()
    gimp.initialize(priceDep)
    gimp.set_watch(tickerlist, pairlist)
    gimp.start()