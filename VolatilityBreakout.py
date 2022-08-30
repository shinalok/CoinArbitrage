import time
import datetime
from UpbitManager import UpbitManager


class VolatilityBreakout():

    def __init__(self):
        self.upbit = UpbitManager()
        print("Hello")

    def get_target_price(self, ticker):
        df = self.upbit.get_ohlcv(ticker)
        yesterday = df.iloc[-2]

        today_open = yesterday['close']
        yesterday_high = yesterday['high']
        yesterday_low = yesterday['low']
        target = today_open + (yesterday_high - yesterday_low) * 0.5
        return target


    def get_bal(self):
        # upbit = pyupbit.Upbit(access_key, secret_key)
        bals = self.upbit.get_balances()
        for bal in bals:
            if bal['currency'] == 'KRW':
                balance = bal['balance']
        return balance


    def get_yesterday_ma5(self, ticker):
        df = self.upbit.get_ohlcv(ticker)
        close = df['close']
        ma = close.rolling(5).mean()
        return ma[-2]

    def sell_crypto_currency(self, ticker):
        unit = self.upbit.get_balance(ticker)
        # return upbit.sell_market_order(ticker, unit)
        return print("매도", ticker, unit)

    def buy_crypto_currency(self, ticker):
        krw = self.get_bal()
        orderbook = self.upbit.get_orderbook(ticker)
        bids_asks = orderbook['orderbook_units']
        sell_price = float(bids_asks[0]['bid_price'])
        unit = float(krw) / float(sell_price)

        # upbit.buy_limit_order(ticker,sell_price,unit)
        # return upbit.buy_market_order("KRW-XRP", 5000)
        return print("매수", ticker, sell_price, unit)


    def volatility_breakout(self, ticker):
        print("변동성돌파 시작")
        now = datetime.datetime.now()
        mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
        target_price = self.get_target_price(ticker)
        ma5 = self.get_yesterday_ma5(ticker)

        while True:
            try:
                now = datetime.datetime.now()
                if mid < now < mid + datetime.timedelta(seconds=10):
                    target_price = self.get_target_price(ticker)
                    mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
                    ma5 = self.get_yesterday_ma5(ticker)
                    print("targetprice 갱신")
                    self.sell_crypto_currency(ticker)

                current_price = self.upbit.get_current_price(ticker)
                print(now, "current_price", current_price, "target_price", target_price, "ma5", ma5)
                time.sleep(0.2)

                if (current_price > target_price) and (current_price > ma5):
                    self.buy_crypto_currency(ticker)

            except:
                print("에러 발생")
            time.sleep(1)


if __name__ == '__main__':
    vb = VolatilityBreakout()
    vb.volatility_breakout("KRW-XRP")
