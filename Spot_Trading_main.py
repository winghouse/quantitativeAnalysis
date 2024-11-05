import time

from binance.spot import Spot

from Biance.algorithms.KellyCalculator import KellyCalculator
from Biance.algorithms.VolatilityPriceAlgorithm import VolatilityPriceAlgorithm
import requests

# API key/secret are required for user data endpoints

# Get server timestamp
# print(client.time())
# Get klines of BTCUSDT at 1m interval
# print(client.klines("BTCUSDT", "1m"))
# Get last 10 klines of BNBUSDT at 1h interval
# print(client.klines("BNBUSDT", "1h", limit=10))
# print(client.klines("FTTUSDT", "15m", limit=1))


def getAccount(client, asset='USDT'):
    balances = client.account()['balances']
    # 遍历 balances 列表，找到 asset 为 'USDT' 的项，并获取其 free 值
    coin_free = None
    coin_lock = None
    for balance in balances:
        if balance['asset'] == asset:
            print(balance)
            coin_free = balance['free']
            coin_lock = balance['locked']
            break
    print("账户可用余额:{}{}\t 账户锁住余额:{}{}".format(coin_free, asset, coin_lock, asset))
    return coin_free, coin_lock

def message():
    appid = 'wx22ff070f7bb219b0'
    secret = ''
    url = ''
    response = requests.get(url)
    access_token = response.json().get('access_token')

    url_send = ''

    data = {}
    response = requests.post(url_send,json=data)

if __name__ == '__main__':
    """
    现货交易执行逻辑
    """
    print('启动机器人交易！！！')
    while True:
        try:
            api_key = 'xxxxxxx'
            api_secret = 'xxxxxxxxx'
            client = Spot(api_key=api_key, api_secret=api_secret)
            coin_list = ["PEOPLE", "WIF", "PEPE", "BOME","NOT","1000SATS","UNI"]
            for tade_coin in coin_list:
                print("计算代币：" + tade_coin)
                # USDT可用余额和锁住余额
                usdt_free, usdt_locked = getAccount(client)
                # 当前代币可用余额和锁住余额
                tade_coin_free, tade_coin_locked = getAccount(client, asset=tade_coin)
                # 当前价格
                coin_price = client.ticker_price(symbol='{}USDT'.format(tade_coin))['price']
                # 价格精度
                decimal_places = len(str(coin_price).split(".")[1]) if "." in str(coin_price) else 0
                if decimal_places >= 7:
                    decimal_places = 7
                print("price:{},{}", coin_price, str(decimal_places))
                # k线数据
                data = client.klines('{}USDT'.format(tade_coin), '15m', limit=60)
                print(str(data))
                # 波动预测价格
                buy_price = VolatilityPriceAlgorithm(data).LSTM_price()

                flow_per = 100 * (float(buy_price) - float(coin_price)) / float(buy_price)
                print(f"代币${tade_coin}预计振幅达" + str(flow_per) + "%")
                if flow_per >= 1.0:
                    print(f"代币${tade_coin}预计振幅达" + str(flow_per) + "%")



                # 凯莉公式
                win_rate = 0.6  # 胜率
                win_ratio = 2.0  # 获胜时的赔率
                capital = 1000  # 资本
                calculator = KellyCalculator(win_rate, win_ratio)
                kelly_fraction = calculator.calculate_kelly_fraction()
                optimal_bet_fraction = calculator.calculate_optimal_bet_fraction(capital)

            # 初始化网格交易模型
            # initial_balance = usdt_free  # 初始资金
            # grid_size = 0.035  # 网格大小
            #
            # grid_model = GridTradingModel(initial_balance, grid_size, api_key, api_secret)
            #
            # FTT = client.ticker_price(symbol='{}USDT'.format(tade_coin))['price']
            # print("price:{}", str(FTT))
            #
            # decimal_places = len(str(FTT).split(".")[1]) if "." in str(FTT) else 0
            # decimal_places = 49
            # if decimal_places >= 7:
            #     decimal_places = 7
            # print("price:{},{}", FTT, str(decimal_places))
            # price = float(FTT)  # 使用收盘价作为交易价格

            # grid_model.update_price(price)
            # grid_model.trade(tade_coin,decimal_places)
            # grid_model.print_status()
        except Exception as e:
            print(f"发生了其他异常：{e}")
        finally:

            time.sleep(10)

    # Get account and balance information
    # print(client.account())

    # Post a new order
    # params = {
    #     'symbol': 'FTTUSDT',
    #     'side': 'BUY',
    #     'type': 'LIMIT',
    #     'timeInForce': 'GTC',
    #     'quantity': 400,
    #     'price': 2.6
    # }
    #
    # response = client.new_order(**params)
    # print(response)

    # print(FTT['price'])
