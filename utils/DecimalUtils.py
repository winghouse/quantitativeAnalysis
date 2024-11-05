from decimal import Decimal, getcontext


def get_decimal_places(value):
    """
    获取小数点后的位数
    :param value: 需要检查的数值
    :return: 小数点后的位数
    """
    # 转换为 Decimal 类型
    decimal_value = Decimal(str(value))
    # 获取小数点后的位数
    return abs(decimal_value.as_tuple().exponent)


def format_value(value, decimal_places):
    """
    将数值格式化为指定的小数位数
    :param value: 需要格式化的数值
    :param decimal_places: 小数位数
    :return: 格式化后的字符串
    """
    # 设置 Decimal 的精度
    getcontext().prec = decimal_places + 10
    decimal_value = Decimal(str(value))
    # 格式化数值
    formatted_value = decimal_value.quantize(Decimal('1.' + '0' * decimal_places))
    return formatted_value


def volatility_down_or_up(current_coin_price: float, predict_LSTM_price: float):
    return float(format(((predict_LSTM_price - current_coin_price) * 100) / predict_LSTM_price, f".2f"))
