"""AkShare 数据加载模块。"""

from __future__ import annotations

from datetime import datetime

import akshare as ak
import pandas as pd


class AShareDataLoader:
    """A 股数据加载器（仅提供核心框架，细节待扩展）。"""

    def get_daily_bars(self, symbol: str, start: str = "20200101", end: str | None = None) -> pd.DataFrame:
        """获取单只股票日线数据。"""
        end = end or datetime.now().strftime("%Y%m%d")
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start, end_date=end, adjust="qfq")

        # 标准化字段，便于回测统一接入
        rename_map = {
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
        }
        df = df.rename(columns=rename_map)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
        return df

    def load_factor_universe(self) -> pd.DataFrame:
        """
        拉取用于选股的基础面字段。
        注：此处仅给出拼装框架，具体字段映射需按实际 AkShare 接口完善。
        """
        spot = ak.stock_zh_a_spot_em()

        result = pd.DataFrame()
        result["symbol"] = spot.get("代码", pd.Series(dtype=str))
        result["name"] = spot.get("名称", pd.Series(dtype=str))

        # 下列字段为占位映射，后续可替换为更准确的数据接口
        result["market_cap"] = pd.to_numeric(spot.get("总市值", 0), errors="coerce").fillna(0)
        result["pe"] = pd.to_numeric(spot.get("市盈率-动态", 0), errors="coerce").fillna(0)
        result["dividend_yield"] = pd.to_numeric(spot.get("股息率", 0), errors="coerce").fillna(0) / 100

        # ROE 通常需从财报接口拼接；先预留字段
        result["roe"] = 0.0

        return result
