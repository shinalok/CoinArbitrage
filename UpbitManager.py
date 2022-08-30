import pyupbit

class UpbitManager():
    def __init__(self):
        # 업비트 키 로드
        with open("upbit_key.txt") as f:
            lines = f.readlines()
            access_key = lines[0].strip()
            secret_key = lines[1].strip()
        self.upbit = pyupbit.Upbit(access_key, secret_key)

    def get_ohlcv(self, ticker):
        return pyupbit.get_ohlcv(ticker)

    def get_balances(self):
        return self.upbit.get_balances()

    def get_balance(self, ticker):
        return self.upbit.get_balance(ticker)

    def get_orderbook(self, ticker):
        return pyupbit.get_orderbook(ticker)

    def get_current_price(self, ticker):
        return pyupbit.get_current_price(ticker)

