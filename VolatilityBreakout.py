import time
import datetime

from BinanceManager import BinanceManager
from UpbitManager import UpbitManager


class VolatilityBreakout():

    def __init__(self, mode, currency, ticker):
        if(mode == "UPBIT"):
            self.api = UpbitManager()
        elif(mode == "BINANCE"):
            self.api = BinanceManager()
        else:
            self.api = UpbitManager()
        self.set_currency(currency)
        self.set_ticker(ticker)
        print("Hello")
    def set_currency(self, currency):
        self.currency = currency

    def set_ticker(self, ticker):
        self.ticker = ticker

    def get_target_price(self, ticker):
        df = self.api.get_ohlcv(ticker)
        yesterday = df.iloc[-2]

        today_open = yesterday['close']
        yesterday_high = yesterday['high']
        yesterday_low = yesterday['low']
        target = today_open + (yesterday_high - yesterday_low) * 0.5
        return target

    def get_bal(self, asset):
        # upbit = pyupbit.Upbit(access_key, secret_key)
        bals = self.api.get_balances()
        return bals[asset]
        '''
        for bal in bals:
            if bal['currency'] == 'KRW':
                balance = bal['balance']
        
        return balance
        '''


    def get_yesterday_ma5(self, ticker):
        df = self.api.get_ohlcv(ticker)
        close = df['close']
        ma = close.rolling(5).mean()
        return ma[-2]

    def sell_crypto_currency(self, ticker):
        unit = self.api.get_balance_amt(ticker)
        # return upbit.sell_market_order(ticker, unit)
        return print("매도", ticker, unit)

    def buy_crypto_currency(self, ticker):
        krw = self.get_bal(self.currency)
        orderbook = self.api.get_orderbook(ticker)
        sell = orderbook['sell']
        sell_price = float(sell[0]['price'])
        unit = float(krw) / float(sell_price)

        # upbit.buy_limit_order(ticker,sell_price,unit)
        # return upbit.buy_market_order("KRW-XRP", 5000)
        return print("매수", ticker, sell_price, unit)


    def run(self):
        print("변동성돌파 시작")
        now = datetime.datetime.now()
        mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
        target_price = self.get_target_price(self.ticker)
        ma5 = self.get_yesterday_ma5(self.ticker)

        while True:
            try:
                now = datetime.datetime.now()
                if mid < now < mid + datetime.timedelta(seconds=10):
                    target_price = self.get_target_price(self.ticker)
                    mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
                    ma5 = self.get_yesterday_ma5(self.ticker)
                    print("targetprice 갱신")
                    self.sell_crypto_currency(self.ticker)

                current_price = self.api.get_current_price(self.ticker)
                print(now, "current_price", current_price, "target_price", target_price, "ma5", ma5)
                time.sleep(0.2)

                if (current_price > target_price) and (current_price > ma5):
                    self.buy_crypto_currency(self.ticker)

            except:
                print("에러 발생")
            time.sleep(1)


if __name__ == '__main__':
    vb = VolatilityBreakout("UPBIT", "KRW", "KRW-XRP")
    #vb = VolatilityBreakout("BINANCE", "USDT", "XRP/USDT")
    vb.run()
