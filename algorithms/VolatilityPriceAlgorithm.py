import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping


class VolatilityPriceAlgorithm:
    """
        LSTM交易预测模型
    """

    def __init__(self, data):
        self.data = data

    def LSTM_price_V1(self):
        # 数据准备
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'timestamp_end', 'amount', 'count',
                   'buy_volume', 'buy_amount', 'ignore']
        df = pd.DataFrame(self.data, columns=columns)

        # 选择用于训练的特征（可以选择多个特征）
        self.data = df[['close', 'open', 'high', 'low', 'volume']].values.astype(float)

        # 归一化数据
        scaler = MinMaxScaler(feature_range=(0, 1))
        data_normalized = scaler.fit_transform(self.data)

        # 准备数据（假设使用前60个时间步来预测未来的价格）
        X, y = [], []
        for i in range(60, len(data_normalized)):
            X.append(data_normalized[i - 60:i, :])  # 使用前60个时间步的所有特征
            y.append(data_normalized[i, 0])  # 预测收盘价
        X, y = np.array(X), np.array(y)

        # 将数据转换为LSTM模型的输入格式 [samples, time steps, features]
        X = np.reshape(X, (X.shape[0], X.shape[1], X.shape[2]))

        # 构建LSTM模型
        model = Sequential()
        model.add(LSTM(units=100, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
        model.add(Dropout(0.2))  # 添加Dropout层以防止过拟合
        model.add(LSTM(units=100))
        model.add(Dropout(0.2))  # 再次添加Dropout层
        model.add(Dense(units=1))  # 输出层，预测收盘价

        # 编译模型
        model.compile(optimizer='adam', loss='mean_squared_error')

        # 早停机制
        early_stopping = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)

        # 训练模型
        model.fit(X, y, epochs=100, batch_size=32, callbacks=[early_stopping])

        # 预测未来的价格
        future_data = data_normalized[-60:].reshape((1, 60, 5))  # 使用最近的60个时间步
        future_price_normalized = model.predict(future_data)
        # 确保提取单个元素
        future_price = scaler.inverse_transform(np.concatenate((future_price_normalized, np.zeros((1, 4))), axis=1))[:,
                       0]

        # 使用 item() 方法提取标量
        predicted_price = future_price.item()
        print(f"未来1到2个周期时间的价格预测：{predicted_price}")

        return predicted_price

    def LSTM_price(self):
        # self.data = [
        #     [1712306700000, '0.96900000', '0.97000000', '0.95100000', '0.96200000', '1673578.30000000', 1712307599999,
        #      '1603244.09960000', 2840, '648739.10000000', '621718.78930000', '0'],
        #     [1712307600000, '0.96200000', '0.97500000', '0.95600000', '0.97400000', '1124519.60000000', 1712308499999,
        #      '1085857.83480000', 2147, '578453.00000000', '558976.37080000', '0'],
        #     [1712308500000, '0.97500000', '0.98400000', '0.96000000', '0.98300000', '1211181.10000000', 1712309399999,
        #      '1174967.67440000', 2321, '642054.60000000', '623420.51520000', '0']
        #     # 添加更多的数据
        # ]

        # 将数据转换为DataFrame
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'timestamp_end', 'amount', 'count',
                   'buy_volume', 'buy_amount', 'ignore']
        df = pd.DataFrame(self.data, columns=columns)

        # 选择用于训练的特征（这里简单地选择了收盘价）
        self.data = df['close'].values.astype(float).reshape(-1, 1)

        # 归一化数据
        scaler = MinMaxScaler(feature_range=(0, 1))
        data_normalized = scaler.fit_transform(self.data)

        # 准备数据（假设使用前3个时间步来预测未来的价格）
        X, y = [], []
        for i in range(30, len(data_normalized)):
            X.append(data_normalized[i - 30:i, 0])
            y.append(data_normalized[i, 0])
        X, y = np.array(X), np.array(y)

        # 将数据转换为LSTM模型的输入格式 [samples, time steps, features]
        # 将数据转换为LSTM模型的输入格式 [样本数, 时间步数, 特征数]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        # 构建LSTM模型
        model = Sequential()  # 创建一个顺序模型
        model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
        # 添加LSTM层，units指定输出空间的维度，return_sequences=True表示返回所有时间步的输出
        model.add(LSTM(units=50))  # 添加第二个LSTM层
        model.add(Dense(units=1))  # 添加输出层，units=1表示输出一个预测值

        # 编译模型
        # 也可以尝试其他优化器，如RMSprop或自适应学习率优化器（如AdamW）来更好地适应不同的学习率情况。损失函数方面，你可以尝试huber_loss，它在处理噪声数据时可能表现得更好。
        model.compile(optimizer='adam', loss='mean_squared_error')
        # 指定优化器为Adam，损失函数为均方误差（MSE）

        # 训练模型
        model.fit(X, y, epochs=100, batch_size=32)
        # 训练模型，epochs指定训练的轮数，batch_size指定每个批次的样本数量

        # 预测未来的价格
        future_data = data_normalized[-10:].reshape((1, 10, 1))
        # 取最后10个归一化数据，并调整形状以适应模型输入
        future_price_normalized = model.predict(future_data)
        # 使用模型进行价格预测
        future_price = scaler.inverse_transform(future_price_normalized).item()
        print(f"未来1到2个周期时间的价格预测：{future_price}")

        return future_price
