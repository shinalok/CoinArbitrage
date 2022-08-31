import pyupbit

from APIManager import APIManager

class UpbitManager(APIManager):

    def __init__(self):
        # 업비트 키 로드
        with open("keys/upbit_key.txt") as f:
            lines = f.readlines()
            access_key = lines[0].strip()
            secret_key = lines[1].strip()
        self.api = pyupbit.Upbit(access_key, secret_key)

    def get_ohlcv(self, ticker):
        return pyupbit.get_ohlcv(ticker)

    def get_balances(self):
        bals = self.api.get_balances()
        conv_bal = {}
        for bal in bals:
            conv_bal[bal['currency']] = float(bal['balance'])
        return conv_bal

    def get_balance_amt(self, ticker):
        return self.api.get_balance(ticker)

    def get_orderbook(self, ticker):
        orderbook = pyupbit.get_orderbook(ticker)
        orderbook_units = orderbook['orderbook_units']
        print(orderbook_units)
        sell = []
        buy = []
        for order in orderbook_units:
            sell.append({"price": order["ask_price"], "vol": order["ask_size"]})
            buy.append({"price": order["bid_price"], "vol": order["bid_size"]})
        return {"sell": sell, "buy": buy}
    def get_current_price(self, ticker):
        return pyupbit.get_current_price(ticker)

if __name__ == '__main__':
    api = UpbitManager()
    bal = api.get_balances()
    print(bal)
    print(api.get_balance_amt('KRW-XRP'))
    print(api.get_orderbook('KRW-XRP'))
    print(api.get_current_price('KRW-XRP'))
