from abc import *

class APIManager(metaclass=ABCMeta):

    #return: Dataframe
    @abstractmethod
    def get_ohlcv(self, ticker):
        raise NotImplemented

    #잔고
    #return: dictionary
    #Ex: {'DOT': 0.0, 'BTC': 0.0, 'SOL': 0.0, 'BNB': 0.0, 'ETH': 0.0, 'ADA': 0.0, 'USDT': 355.23399767, 'XRP': 0.0, 'USDC': 0.0, 'BUSD': 0.0}
    @abstractmethod
    def get_balances(self):
        raise NotImplemented

    #해당 종목의 잔고수량
    @abstractmethod
    def get_balance_amt(self, ticker):
        raise NotImplemented

    #호가창
    @abstractmethod
    def get_orderbook(self, ticker):
        raise NotImplemented

    @abstractmethod
    def get_current_price(self, ticker):
        raise NotImplemented

    @abstractmethod
    def sell(self):
        raise NotImplemented

    @abstractmethod
    def buy(self):
        raise NotImplemented

    @abstractmethod
    def buy_target(self):
        raise NotImplemented
