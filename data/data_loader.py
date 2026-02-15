"""AkShare 数据加载模块 - 简化版"""

from __future__ import annotations
from datetime import datetime

import akshare as ak
import pandas as pd


# 测试用的大盘股列表
TEST_STOCKS = [
    ("600519", "贵州茅台"),
    ("600036", "招商银行"),
    ("601318", "中国平安"),
    ("600900", "长江电力"),
    ("601166", "兴业银行"),
    ("601398", "工商银行"),
    ("600030", "中信证券"),
    ("000858", "五粮液"),
    ("000333", "美的集团"),
    ("002594", "比亚迪"),
]


class AShareDataLoader:
    """A股数据加载器"""

    def __init__(self):
        self.cache = {}

    def get_daily_bars(self, symbol: str, start: str = "20200101", end: str = None) -> pd.DataFrame:
        """获取单只股票日线数据"""
        # 转换symbol格式：600519 -> 1.600519 (上海) 或 0.000001 (深圳)
        if symbol.startswith("6"):
            ak_symbol = f"1.{symbol}"
        else:
            ak_symbol = f"0.{symbol}"

        end = end or datetime.now().strftime("%Y%m%d")

        try:
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                   start_date=start, end_date=end, adjust="qfq")
            
            # 标准化字段
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
        except Exception as e:
            print(f"获取 {symbol} 数据失败: {e}")
            return pd.DataFrame()

    def load_factor_universe(self) -> pd.DataFrame:
        """
        加载选股因子数据库
        使用简化版：基于已知的大盘股
        """
        result = []
        
        for code, name in TEST_STOCKS:
            # 尝试获取实时数据
            try:
                df = ak.stock_individual_info_em(symbol=code)
                
                # 提取关键指标
                info = {"symbol": code, "name": name}
                
                for _, row in df.iterrows():
                    item = row.get("item", "")
                    value = row.get("value", 0)
                    
                    if "总市值" in item:
                        # 处理市值数据，如 "2.10万亿" -> 210000000000
                        if "万亿" in str(value):
                            info["market_cap"] = float(str(value).replace("万亿", "")) * 1e12
                        elif "亿" in str(value):
                            info["market_cap"] = float(str(value).replace("亿", "")) * 1e8
                        else:
                            info["market_cap"] = float(value) if value else 0
                    elif "市盈率" in item:
                        info["pe"] = float(value) if value and value != "--" else 0
                    elif "股息" in item and "率" in item:
                        info["dividend_yield"] = float(value.replace("%", ""))/100 if value and value != "--" else 0
                    elif "净资产收益率" in item or "ROE" in item:
                        info["roe"] = float(value.replace("%", "")) if value and value != "--" else 0
                
                # 如果没有获取到数据，给默认值
                if "market_cap" not in info:
                    info["market_cap"] = 1e11  # 假设1000亿
                if "pe" not in info:
                    info["pe"] = 15
                if "dividend_yield" not in info:
                    info["dividend_yield"] = 0.02
                if "roe" not in info:
                    info["roe"] = 15
                    
                result.append(info)
            except Exception as e:
                # 如果获取失败，使用默认值
                result.append({
                    "symbol": code,
                    "name": name,
                    "market_cap": 1e11,
                    "pe": 15,
                    "dividend_yield": 0.02,
                    "roe": 15
                })
        
        df = pd.DataFrame(result)
        return df


def get_stock_name(symbol: str) -> str:
    """获取股票名称"""
    for code, name in TEST_STOCKS:
        if code == symbol:
            return name
    return symbol