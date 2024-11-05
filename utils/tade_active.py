import time


class tade_active:
    """
    现货交易
    """
    def __init__(self, client):
        self.client = client

    def buy_coin(self, asset, buy_price, quantity, decimal_places):
        """
            代币购买调用方法
            asset 代币
            buy_price 购买目标价格
            quantity 购买总量
            decimal_places 代币价格精度
        """
        print("buy_price:[{}]".format(str(buy_price)))
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
                response = self.client.new_order(**params)
                buy_orderId = response['orderId']
                print(response)
                if len(self.client.get_open_orders()) == 1:
                    print("买入挂单成功,订单id：[{}]".format(str(buy_orderId)))
                break
            except Exception as e:
                time.sleep(10)
                print(f"买入挂单失败，重试中，发生了其他异常：{e}")
        return buy_orderId

    def sell_coin(self, asset, sell_price, quantity, decimal_places):
        """
            代币卖出调用方法
            asset 代币
            sell_price 卖出目标价格
            quantity 购买总量
            decimal_places 代币价格精度
            """
        print("sell_price:[{}]".format(str(sell_price)))
        params = {
            'symbol': '{}USDT'.format(asset),
            'side': 'SELL',
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'quantity': '{}'.format(quantity),
            'price': format(float(sell_price), f".{decimal_places}f")
        }
        print(str(params))
        while True:
            try:
                response = self.client.new_order(**params)
                sell_orderId = response['orderId']
                print(response)
                break
            except Exception as e:
                time.sleep(10)
                print(f"挂买单失败，发生了其他异常，重试中..：{e}")
        return sell_orderId

    def cancel_coin_order(self, asset, order_id):
        """
            取消订单方法
            asset 代币
            order_id 订单id
        """
        try:
            self.client.cancel_order(symbol='{}USDT'.format(asset), orderId=order_id)
            return True
        except Exception as e:
            time.sleep(10)
            print(f"取消订单失败，出现异常：[{e}]")
            return False
