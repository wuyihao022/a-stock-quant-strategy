"""最终优化版回测 - 多参数测试"""

import backtrader as bt
import pandas as pd
from data.data_loader import AShareDataLoader
from itertools import product

# 沪深300核心股票
HS300_CORE = [
    ("600519", "贵州茅台"),
    ("600036", "招商银行"),
    ("601318", "中国平安"),
    ("600900", "长江电力"),
    ("601166", "兴业银行"),
    ("000333", "美的集团"),
    ("002594", "比亚迪"),
    ("601012", "隆基绿能"),
    ("600276", "恒瑞医药"),
    ("600887", "伊利股份"),
]

# ============ 优化后的双均线策略 ============
class OptimizedDualMA(bt.Strategy):
    """优化的双均线策略，只做多，金叉买死叉卖"""
    params = dict(fast=5, slow=20)
    
    def __init__(self):
        self.fast = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.fast)
        self.slow = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.slow)
        self.prev_cross = 0
        
    def next(self):
        curr_cross = 1 if self.fast[0] > self.slow[0] else -1
        
        # 金叉买入
        if curr_cross == 1 and self.prev_cross == -1:
            if not self.position:
                size = int(self.broker.getcash() * 0.95 / self.data.close[0] / 100) * 100
                if size >= 100:
                    self.buy(size=size)
                    
        # 死叉卖出
        elif curr_cross == -1 and self.prev_cross == 1:
            if self.position:
                self.close()
                
        self.prev_cross = curr_cross


# 优化参数组合
PARAM_COMBOS = [
    (5, 20),
    (10, 30),
    (10, 60),
    (20, 60),
    (5, 10),
]

def quick_backtest(symbol, fast, slow, start_date="2024-01-01"):
    """快速回测"""
    loader = AShareDataLoader()
    df = loader.get_daily_bars(symbol, start_date)
    if len(df) < 50:
        return None
        
    df = df[df['date'] >= start_date][['date','open','high','low','close','volume']]
    df = df.set_index('date')
    
    cerebro = bt.Cerebro()
    cerebro.addstrategy(OptimizedDualMA, fast=fast, slow=slow)
    cerebro.adddata(bt.feeds.PandasData(dataname=df))
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0.001)
    
    initial = cerebro.broker.getcash()
    cerebro.run()
    final = cerebro.broker.getvalue()
    
    return (final - initial) / initial * 100


print("="*60)
print("寻找最佳策略参数")
print("="*60)

best_params = {}
best_overall = None

# 测试不同参数
for fast, slow in PARAM_COMBOS:
    print(f"\n参数: fast={fast}, slow={slow}")
    total_return = 0
    count = 0
    
    for code, name in HS300_CORE:
        ret = quick_backtest(code, fast, slow)
        if ret is not None:
            total_return += ret
            count += 1
            print(f"  {code}: {ret:+.1f}%")
    
    if count > 0:
        avg_return = total_return / count
        print(f"  平均: {avg_return:+.1f}%")
        
        if best_overall is None or avg_return > best_overall:
            best_overall = avg_return
            best_params = {'fast': fast, 'slow': slow}

print("\n" + "="*60)
print(f"最佳参数: fast={best_params['fast']}, slow={best_params['slow']}")
print(f"平均收益率: {best_overall:+.1f}%")
print("="*60)