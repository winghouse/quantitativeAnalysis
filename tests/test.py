from binance.spot import Spot


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
    usdt_free = None
    for balance in balances:
        if balance['asset'] == asset:
            print(balance)
            usdt_free = balance['free']
            break
    print("账户余额:{}{}".format(usdt_free, asset))
    return usdt_free


if __name__ == '__main__':
    client = Spot(api_key='xxxx',
                  api_secret='xxxx')
    print(getAccount(client, "FTT"))
    params = {
        'symbol': 'FTTUSDT',
        'side': 'SELL',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': '{}'.format(441.56),
        'price': '2.6838'
    }

    response = client.new_order(**params)
    print(response)

    # print(client.klines("FTTUSDT", "15m", limit=24))
    #
    # # 输入您的时间序列数据
    # data = client.klines("FTTUSDT", "15m", limit=24)
    #
    # # 转换数据为DataFrame
    # columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'timestamp_close', 'quote_asset_volume',
    #            'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore']
    # df = pd.DataFrame(data, columns=columns)
    #
    # # 将timestamp列转换为日期类型
    # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    #
    # # 设置日期为索引
    # df.set_index('timestamp', inplace=True)
    #
    # # 提取收盘价数据
    # ts = df['close'].astype(float)
    #
    # # # 绘制时间序列图
    # # plt.figure(figsize=(10, 6))
    # # plt.plot(ts, label='Close Price')
    # # plt.title('Time Series of Close Prices')
    # # plt.xlabel('Date')
    # # plt.ylabel('Close Price')
    # # plt.legend()
    # # plt.show()
    #
    # # 差分操作
    # ts_diff = ts.diff().dropna()
    #
    # # # 绘制差分后的时间序列图
    # # plt.figure(figsize=(10, 6))
    # # plt.plot(ts_diff, label='Differenced Close Price')
    # # plt.title('Differenced Time Series of Close Prices')
    # # plt.xlabel('Date')
    # # plt.ylabel('Differenced Close Price')
    # # plt.legend()
    # # plt.show()
    #
    # # 拟合ARIMA(1,1,1)模型
    # model = ARIMA(ts_diff, order=(1, 1, 1))
    # results = model.fit()
    #
    # # 预测未来一个时间点的差分值
    # forecast_diff = results.forecast(steps=1)[0]
    #
    # # 计算预测值
    # forecast_value = ts.iloc[-1] + forecast_diff
    #
    # print(f"Predicted Close Price for the next time point: {forecast_value}")
    #
    # # 转换数据为DataFrame
    # columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'timestamp_close', 'quote_asset_volume',
    #            'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore']
    # df = pd.DataFrame(data, columns=columns)
    #
    # # 将timestamp列转换为日期类型
    # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    #
    # # 设置日期为索引
    # df.set_index('timestamp', inplace=True)
    #
    # # 提取收盘价数据
    # returns = df['close'].astype(float).pct_change().dropna()
    #
    # # 拟合 GARCH(1, 1) 模型
    # model = arch_model(returns, vol='Garch', p=1, q=1)
    # results = model.fit()
    #
    # # 打印模型的统计信息
    # print(results.summary())
    #
    # # 预测未来的波动性
    # forecast_volatility = results.conditional_volatility[-1]
    #
    # print(f"Predicted volatility for the next time point: {forecast_volatility}")
    #
    # # 假设您已经拟合了 GARCH 模型并有了 forecast_volatility
    # forecast_mean = float(df['close'].iloc[-1])  # 假设最后一个收盘价是预测的均值
    #
    # # 计算置信区间
    # confidence_level = 0.95  # 95% 的置信水平
    # z_score = 1.96  # 对应于 95% 置信水平的 Z 分数
    #
    # # 计算置信区间的半宽度
    # confidence_interval_width = z_score * forecast_volatility
    #
    # # 计算置信区间的上下限
    # upper_bound = forecast_mean + confidence_interval_width
    # lower_bound = forecast_mean - confidence_interval_width
    #
    # print(f"Predicted price range at 95% confidence level: [{lower_bound}, {upper_bound}]")
    #
    #
    #
    # # Get account and balance information
    # # print(client.account())
    #
    # # Post a new order
    # # params = {
    # #     'symbol': 'FTTUSDT',
    # #     'side': 'BUY',
    # #     'type': 'LIMIT',
    # #     'timeInForce': 'GTC',
    # #     'quantity': 400,
    # #     'price': 2.6
    # # }
    # #
    # # response = client.new_order(**params)
    # # print(response)
    #
    #
    # # print(FTT['price'])
