import math
import time
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from binance.spot import Spot
import pandas as pd


def getAccount(client, asset='USDT'):
    balances = client.account()['balances']
    # 遍历 balances 列表，找到 asset 为 'USDT' 的项，并获取其 free 值
    usdt_free = None
    for balance in balances:
        if balance['asset'] == asset:
            print(balance)
            usdt_free = balance['free']
            break
    print("账户余额:{}{}".format(usdt_free, asset))
    return usdt_free


class GridTradingModel:
    """
    现货交易
    """
    def __init__(self, initial_balance, grid_size, api_key, api_secret):
        self.balance = initial_balance
        # 交易网格大小
        self.grid_size = grid_size
        self.lower_bound = 0
        self.upper_bound = 0
        self.current_price = 0
        self.api_key = api_key
        self.api_secret = api_secret

    def update_price(self, price):
        """
        更新当前价格
        :param price: 当前交易价格
        """
        self.current_price = price

    def calculate_bounds(self):
        """
        计算交易区间，保留8位小数
        :return:
        """
        half_grid = self.grid_size / 2
        self.lower_bound = round(self.current_price - half_grid, 8)
        self.upper_bound = round(self.current_price + half_grid, 8)

    def calculate_optimal_prices(self):
        """
        计算最佳买单和卖单价格
        """
        self.calculate_bounds()

        # 计算最优的买单和卖单价格
        buy_price = round(self.lower_bound - self.grid_size, 8)
        sell_price = round(self.upper_bound + self.grid_size, 8)

        return buy_price, sell_price

    def calculate_up_down_prices(self, client, asset, time):
        """计算价格波动是否过大，过大则不执行交易"""
        while True:
            try:
                data = client.klines("{}USDT".format(asset), time, limit=2)
                break
            except Exception as e:
                time.sleep(30)
                print(f"获取k线失败，重试中：{e}")
        datas = [float(item[4]) for item in data]
        if (1.0 - (datas[1] / datas[0])) > 0.07:
            print("波动过大，不执行买单")
            return False
        else:
            return True

    def calculate_ARIMA_ARCH_prices(self, client, asset, time, decimal_places):
        """
        预测模型——ARIMA—ARCH
        :param client: API客户端
        :param asset: 代币
        :param time: 计算时间
        :param decimal_places: 预测价格精确度
        :return:
        """
        while True:
            try:
                data = client.klines("{}USDT".format(asset), time, limit=24)
                print("time:{},data:{}".format(time, data))
                break
            except Exception as e:
                time.sleep(10)
                print(f"获取k线失败，重试中：{e}")

        # 转换数据为DataFrame
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'timestamp_close', 'quote_asset_volume',
                   'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore']
        df = pd.DataFrame(data, columns=columns)
        # 将timestamp列转换为日期类型
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        # 设置日期为索引
        df.set_index('timestamp', inplace=True)
        # 提取收盘价数据
        ts = df['close'].astype(float)
        # 差分操作
        ts_diff = ts.diff().dropna()
        # 拟合ARIMA(1,1,1)模型
        model = ARIMA(ts_diff, order=(1, 1, 1))
        results = model.fit()
        # 预测未来一个时间点的差分值
        forecast_diff = results.forecast(steps=1)[0]
        # 计算预测值
        forecast_value = float(ts.iloc[-1] + forecast_diff)
        print(f"预测下个收盘价为: {forecast_value}")

        # 提取收盘价数据
        returns = df['close'].astype(float).pct_change().dropna()

        # 拟合 GARCH(1, 1) 模型
        model = arch_model(returns, vol='Garch', p=1, q=1)
        results = model.fit()

        # 打印模型的统计信息
        print(results.summary())

        # 预测未来的波动性
        forecast_volatility = results.conditional_volatility[-1]

        print(f"Predicted volatility for the next time point: {forecast_volatility}")

        # 假设您已经拟合了 GARCH 模型并有了 forecast_volatility
        forecast_mean = float(df['close'].iloc[-1])  # 假设最后一个收盘价是预测的均值

        # 计算置信区间
        confidence_level = 0.95  # 95% 的置信水平
        z_score = 1.96  # 对应于 95% 置信水平的 Z 分数

        # 计算置信区间的半宽度
        confidence_interval_width = z_score * forecast_volatility

        # 计算置信区间的上下限
        upper_bound = forecast_mean + confidence_interval_width
        lower_bound = forecast_mean - confidence_interval_width

        print(f"Predicted price range at 95% confidence level: [{lower_bound}, {upper_bound}]")
        return format(forecast_value, f".{decimal_places}f"), format(lower_bound, f".{decimal_places}f"), format(
            upper_bound, f".{decimal_places}f")

    def trade(self, asset, decimal_places):
        """现货交易逻辑"""
        global buy_price, quantity, sell_price, forecast_price
        if self.lower_bound < self.current_price < self.upper_bound:
            return  # 当前价格在网格范围内，不执行交易
        try:
            client = Spot(api_key=self.api_key,
                          api_secret=self.api_secret)
            # 获取预测15m、30m、1h：k线预测值、波动最小值和波动最大值
            forecast_price_1h, buy_price_1h, sell_price_1h = self.calculate_ARIMA_ARCH_prices(client, asset, "1h",
                                                                                              decimal_places)
            forecast_price_30m, buy_price_30m, sell_price_30m = self.calculate_ARIMA_ARCH_prices(client, asset, "30m",
                                                                                                 decimal_places)
            forecast_price_15m, buy_price_15m, sell_price_15m = self.calculate_ARIMA_ARCH_prices(client, asset, "15m",
                                                                                                 decimal_places)

            print("forecast_price_1h:{}, buy_price_1h:{}, sell_price_1h:{}".format(forecast_price_1h, buy_price_1h,
                                                                                   sell_price_1h))
            print("forecast_price_30m:{}, buy_price_30m:{}, sell_price_30m:{}".format(forecast_price_30m, buy_price_30m,
                                                                                      sell_price_30m))
            print("forecast_price_15m:{}, buy_price_15m:{}, sell_price_15m:{}".format(forecast_price_15m, buy_price_15m,
                                                                                      sell_price_15m))
            # 取预测均数
            forecast_price = (float(forecast_price_1h) + float(forecast_price_30m) + float(forecast_price_15m)) / 3.0
            buy_price = (float(buy_price_1h) + float(buy_price_30m) + float(buy_price_15m)) / 3.0
            if forecast_price/buy_price > 1.1 or forecast_price/buy_price < 0:
                buy_price = forecast_price * 0.98
            sell_price = (float(sell_price_1h) + float(sell_price_30m) + float(sell_price_15m)) / 3.0
            if sell_price / forecast_price > 1.1 or sell_price / forecast_price < 0:
                sell_price = forecast_price * 1.02


            # 判断买卖价波动不能小于网格区间
            # if float(sell_price)/float(self.current_price) >= 1.01:
            #     sell_price = "{:.4f}".format(self.current_price + self.grid_size)
            # if float(self.current_price)/float(buy_price) >= 1.01 :
            #     buy_price = "{:.4f}".format(self.current_price - self.grid_size)
            # 计算购买总数量
            quantity = math.floor(float(self.balance) / float(buy_price))
            flag = False
            print(
                "forecast_price:{},buy_price:{},sell_price：{},balance:{},quantity:{}".format(forecast_price, buy_price,
                                                                                             sell_price, self.balance,
                                                                                             quantity))
            print("self.getAccount(client):" + str(getAccount(client)))
        except Exception as e:
            time.sleep(10)
            client = Spot(api_key=self.api_key,
                          api_secret=self.api_secret)
            print(f"client发生了其他异常,但重试成功了：{e}")

        orderId = None
        # 执行买单
        while True:
            try:
                current = float(getAccount(client))
                coin_price = client.ticker_price(symbol='{}USDT'.format(asset))['price']
                price = float(coin_price)  # 使用收盘价作为交易价格
                break
            except Exception as e:
                time.sleep(10)
                print(f"获取余额失败，发生了其他异常，重试中..：{e}")

        if price > forecast_price:
            print("当前价格大于预测价格")

        if current > 100.0 and price < forecast_price and self.calculate_up_down_prices(client, asset, "15m") and float(
                self.current_price) / float(buy_price) >= 1.01 and float(self.current_price) / float(buy_price) >= 1.01:
            print("buy_price:" + str(buy_price))
            params = {
                'symbol': '{}USDT'.format(asset),
                'side': 'BUY',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': '{}'.format(quantity),
                'price': "{}".format(float(buy_price), f".{decimal_places}f")
            }
            print(str(params))
            while True:
                try:
                    response = client.new_order(**params)
                    orderId = response['orderId']
                    print(response)
                    if len(client.get_open_orders()) == 1:
                        print("买入挂单成功")
                    break
                except Exception as e:
                    time.sleep(10)
                    print(f"买入挂单失败，重试中，发生了其他异常：{e}")

            wait_buy = True
            while True:
                try:
                    print("等待买入中...")
                    if wait_buy:
                        time.sleep(900)
                        wait_buy = False
                    else:
                        time.sleep(30)
                    if len(client.get_open_orders()) != 1:
                        print("买入成功")
                        flag = True
                        break
                    else:
                        print("超时没买入，重新挂单")
                        client.cancel_order(symbol='{}USDT'.format(asset), orderId=orderId)
                        flag = False
                        break
                except Exception as e:
                    print(f"发生了其他异常：{e}")

        while True:
            try:
                current = float(getAccount(client))
                asset_num = "{:.1f}".format(float(getAccount(client, asset)) - 1)
                break
            except Exception as e:
                time.sleep(3)
                print(f"获取余额失败，发生了其他异常，重试中..：{e}")

        # 执行卖单
        if current < 100.0 and (flag == True or float(asset_num) > 10):

            print("sell_price:" + str(sell_price))
            params = {
                'symbol': '{}USDT'.format(asset),
                'side': 'SELL',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': '{}'.format(asset_num),
                'price': format(float(sell_price), f".{decimal_places}f")
            }
            print(str(params))
            while True:
                try:
                    response = client.new_order(**params)
                    print(response)
                    break
                except Exception as e:
                    time.sleep(10)
                    print(f"挂买单失败，发生了其他异常，重试中..：{e}")
        wait_sell = True
        while True:
            try:
                if len(client.get_open_orders()) != 1:
                    print("卖出成功")
                    wait_sell = False

                    break
                print("等待卖出中...")
                if wait_sell:
                    time.sleep(300)
                    wait_sell = False
                else:
                    time.sleep(30)
            except Exception as e:
                print(f"发生了其他异常：{e}")

        # 更新交易后的界限
        self.calculate_bounds()

    def print_status(self):
        print(
            f"当前价格: {self.current_price}, 账户余额: {self.balance}, 网格范围: ({self.lower_bound}, {self.upper_bound})")
