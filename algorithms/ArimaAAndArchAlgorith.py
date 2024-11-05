from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
import pandas as pd


class ArimaAAndArchAlgorithm:
    """
    ARIMA-ARCH 价格预测模型
    """

    def __init__(self, data):
        self.data = data

    def calculate_ARIMA_ARCH_prices(self, decimal_places):
        """
        预测模型——ARIMA—ARCH
        :param decimal_places: 预测价格精确度
        :return:
        """
        # 转换数据为DataFrame
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'timestamp_close', 'quote_asset_volume',
                   'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore']
        df = pd.DataFrame(self.data, columns=columns)
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
