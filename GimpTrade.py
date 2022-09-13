import pyupbit
import time
import datetime
import ccxt

# 업비트 키 로드
with open("keys/upbit_key.txt") as f:
    lines = f.readlines()
    access_key = lines[0].strip()
    secret_key = lines[1].strip()

upbit = pyupbit.Upbit(access_key, secret_key)

# 바이낸스 키 로드
with open("keys/binance_key.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret = lines[1].strip()

binance = ccxt.binance(config={
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})


def ticker_listmapping(c_ticker, c_exchange):
    result = []

    if c_exchange == 'upbit':
        for s in c_ticker:
            result.append("KRW-" + s)
    elif c_exchange == 'binance':
        for s in c_ticker:
            result.append(s + '/USDT')
    return result


def get_bal():
    # upbit = pyupbit.Upbit(access_key, secret_key)
    bals = upbit.get_balances()
    for bal in bals:
        if bal['currency'] == 'KRW':
            balance = bal['balance']
    return balance


# 청산
def exit(ticker):
    '''
    동시 전액 청산
    '''
    bi = ticker_listmapping(ticker, 'binance')[0]
    up = ticker_listmapping(ticker, 'upbit')[0]
    upcnt = upbit.get_balance(ticker=up)

    upbit.sell_market_order(up, upcnt)
    print("업비트청산", up, upcnt)

    time.sleep(0.2)

    balance = binance.fetch_balance()
    positions = balance['info']['positions']


    markets = binance.load_markets()
    market = binance.market(bi)
    for position in positions:
        if position["symbol"] == bi.replace("/", ''):
            c_position = position['positionAmt']
            bicnt = float(c_position)

    if bicnt < 0: #sell order기 때문에 양수로 바꿔줌
        bicnt = float(c_position) * -1

    print("바이낸스청산", bi, bicnt)


    order = binance.create_market_buy_order(
         symbol=bi,
         amount=bicnt
     )


# 진입
def entry(ticker, ratio):
    '''
    업비트는 시장가매수할때 금액으로 해야함.
    바이낸스 숏은 수량으로
    '''

    bi = ticker_listmapping(ticker, 'binance')[0]
    up = ticker_listmapping(ticker, 'upbit')[0]

    krw = get_bal() #업비트 원화조회
    krw = float(krw) * float(ratio)  # 들어갈 비율을 설정함


    beforecnt = upbit.get_balance(ticker=up)

    upbit.buy_market_order(up, krw)

    print("업비트매수", up, krw)
    time.sleep(0.2)
    bicnt = round(upbit.get_balance(ticker=up) - beforecnt, 4)  # 따로 체결완료 수량 조회방법이없어서 전과 후 차이를구해야함
    # print(upbit.get_order("KRW-XRP", state="cancel")[0])에서 state를 cancel로하면 시장가주문도 보임. done은 지정가주문만보임

    print("바이낸스헷징", bi, bicnt)



    markets = binance.load_markets()
    market = binance.market(bi)#레버리지율 조절하기 위해 market id load

    leverage = 1 #1배

    resp = binance.fapiPrivate_post_leverage({
        'symbol': market['id'],
        'leverage': leverage
    })

    order = binance.create_market_sell_order(
         symbol=bi,
         amount=bicnt
     )


if __name__ == '__main__':
    L_holding = ['ETC']
    exit(L_holding)


    # if entrygimp[0] < 0.3:
    #     entry(L_holding, 0.5)  -> bals 입력해줘됨(1, 비중, 김프,달러)
    # elif entrygimp[0] < 0.1 && 진입 1:
    #     entry(L_holding, 0.5)   -> bals 입력해줘됨(2, 비중, 김프,달러)
    #
    #     #진입 3번까지
    # if eixitgimp > avg(김프)*1.01: ->이때 시간을체크한다음에
    #     entry(L_holding, 0.3)
    # if eixitgimp > avg(김프)*1.015:
    #     entry(L_holding, 0.3)
    # if 3시간이 지나면 모두 청산.True
    #




