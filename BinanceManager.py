import pyupbit
import ccxt

from APIManager import *
import pandas as pd

class BinanceManager(APIManager):
    def __init__(self):
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

    def get_ohlcv(self, ticker):
        ohlcvs = self.api.fetch_ohlcv(ticker, '1d')
        df = pd.DataFrame(ohlcvs, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df.set_index(keys='date', inplace=True)
        return df

    def get_balances(self):
        bal = self.api.fetch_balance()
        return bal['free']

    def get_balance_amt(self, ticker):
        bal = self.api.fetch_balance()
        positions = bal['info']['positions']
        conv_ticker = ticker.replace("/",'')
        res_bal = next((item for item in positions if item['symbol'] == conv_ticker), None)
        return res_bal['positionAmt']

    def get_orderbook(self, ticker):
        orderbook = self.api.fetch_order_book(ticker)
        orderbook_buys = orderbook['bids']
        orderbook_sells = orderbook['asks']
        sell = []
        buy = []
        for order in orderbook_buys:
            buy.append({"price": order[0], "vol": order[1]})
        for order in orderbook_sells:
            sell.append({"price": order[0], "vol": order[1]})
        return {"sell": sell, "buy": buy}

    def get_current_price(self, ticker):
        return self.api.fetch_ticker(ticker)['close']


if __name__ == '__main__':
    api = BinanceManager()
    print(api.get_current_price("XRP/USDT"))
    order = api.get_orderbook("XRP/USDT")
    print(order)
    bal = api.get_balances()
    print(bal)
    bal = api.get_balance_amt("XRP/USDT")
    print(bal)
    exit()
    df = api.get_ohlcv("XRP/USDT")
    print(df)