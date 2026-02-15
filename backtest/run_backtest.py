"""10年回测 - 修复版"""

import backtrader as bt
import pandas as pd
from data.data_loader import AShareDataLoader

# ============== 策略1: 双均线金叉死叉 ==============
class DualMAStrategy(bt.Strategy):
    params = dict(fast=5, slow=20)
    
    def __init__(self):
        self.fast = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.fast)
        self.slow = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.slow)
        self.prev_fast = 0
        
    def next(self):
        if len(self.data) < self.params.slow + 5:
            return
            
        fast_now = self.fast[0]
        slow_now = self.slow[0]
        fast_prev = self.fast[-1]
        slow_prev = self.slow[-1]
        
        # 金叉买入
        if fast_now > slow_now and fast_prev <= slow_prev:
            if not self.position:
                price = self.data.close[0]
                if price > 0:
                    size = int(self.broker.getcash() * 0.95 / price / 100) * 100
                    if size >= 100:
                        self.buy(size=size)
                    
        # 死叉卖出
        elif fast_now < slow_now and fast_prev >= slow_prev:
            if self.position:
                self.close()
                
        self.prev_fast = fast_now


# ============== 策略2: 突破20日均线 ==============
class BreakoutStrategy(bt.Strategy):
    params = dict(period=20)
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)
        
    def next(self):
        if len(self.data) < self.params.period + 5:
            return
            
        close = self.data.close[0]
        prev_close = self.data.close[-1]
        sma_now = self.sma[0]
        sma_prev = self.sma[-1]
        
        # 突破买入
        if prev_close <= sma_prev and close > sma_now:
            if not self.position:
                size = int(self.broker.getcash() * 0.95 / close / 100) * 100
                if size >= 100:
                    self.buy(size=size)
                    
        # 跌破卖出
        elif prev_close >= sma_prev and close < sma_now:
            if self.position:
                self.close()


def run_test(code, name, StrategyClass, params):
    loader = AShareDataLoader()
    df = loader.get_daily_bars(code, "2014-01-01")
    if df is None or len(df) < 500:
        return None
    
    df = df[df['date'] >= '2014-01-01'][['date','open','high','low','close','volume']]
    df = df.set_index('date')
    
    cerebro = bt.Cerebro()
    cerebro.addstrategy(StrategyClass, **params)
    cerebro.adddata(bt.feeds.PandasData(dataname=df))
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0.001)
    
    initial = cerebro.broker.getcash()
    cerebro.run()
    return (cerebro.broker.getvalue() - initial) / initial * 100


# 主程序
print("="*60)
print("10年回测 (2014-01-01 至今)")
print("="*60)

stocks = [
    ("601318", "中国平安"),
    ("600036", "招商银行"),
    ("600519", "贵州茅台"),
    ("600900", "长江电力"),
    ("000333", "美的集团"),
]

for code, name in stocks:
    print(f"\n{code} {name}")
    
    r1 = run_test(code, name, DualMAStrategy, {'fast': 5, 'slow': 20})
    r2 = run_test(code, name, BreakoutStrategy, {'period': 20})
    
    print(f"  双均线(5,20): {r1:+.1f}%")
    print(f"  突破20日均线: {r2:+.1f}%")