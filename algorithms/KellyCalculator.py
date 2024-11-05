class KellyCalculator:
    """
        凯莉公式（赌徒算法）——计算投资比例

        Attributes:
        ----------
        win_rate : float
            胜率——获利概率
        win_ratio : float
            获胜时的赔率
            
        Methods:
        -------
        calculate_kelly_fraction():
            凯莉公式计算——计算交易比例
        calculate_optimal_bet_fraction(capital):
            计算最佳投资比例
        """

    def __init__(self, win_rate, win_ratio):
        self.win_rate = win_rate
        self.win_ratio = win_ratio

    def calculate_kelly_fraction(self):
        """
        计算凯利公式中的比例因子
        """
        p = self.win_rate
        q = 1 - p
        r = self.win_ratio
        kelly_fraction = (p * r - q) / r
        return kelly_fraction

    def calculate_optimal_bet_fraction(self, capital):
        """
        计算最优下注比例
        """
        kelly_fraction = self.calculate_kelly_fraction()
        optimal_bet_fraction = kelly_fraction * capital
        return optimal_bet_fraction


# 示例
if __name__ == "__main__":
    win_rate = 0.6  # 胜率
    win_ratio = 2.0  # 获胜时的赔率
    capital = 1000  # 资本
    calculator = KellyCalculator(win_rate, win_ratio)
    kelly_fraction = calculator.calculate_kelly_fraction()
    optimal_bet_fraction = calculator.calculate_optimal_bet_fraction(capital)
    print(f"凯利公式比例因子：{kelly_fraction:.2f}")
    print(f"最优下注比例：{optimal_bet_fraction:.2f}")
