import json
from typing import List, Dict


class AccountBalance:
    def __init__(self, account_alias: str, asset: str, balance: float, cross_wallet_balance: float,
                 cross_un_pnl: float, available_balance: float, max_withdraw_amount: float,
                 margin_available: bool, update_time: int):
        self.account_alias = account_alias  # 账户唯一识别码
        self.asset = asset  # 资产类型（例如 USDT）
        self.balance = balance  # 总余额
        self.cross_wallet_balance = cross_wallet_balance  # 全仓余额
        self.cross_un_pnl = cross_un_pnl  # 全仓持仓未实现盈亏
        self.available_balance = available_balance  # 下单可用余额
        self.max_withdraw_amount = max_withdraw_amount  # 最大可转出余额
        self.margin_available = margin_available  # 是否可用作联合保证金
        self.update_time = update_time  # 数据更新时间（Unix时间戳）

    def __repr__(self):
        return (f"AccountBalance(account_alias={self.account_alias}, asset={self.asset}, balance={self.balance}, "
                f"cross_wallet_balance={self.cross_wallet_balance}, cross_un_pnl={self.cross_un_pnl}, "
                f"available_balance={self.available_balance}, max_withdraw_amount={self.max_withdraw_amount}, "
                f"margin_available={self.margin_available}, update_time={self.update_time})")


def parse_account_balance(data: str) -> AccountBalance:
    for item in data:
        if item["asset"] == "USDT":
            return AccountBalance(
                account_alias=item["accountAlias"],
                asset=item["asset"],
                balance=float(item["balance"]),
                cross_wallet_balance=float(item["crossWalletBalance"]),
                cross_un_pnl=float(item["crossUnPnl"]),
                available_balance=float(item["availableBalance"]),
                max_withdraw_amount=float(item["maxWithdrawAmount"]),
                margin_available=item["marginAvailable"],
                update_time=int(item["updateTime"])
            )

# 示例 JSON 数据
# json_data = '''
# [
#     {
#         "accountAlias": "SgsR",
#         "asset": "USDT",
#         "balance": "122607.35137903",
#         "crossWalletBalance": "23.72469206",
#         "crossUnPnl": "0.00000000",
#         "availableBalance": "23.72469206",
#         "maxWithdrawAmount": "23.72469206",
#         "marginAvailable": true,
#         "updateTime": 1617939110373
#     }
# ]
# '''
#
# # 解析 JSON 数据
# account_balance_ustd = parse_account_balance(json_data)
# print(account_balance_ustd)
