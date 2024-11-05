import time

from Biance.strategies.Future_Trading import Future_Trading
import logging

from Biance.utils.DecimalUtils import get_decimal_places, volatility_down_or_up, format_value

logging.basicConfig(level=logging.DEBUG, filename='F:/Python-BianceBot/Biance/data/logs/Futures.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

if __name__ == '__main__':
    """合约交易执行类"""
    while True:
        try:
            future_trading = Future_Trading()
            coins = future_trading.get_coin()

            for coin in coins:
                # 预测大盘走势
                BTC_predict_LSTM_price = future_trading.predict_LSTM_price("BTCUSDT")
                BTC_current_coin_price = future_trading.current_coin_price("BTCUSDT")
                BTC_decimal_places = get_decimal_places(BTC_current_coin_price)
                BTC_predict_LSTM_volatility = volatility_down_or_up(float(BTC_current_coin_price),
                                                                    float(BTC_predict_LSTM_price))
                # 查看是否有存在该代币的挂单，有的话，等待成交
                future_trading.wait_trade_finished(None, coin)
                # LSTM算法预测价格
                predict_LSTM_price = future_trading.predict_LSTM_price(coin)
                # 波动计算
                current_coin_price = future_trading.current_coin_price(coin)
                # 获取价格精度
                decimal_places = get_decimal_places(current_coin_price)
                # 获取预测上涨或下跌幅度
                predict_LSTM_volatility = 0
                if float(current_coin_price) > 0:
                    predict_LSTM_volatility = volatility_down_or_up(float(current_coin_price),
                                                                    float(predict_LSTM_price))
                    # 判断上涨或下跌
                    if predict_LSTM_volatility > 0:
                        print(
                            f"预测{coin}将上涨 {predict_LSTM_volatility}%,当前价格为{current_coin_price},预测价格为{format_value(predict_LSTM_price, decimal_places)}")
                        if predict_LSTM_volatility > 0.4 and BTC_predict_LSTM_volatility > -0.4:
                            print(
                                f"预测BTC将上涨 {BTC_predict_LSTM_volatility}%,当前价格为{BTC_current_coin_price},预测价格为{format_value(BTC_predict_LSTM_price, BTC_decimal_places)}")
                            investment_ratio, investment_capital = future_trading.kelly_investment_strategy(
                                predict_LSTM_volatility)
                            future_trading.long_buying(coin,
                                                       format_value(float(current_coin_price) * 0.995, decimal_places),
                                                       investment_capital)
                            # future_trading.close_long_position(coin, format_value(float(current_coin_price) * (1 + (predict_LSTM_volatility / 100)), decimal_places))
                            future_trading.close_long_position(coin, format_value(float(current_coin_price) * 1.005, decimal_places))
                    else:
                        print(
                            f"预测{coin}将下跌 {predict_LSTM_volatility}%,当前价格为{current_coin_price},预测价格为{format_value(predict_LSTM_price, decimal_places)}")
                        if predict_LSTM_volatility < -0.4 and BTC_predict_LSTM_volatility < 0.4:
                            print(
                                f"预测BTC将下跌 {BTC_predict_LSTM_volatility}%,当前价格为{BTC_current_coin_price},预测价格为{format_value(BTC_predict_LSTM_price, BTC_decimal_places)}")
                            investment_ratio, investment_capital = future_trading.kelly_investment_strategy(
                                predict_LSTM_volatility)
                            future_trading.short_selling(coin, format_value(float(current_coin_price) * 1.005,
                                                                            decimal_places),
                                                         investment_capital)
                            # future_trading.close_short_position(coin, format_value(float(current_coin_price) * (1 + (predict_LSTM_volatility / 100)), decimal_places))
                            future_trading.close_short_position(coin, format_value(float(current_coin_price) * 0.995, decimal_places))

        except Exception as e:
            print(f"执行合约交易失败,出现异常：{e.__str__()}")

        print("交易执行周期结束，60秒后进入下一个交易执行周期...")
        time.sleep(60)
