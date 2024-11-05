import time

from Biance.algorithms.KellyCalculator import KellyCalculator
import logging
from binance.um_futures import UMFutures
from binance.error import ClientError

from Biance.algorithms.ArimaAAndArchAlgorith import ArimaAAndArchAlgorithm
from Biance.algorithms.VolatilityPriceAlgorithm import VolatilityPriceAlgorithm
from Biance.common.ConfigManager import ConfigManager
from Biance.dao.AccountBalance import parse_account_balance
import logging

from Biance.utils.DecimalUtils import format_value

logging.basicConfig(level=logging.DEBUG, filename='F:/Python-BianceBot/Biance/data/logs/Futures.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')


class Future_Trading:
    """
    USDT本位合约交易
    """

    def __init__(self):
        config = ConfigManager()
        self.key = config.get('api', 'key')
        self.secret = config.get('api', 'secret')
        self.coins = config.get('custom', 'coin')
        self.timeslice = config.get('custom', 'timeslice')
        self.kelly_win_rate = config.get('custom', 'kelly_win_rate')
        self.investment_amount = config.get('custom', 'investment_amount')
        self.leverage_ratio = float(config.get('custom', 'leverage_ratio'))
        self.um_futures_client = UMFutures()
        # HMAC authentication with API key and secret
        self.hmac_client = UMFutures(key=self.key, secret=self.secret)
        self.short_clientOrderId = ""
        self.short_orderId = 0
        self.short_stop_clientOrderId = ""
        self.short_stop_orderId = 0
        self.long_clientOrderId = ""
        self.long_orderId = 0

    def my_account(self):
        try:
            account_json = self.hmac_client.balance(recvWindow=6000)
            account_usdt = parse_account_balance(account_json)
            print(account_usdt)
            return account_usdt
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    def get_coin(self):
        """
        返回代币列表
        :return:代币列表
        """
        return self.coins.split(',')

    def predict_LSTM_price(self, coin):
        """
        :return:返回1-2 周期的预期值
        """
        klines_data = self.um_futures_client.klines(coin, self.timeslice, limit=672)
        # print(f"k线：{klines_data}")
        return VolatilityPriceAlgorithm(klines_data).LSTM_price_V1()

    def predict_ARIMA_ARCH_prices(self, coin):
        """
        :return: [预测值、最小边界值、最大边界值]
        """
        klines_data = self.um_futures_client.klines(coin, self.timeslice, limit=672)
        return ArimaAAndArchAlgorithm(klines_data).calculate_ARIMA_ARCH_prices(2)

    def current_coin_price(self, coin):
        """
        获取当前代币价格
        :param coin: 代币
        :return: 当前价格
        """
        um_futures_client = UMFutures()
        return um_futures_client.ticker_price(coin)["price"]

    def quantity(self, investment_capital, current_coin_price):
        return format_value(self.leverage_ratio * float(investment_capital) / float(current_coin_price), 0)

    def wait_trade_finished(self, response, coin):
        """
        等待交易完成
        :param response:
        :param coin:
        :return:
        """
        flag = 1
        if response is not None:
            clientOrderId = response["clientOrderId"]
            orderId = response["orderId"]
        else:
            print(f"代币{coin}存在挂单，等待完成交易...")
            clientOrderId = None
            orderId = None
            flag = 0
        isExecuted = 1
        while isExecuted:
            try:
                if flag :
                    response = self.hmac_client.get_open_orders(
                        symbol=coin, orderId=orderId, clientOrderId=clientOrderId,
                        recvWindow=2000
                    )
                else:
                    response = self.hmac_client.get_orders(
                        symbol=coin, recvWindow=2000
                    )
                    if len(response) == 0 :
                        isExecuted = 0
                        print(f"当前不存在代币{coin}的挂单，继续执行交易")
                logging.info(response)
            except ClientError as error:
                if "Order does not exist." in error.error_message:
                    isExecuted = 0
                print("等待交易完成......")
                time.sleep(10)
                logging.error(
                    "Found error. status: {}, error code: {}, error message: {}".format(
                        error.status_code, error.error_code, error.error_message
                    )
                )

    def kelly_investment_strategy(self, predict_LSTM_volatility):
        """
        凯莉公式——投资策略
        :param predict_LSTM_volatility: 波动幅度
        :return:
        """
        win_ratio = float(self.leverage_ratio) * abs(predict_LSTM_volatility)  # 获胜时的赔率
        calculator = KellyCalculator(self.kelly_win_rate, win_ratio)
        kelly_fraction = format_value(calculator.calculate_kelly_fraction(), 2)
        optimal_bet_fraction = format_value(calculator.calculate_optimal_bet_fraction(self.investment_amount), 2)
        print(f"凯利公式比例因子：{kelly_fraction:.2f}")
        print(f"最优下注比例：{optimal_bet_fraction:.2f}")
        return kelly_fraction, optimal_bet_fraction

    def short_selling(self, coin, current_coin_price: float, investment_capital: float):
        """
        做空交易
        https://developers.binance.com/docs/zh-CN/derivatives/usds-margined-futures/trade/rest-api
        :param coin: 代币
        :param current_coin_price: 当前价格
        :param investment_capital: 投资比例资金
        :return:
        """
        if self.my_account().available_balance > investment_capital:
            quantity = self.quantity(investment_capital, current_coin_price)
            # quantity = format_value(self.leverage_ratio * float(investment_capital) / float(current_coin_price), 0)
            try:
                response = self.hmac_client.change_leverage(
                    symbol=coin, leverage=int(self.leverage_ratio), recvWindow=6000
                )
                logging.info(response)
                print(response)
            except ClientError as error:
                logging.error(
                    "Found error. status: {}, error code: {}, error message: {}".format(
                        error.status_code, error.error_code, error.error_message
                    )
                )

            try:
                response = self.hmac_client.new_order(
                    symbol=coin,
                    side="SELL",
                    positionSide="SHORT",
                    type="LIMIT",
                    quantity=quantity,
                    timeInForce="GTC",
                    price=current_coin_price,
                )
                print(response)
                self.short_clientOrderId = response["clientOrderId"]
                self.short_orderId = response["orderId"]
                print(f"执行做空交易，价格：{current_coin_price},交易总量：{quantity}USDT")
                self.wait_trade_finished(response, coin)
                print(f"执行做空交易成功！！！")
            except ClientError as error:
                print("Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message))
                logging.error(
                    "Found error. status: {}, error code: {}, error message: {}".format(
                        error.status_code, error.error_code, error.error_message
                    )
                )

    def close_short_position(self, coin, stop_price):
        """
        平仓空头仓位
        :param coin:
        :param stop_price:
        :return:
        STOP_MARKET, TAKE_PROFIT_MARKET 配合 closePosition=true:

        条件单触发依照上述条件单触发逻辑
        条件触发后，平掉当时持有所有多头仓位(若为卖单)或当时持有所有空头仓位(若为买单)
        不支持 quantity 参数
        自带只平仓属性，不支持reduceOnly参数
        双开模式下,LONG方向上不支持BUY; SHORT 方向上不支持SELL
        """
        try:
            response = self.hmac_client.new_order(
                symbol=coin,
                side="BUY",
                positionSide="SHORT",
                type="TAKE_PROFIT_MARKET",
                timeInForce="GTC",
                stopPrice=stop_price,
                closePosition="true",
            )
            logging.info(response)
            print(response)
            self.short_stop_clientOrderId = response["clientOrderId"]
            self.short_stop_orderId = response["orderId"]
            print(f"执行平空交易，价格：{stop_price}")
            self.wait_trade_finished(response, coin)
            print(f"执行平多交易成功！")
        except ClientError as error:
            print("Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message))
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    def long_buying(self, coin, current_coin_price: float, investment_capital: float):
        """
        做多交易
        https://developers.binance.com/docs/zh-CN/derivatives/usds-margined-futures/trade/rest-api
        :param coin: 代币
        :param current_coin_price: 当前价格
        :param investment_capital: 投资比例资金
        :return:
        """
        # quantity = format_value(self.leverage_ratio * float(investment_capital) / float(current_coin_price), 0)
        quantity = self.quantity(investment_capital, current_coin_price)
        try:
            response = self.hmac_client.change_leverage(
                symbol=coin, leverage=int(self.leverage_ratio), recvWindow=6000
            )
            logging.info(response)
            print(response)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

        try:
            response = self.hmac_client.new_order(
                symbol=coin,
                side="BUY",
                positionSide="LONG",
                type="LIMIT",
                quantity=quantity,
                timeInForce="GTC",
                price=current_coin_price,
            )
            print(response)
            self.long_clientOrderId = response["clientOrderId"]
            self.long_orderId = response["orderId"]
            print(f"执行做多交易，价格：{current_coin_price},交易总量：{quantity}USDT")
            self.wait_trade_finished(response, coin)
            print(f"执行做多交易成功！！！")
        except ClientError as error:
            print("Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message))
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    def close_long_position(self, coin, stop_price):
        """
        平仓多头仓位
        :param coin:
        :param stop_price:
        :return:
        条件单触发依照上述条件单触发逻辑
        条件触发后，平掉当时持有所有多头仓位(若为卖单)或当时持有所有空头仓位(若为买单)
        不支持 quantity 参数
        自带只平仓属性，不支持reduceOnly参数
        双开模式下,LONG方向上不支持BUY; SHORT 方向上不支持SELL
        """
        try:
            response = self.hmac_client.new_order(
                symbol=coin,
                side="SELL",
                positionSide="LONG",
                type="TAKE_PROFIT_MARKET",
                timeInForce="GTC",
                stopPrice=stop_price,
                closePosition="true",
            )

            logging.info(response)
            print(response)
            print(f"执行平多交易，价格：{stop_price}")
            self.wait_trade_finished(response, coin)
            print(f"执行平多交易成功！！！")
        except ClientError as error:
            print("Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message))
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
