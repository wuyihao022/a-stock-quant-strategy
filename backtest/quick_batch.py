"""沪深300快速回测 - 使用tushare Pro"""
import tushare as ts
import pandas as pd
import csv

# Tushare token (需要设置)
token = None

def get_hs300_akshare():
    """用akshare获取沪深300"""
    try:
        import akshare as ak
        # 尝试获取
        df = ak.stock_hs300_stocks_sina()
        return df
    except Exception as e:
        print(f"akshare获取失败: {e}")
        return None

def get_hs300_from_file():
    """从文件读取"""
    stocks = []
    try:
        with open('data/hs300_stocks.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stocks.append((row['code'], row['name']))
    except:
        pass
    return stocks

def quick_backtest_martingale(prices):
    """快速回测马丁策略（无backtrader）
    
    策略：初始10%仓位，每下跌5%加仓一倍，达到+3%止盈
    """
    if len(prices) < 50:
        return None
    
    cash = 1000000
    position = 0
    entry_price = 0
    layers = 0
    max_layers = 5
    
    for i, price in enumerate(prices):
        # 初始建仓
        if position == 0 and i > 20:  # 跳过前20天
            shares = int(cash * 0.1 / price / 100) * 100
            if shares >= 100:
                position = shares
                entry_price = price
                cash -= shares * price
                layers = 1
        
        # 持仓中
        elif position > 0:
            pnl = (price - entry_price) / entry_price
            
            # 止盈
            if pnl >= 0.03:
                cash += position * price
                position = 0
                entry_price = 0
                layers = 0
            
            # 加仓（马丁）
            elif pnl < -0.05 and layers < max_layers:
                # 加仓数量翻倍
                new_shares = position
                cost = new_shares * price
                if cost < cash * 0.9:
                    # 更新均价
                    total = position + new_shares
                    entry_price = (entry_price * position + price * new_shares) / total
                    position = total
                    cash -= new_shares * price
                    layers += 1
            
            # 超过最大层数止损
            elif pnl < -0.15:  # 累计亏损15%强制止损
                cash += position * price
                position = 0
                entry_price = 0
                layers = 0
    
    # 最终结算
    if position > 0:
        cash += position * prices[-1]
    
    return (cash - 1000000) / 1000000 * 100


def get_stock_data(symbol, days=250):
    """快速获取股票数据"""
    try:
        df = ts.pro_bar(ts_code=f"{symbol}.SH" if symbol.startswith('6') else f"{symbol}.SZ", 
                       asset='E', start_date='20250101', end_date='20260216')
        if df is not None and len(df) > 50:
            return df['close'].tolist()
    except Exception as e:
        pass
    return None


def main():
    # 尝试获取tushare token
    global token
    try:
        token = open('.token').read().strip() if open('.token').read().strip() else None
    except:
        pass
    
    if token:
        ts.set_token(token)
        pro = ts.pro_api()
    else:
        print("未设置tushare token，尝试akshare...")
        # 使用本地股票列表
        stocks = get_hs300_from_file()
        if not stocks:
            print("使用默认股票列表")
            stocks = [
                ("600519", "贵州茅台"),
                ("600036", "招商银行"),
                ("601318", "中国平安"),
                ("600900", "长江电力"),
                ("000333", "美的集团"),
            ]
        
        print(f"共{len(stocks)}只股票，开始回测...")
        
        results = []
        for i, (code, name) in enumerate(stocks, 1):
            print(f"[{i}/{len(stocks)}] {code} {name}...", end=" ", flush=True)
            prices = get_stock_data(code)
            if prices:
                ret = quick_backtest_martingale(prices)
                if ret is not None:
                    results.append((code, name, ret))
                    print(f"{ret:+.1f}%")
                else:
                    print("数据不足")
            else:
                print("获取失败")
        
        if results:
            results.sort(key=lambda x: x[2], reverse=True)
            print("\n=== 马丁策略收益排名 ===")
            for i, (code, name, ret) in enumerate(results[:15], 1):
                print(f"{i}. {code} {name}: {ret:+.1f}%")
            
            avg = sum(r[2] for r in results) / len(results)
            wins = sum(1 for r in results if r[2] > 0)
            print(f"\n平均: {avg:+.1f}% 正收益: {wins}/{len(results)}")


if __name__ == "__main__":
    main()