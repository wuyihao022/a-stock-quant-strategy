"""基础策略模块：包含策略基类与 Supertrend 指标计算。"""

from __future__ import annotations

from dataclasses import dataclass

import backtrader as bt
import numpy as np
import pandas as pd


@dataclass
class SupertrendConfig:
    """Supertrend 参数配置。"""

    atr_period: int = 10
    multiplier: float = 3.0


class StrategyBase(bt.Strategy):
    """Backtrader 策略基类，预留通用风控与交易钩子。"""

    params = dict(
        atr_period=10,
        atr_multiplier=3.0,
        risk_per_trade=0.02,
    )

    def __init__(self):
        self.order = None

    def notify_order(self, order):
        """订单状态回调（框架占位）。"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None

    def calculate_position_size(self, price: float, cash: float) -> int:
        """按固定风险比例计算仓位（简单示例）。"""
        if price <= 0:
            return 0
        budget = cash * self.params.risk_per_trade
        return max(int(budget // price), 0)


class SupertrendCalculator:
    """使用 Pandas 计算 Supertrend（可用于离线选股/信号预计算）。"""

    @staticmethod
    def calculate(df: pd.DataFrame, config: SupertrendConfig | None = None) -> pd.DataFrame:
        """
        计算 Supertrend。

        期望输入列：high, low, close
        输出新增列：atr, supertrend, trend(1/-1)
        """
        config = config or SupertrendConfig()
        data = df.copy()

        hl = data["high"] - data["low"]
        hc = (data["high"] - data["close"].shift(1)).abs()
        lc = (data["low"] - data["close"].shift(1)).abs()
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        data["atr"] = tr.rolling(config.atr_period).mean()

        mid = (data["high"] + data["low"]) / 2
        upper = mid + config.multiplier * data["atr"]
        lower = mid - config.multiplier * data["atr"]

        trend = np.ones(len(data), dtype=int)
        supertrend = np.full(len(data), np.nan)

        for i in range(1, len(data)):
            if data["close"].iloc[i] > upper.iloc[i - 1]:
                trend[i] = 1
            elif data["close"].iloc[i] < lower.iloc[i - 1]:
                trend[i] = -1
            else:
                trend[i] = trend[i - 1]
                if trend[i] == 1:
                    lower.iloc[i] = max(lower.iloc[i], lower.iloc[i - 1])
                else:
                    upper.iloc[i] = min(upper.iloc[i], upper.iloc[i - 1])

            supertrend[i] = lower.iloc[i] if trend[i] == 1 else upper.iloc[i]

        data["supertrend"] = supertrend
        data["trend"] = trend
        return data
