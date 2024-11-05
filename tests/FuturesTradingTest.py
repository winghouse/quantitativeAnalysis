import logging
from binance.um_futures import UMFutures
from binance.error import ClientError
from self import self

from Biance.algorithms.ArimaAAndArchAlgorith import ArimaAAndArchAlgorithm
from Biance.algorithms.VolatilityPriceAlgorithm import VolatilityPriceAlgorithm
from Biance.common.ConfigManager import ConfigManager
from Biance.dao.AccountBalance import parse_account_balance

logging.basicConfig(level=logging.DEBUG, filename='F:/Python-BianceBot/Biance/data/logs/Futures.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')


class FuturesTradingTest:
    def __init__(self):
        config = ConfigManager()
        self.key = config.get('api', 'key')
        self.secret = config.get('api', 'secret')

    def coinTrading(self):
        um_futures_client = UMFutures()
        klines_data = um_futures_client.klines("BIGTIMEUSDT", "15m", limit=672)
        VolatilityPriceAlgorithm(klines_data).LSTM_price()
        ArimaAAndArchAlgorithm(klines_data).calculate_ARIMA_ARCH_prices(2)

    def my_account(self):
        # HMAC authentication with API key and secret
        hmac_client = UMFutures(key=self.key, secret=self.secret)

        try:
            account_json = hmac_client.balance(recvWindow=6000)
            account_usdt = parse_account_balance(account_json)
            print(account_usdt)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
    def current_coin_price(self,coin):
        um_futures_client = UMFutures()
        current_price = um_futures_client.ticker_price(coin)["price"]
        logging.info(current_price)
        print(current_price)



"""合约交易执行类"""
# 我的合约账户余额
# FuturesTradingTest().my_account()

# 当前代币价格
# FuturesTradingTest().current_coin_price("BTCUSDT")


