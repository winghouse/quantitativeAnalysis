import threading
import time
import logging
from typing import Any

from Biance.common.ConfigManager import ConfigManager
from Biance.strategies.Future_Trading import Future_Trading

from datetime import datetime, timedelta

from Biance.utils.DecimalUtils import get_decimal_places, format_value
from Biance.utils.MySQLUtils import MySQLUtils
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, filename='F:/Python-BianceBot/Biance/data/logs/Futures.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')


class KLineAnalysisThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.mysql = MySQLUtils()
        config = ConfigManager()
        self.coins = config.get('custom', 'kline_analysis_coin').split(',')
        self.table_name = "coin_kline_analysis"

        self.name = name

    def is_time_in_range(self):
        now = datetime.now()
        minute = now.minute
        return minute % 15 == 0 and now.second < 30

    def run(self):
        print("开始采集k线预测数据......")
        while True:
            # if self.is_time_in_range():
            for coin in self.coins:
                try:
                    future_trading = Future_Trading()
                    logging.info(f"starting analysis {coin}")
                    current_coin_price = future_trading.current_coin_price(coin)
                    decimal_places = get_decimal_places(current_coin_price)
                    predict_LSTM_price = format_value(future_trading.predict_LSTM_price(coin), decimal_places)
                    # 获取当前时间
                    current_time = datetime.now()
                    # 获取当前时间戳
                    current_timestamp = int(current_time.timestamp())
                    current_datetime = datetime.fromtimestamp(current_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    # 获取当前时间加 15 分钟后的时间戳
                    future_time = current_time + timedelta(minutes=15)
                    future_timestamp = int(future_time.timestamp())
                    future_datetime = datetime.fromtimestamp(future_timestamp).strftime('%Y-%m-%d %H:%M:%S')

                    data = [
                        {"coin": coin,
                         "current_coin_price": current_coin_price,
                         "predict_LSTM_price": str(predict_LSTM_price),
                         "`current_timestamp`": str(current_datetime),
                         "`predict_timestamp`": str(future_datetime)
                         }
                    ]

                    self.mysql.insert_data_to_mysql(self.table_name, data)
                    logging.info(f"finish analysis {coin}")
                    time.sleep(60)
                except Exception as error:
                    print("Found error. error message: {}".format(error))
                    logging.error("Found error. error message: {}".format(error))

# # 创建线程实例
# thread1 = KLineAnalysisThread("Thread-1")
# thread2 = KLineAnalysisThread("Thread-2")
#
# # 启动线程
# thread1.start()
# thread2.start()
#
# # 等待线程结束
# thread1.join()
# thread2.join()
#
# print("All threads have finished.")
