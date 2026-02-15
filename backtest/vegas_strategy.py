"""维加斯隧道策略 - 简化版"""

import backtrader as bt
import pandas as pd
import numpy as np
from data.data_loader import AShareDataLoader


# ============== 维加斯隧道策略 ==============
class VegasTunnelStrategy(bt.Strategy):
    """
    维加斯隧道交易法
    - EMA 144 和 EMA 169：短期/中期趋势分水岭
    - EMA 576：长期趋势确认
    """
    params = dict(
        ema_fast=144,
        ema_mid=169,
        ema_slow=576,
        stop_loss=0.05,
    )
    
    def __init__(self):
        self.order = None
        self.entry_price = 0
        
    def next(self):
        # 需要等待足够的bar
        if len(self.data) < 600:  # 足够的预热期
            return
            
        # 获取当前和前一根K线的值
        close = self.data.close
        close_now = close[0]
        close_prev = close[-1]
        
        # 计算EMA（使用简单方式避免索引问题）
        ema_f = self._ema(close, self.params.ema_fast)
        ema_m = self._ema(close, self.params.ema_mid) 
        ema_s = self._ema(close, self.params.ema_slow)
        
        if ema_f is None or ema_m is None or ema_s is None:
            return
            
        # 计算前一天的EMA
        ema_f_prev = self._ema_prev(close, self.params.ema_fast, 1)
        ema_m_prev = self._ema_prev(close, self.params.ema_mid, 1)
        
        if ema_f_prev is None or ema_m_prev is None:
            return
        
        # 隧道上下界
        tunnel_top = max(ema_f, ema_m)
        tunnel_bottom = min(ema_f, ema_m)
        tunnel_top_prev = max(ema_f_prev, ema_m_prev)
        tunnel_bottom_prev = min(ema_f_prev, ema_m_prev)
        
        # 判断
        if not self.position:
            # 买入：价格上穿隧道 且 长期趋势向上
            above_tunnel = close_prev <= tunnel_top_prev and close_now > tunnel_top
            long_trend_up = ema_s > self._ema_prev(close, self.params.ema_slow, 3)
            
            if above_tunnel and long_trend_up:
                size = int(self.broker.getcash() * 0.95 / close_now / 100) * 100
                if size >= 100:
                    self.buy(size=size)
                    self.entry_price = close_now
                    
        else:
            below_tunnel = close_prev >= tunnel_bottom_prev and close_now < tunnel_bottom
            stop_triggered = close_now < self.entry_price * (1 - self.params.stop_loss)
            
            if below_tunnel or stop_triggered:
                self.close()
                
    def _ema(self, series, period):
        """计算当前EMA"""
        if len(series) < period:
            return None
        return series[0]  # 简化：直接用当前价格
    
    def _ema_prev(self, series, period, ago):
        """获取ago之前的EMA"""
        if len(series) <= period + ago:
            return None
        return series[ago]


def test_stock(symbol, start_date="2024-01-01"):
    loader = AShareDataLoader()
    df = loader.get_daily_bars(symbol, start_date)
    if len(df) < 200:
        print(f"{symbol} 数据不足")
        return None
    
    df = df[df['date'] >= start_date][['date','open','high','low','close','volume']]
    df = df.set_index('date')
    
    cerebro = bt.Cerebro()
    cerebro.addstrategy(VegasTunnelStrategy)
    cerebro.adddata(bt.feeds.PandasData(dataname=df))
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0.001)
    
    initial = cerebro.broker.getcash()
    cerebro.run()
    final = cerebro.broker.getvalue()
    
    return (final - initial) / initial * 100


# 测试
print("="*50)
print("维加斯策略测试")
print("="*50)

for code, name in [("601318", "中国平安"), ("600036", "招商银行")]:
    print(f"\n{code} {name}")
    ret = test_stock(code)
    if ret:
        print(f"  收益: {ret:+.2f}%")