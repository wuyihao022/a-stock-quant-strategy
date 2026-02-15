"""回测入口脚本。"""

from __future__ import annotations

import backtrader as bt

from data.data_loader import AShareDataLoader
from strategy.base import StrategyBase


class DemoSupertrendStrategy(StrategyBase):
    """示例策略：仅作为框架占位。"""

    def next(self):
        if self.order:
            return

        # TODO: 替换为真实 Supertrend 信号逻辑
        if not self.position and self.data.close[0] > self.data.close[-1]:
            size = self.calculate_position_size(self.data.close[0], self.broker.getcash())
            if size > 0:
                self.order = self.buy(size=size)
        elif self.position and self.data.close[0] < self.data.close[-1]:
            self.order = self.close()


def run(symbol: str = "600519", cash: float = 1_000_000):
    loader = AShareDataLoader()
    raw = loader.get_daily_bars(symbol=symbol, start="20200101")

    data = raw[["date", "open", "high", "low", "close", "volume"]].copy()
    data = data.set_index("date")

    feed = bt.feeds.PandasData(dataname=data)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(DemoSupertrendStrategy)
    cerebro.adddata(feed)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)

    print(f"初始资金: {cerebro.broker.getvalue():,.2f}")
    cerebro.run()
    print(f"结束资金: {cerebro.broker.getvalue():,.2f}")

    # 可视化（可按需关闭）
    cerebro.plot(style="candlestick")


if __name__ == "__main__":
    run()
