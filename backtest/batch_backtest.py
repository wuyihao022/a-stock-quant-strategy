"""沪深300批量回测"""
import backtrader as bt
import pandas as pd
import csv
from data.data_loader import AShareDataLoader

# 策略
from strategy.martingale import MartingaleStrategy, MartingaleV2Strategy


class DualMAStrategy(bt.Strategy):
    params = dict(fast=5, slow=20)
    
    def __init__(self):
        self.fast = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.fast)
        self.slow = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.slow)
        
    def next(self):
        if len(self.data) < self.params.slow + 5:
            return
            
        fast_now = self.fast[0]
        slow_now = self.slow[0]
        fast_prev = self.fast[-1]
        slow_prev = self.slow[-1]
        
        if fast_now > slow_now and fast_prev <= slow_prev:
            if not self.position:
                price = self.data.close[0]
                if price > 0:
                    size = int(self.broker.getcash() * 0.95 / price / 100) * 100
                    if size >= 100:
                        self.buy(size=size)
                    
        elif fast_now < slow_now and fast_prev >= slow_prev:
            if self.position:
                self.close()


def run_backtest(code, name, strategy_class, params=None, start_date="2023-01-01"):
    """运行单个股票回测"""
    loader = AShareDataLoader()
    df = loader.get_daily_bars(code, start_date)
    
    if df is None or len(df) < 100:
        return None
    
    df = df[df['date'] >= start_date][['date','open','high','low','close','volume']]
    if len(df) < 100:
        return None
        
    df = df.set_index('date')
    
    cerebro = bt.Cerebro()
    if params:
        cerebro.addstrategy(strategy_class, **params)
    else:
        cerebro.addstrategy(strategy_class)
    
    cerebro.adddata(bt.feeds.PandasData(dataname=df))
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0.001)
    
    initial = cerebro.broker.getcash()
    cerebro.run()
    final = cerebro.broker.getvalue()
    
    return (final - initial) / initial * 100


def load_hs300_stocks():
    """加载沪深300股票列表"""
    stocks = []
    try:
        with open('data/hs300_stocks.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stocks.append((row['code'], row['name']))
    except FileNotFoundError:
        print("未找到hs300_stocks.csv，使用默认股票列表")
        stocks = [
            ("600519", "贵州茅台"),
            ("600036", "招商银行"),
            ("601318", "中国平安"),
            ("600900", "长江电力"),
            ("000333", "美的集团"),
        ]
    return stocks


def main():
    print("="*60)
    print("沪深300批量回测")
    print("="*60)
    
    stocks = load_hs300_stocks()
    print(f"共{len(stocks)}只股票\n")
    
    results = {
        'dual_ma': [],
        'martingale': [],
    }
    
    # 回测双均线策略
    print("--- 双均线策略(5,20) ---")
    for i, (code, name) in enumerate(stocks[:50], 1):
        print(f"[{i}/{len(stocks[:50])}] {code} {name}...", end=" ")
        ret = run_backtest(code, name, DualMAStrategy)
        if ret is not None:
            results['dual_ma'].append((code, name, ret))
            print(f"{ret:+.1f}%")
        else:
            print("数据不足")
    
    print(f"\n完成双均线策略: {len(results['dual_ma'])}只")
    
    # 回测马丁策略
    print("\n--- 马丁策略 ---")
    for i, (code, name) in enumerate(stocks[:50], 1):
        print(f"[{i}/{len(stocks[:50])}] {code} {name}...", end=" ")
        ret = run_backtest(code, name, MartingaleStrategy)
        if ret is not None:
            results['martingale'].append((code, name, ret))
            print(f"{ret:+.1f}%")
        else:
            print("数据不足")
    
    print(f"\n完成马丁策略: {len(results['martingale'])}只")
    
    # 输出排名
    print("\n" + "="*60)
    print("收益排名")
    print("="*60)
    
    print("\n双均线策略 Top 10:")
    results['dual_ma'].sort(key=lambda x: x[2], reverse=True)
    for i, (code, name, ret) in enumerate(results['dual_ma'][:10], 1):
        print(f"  {i}. {code} {name}: {ret:+.1f}%")
    
    print("\n马丁策略 Top 10:")
    results['martingale'].sort(key=lambda x: x[2], reverse=True)
    for i, (code, name, ret) in enumerate(results['martingale'][:10], 1):
        print(f"  {i}. {code} {name}: {ret:+.1f}%")
    
    # 统计
    if results['dual_ma']:
        avg = sum(r[2] for r in results['dual_ma']) / len(results['dual_ma'])
        wins = sum(1 for r in results['dual_ma'] if r[2] > 0)
        print(f"\n双均线 平均: {avg:+.1f}% 正收益: {wins}/{len(results['dual_ma'])}")
    
    if results['martingale']:
        avg = sum(r[2] for r in results['martingale']) / len(results['martingale'])
        wins = sum(1 for r in results['martingale'] if r[2] > 0)
        print(f"马丁 平均: {avg:+.1f}% 正收益: {wins}/{len(results['martingale'])}")
    
    return results


if __name__ == "__main__":
    main()