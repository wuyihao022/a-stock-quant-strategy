"""选股器：大市值、低 PE、高股息、ROE > 10%。"""

from __future__ import annotations

import pandas as pd


class FundamentalSelector:
    """基础面选股框架。"""

    def __init__(
        self,
        min_market_cap: float = 5e10,
        max_pe: float = 20.0,
        min_dividend_yield: float = 0.02,
        min_roe: float = 10.0,
    ):
        self.min_market_cap = min_market_cap
        self.max_pe = max_pe
        self.min_dividend_yield = min_dividend_yield
        self.min_roe = min_roe

    def select(self, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """
        输入应至少包含：
        - symbol
        - name
        - market_cap
        - pe
        - dividend_yield
        - roe
        """
        required = {"symbol", "name", "market_cap", "pe", "dividend_yield", "roe"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"缺少必要字段: {missing}")

        candidates = df[
            (df["market_cap"] >= self.min_market_cap)
            & (df["pe"] > 0)
            & (df["pe"] <= self.max_pe)
            & (df["dividend_yield"] >= self.min_dividend_yield)
            & (df["roe"] >= self.min_roe)
        ].copy()

        # 简单排序框架：PE 越低越好，股息/ROE 越高越好
        candidates["score"] = (
            (1 / candidates["pe"]).rank(pct=True)
            + candidates["dividend_yield"].rank(pct=True)
            + candidates["roe"].rank(pct=True)
        )
        return candidates.sort_values("score", ascending=False).head(top_n)


class SelectorService:
    """组合数据源与选股器的服务层。"""

    def __init__(self, data_loader, selector: FundamentalSelector | None = None):
        self.data_loader = data_loader
        self.selector = selector or FundamentalSelector()

    def get_recommendations(self, top_n: int = 20) -> pd.DataFrame:
        universe = self.data_loader.load_factor_universe()
        return self.selector.select(universe, top_n=top_n)
