"""双均线 + 马丁策略结合"""

import backtrader as bt


class DualMAWithMartingale(bt.Strategy):
    """
    双均线 + 马丁策略结合
    
    买入逻辑：双均线金叉（5日均线上穿20日均线）
    加仓逻辑：亏损5%时加仓（马丁）
    止盈：盈利3%全部卖出
    止损：亏损15%或达到最大层数5层强制止损
    """
    params = dict(
        fast_period=5,      # 短期均线周期
        slow_period=20,     # 长期均线周期
        martingale_layers=5,
        martingale_loss=-0.05,   # 亏损5%触发加仓
        martingale_profit=0.03,  # 盈利3%止盈
        stop_loss=-0.15,    # 止损线 -15%
    )
    
    def __init__(self):
        # 双均线
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period)
        
        # 马丁策略参数
        self.avg_price = 0      # 平均持仓成本
        self.layers = 0         # 当前加仓层数
        self.order = None       # 待处理订单
        self.prev_cross = 0     # 记录之前的均线状态
        
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.avg_price = order.executed.price
                self.layers += 1
        self.order = None
        
    def next(self):
        if self.order:
            return
            
        close = self.data.close[0]
        if close <= 0:
            return
        
        # 计算当前持仓盈亏
        if self.position and self.avg_price > 0:
            current_pnl = (close - self.avg_price) / self.avg_price
        else:
            current_pnl = 0
        
        # === 卖出条件 ===
        
        # 1. 止盈：盈利达到3%
        if self.position and current_pnl >= self.params.martingale_profit:
            self.order = self.close()
            self.avg_price = 0
            self.layers = 0
            return
            
        # 2. 止损：亏损达到15%或超过最大层数
        if self.position and (current_pnl < self.params.stop_loss or self.layers > self.params.martingale_layers):
            self.order = self.close()
            self.avg_price = 0
            self.layers = 0
            return
            
        # 3. 死叉卖出
        if self.position and self.prev_cross > 0:
            if self.fast_ma[0] <= self.slow_ma[0]:
                self.order = self.close()
                self.avg_price = 0
                self.layers = 0
                self.prev_cross = 0
                return
        
        # === 买入/加仓条件 ===
        
        # 没有持仓时，金叉买入
        if not self.position:
            if len(self) < self.params.slow_period + 5:
                return
                
            if self.fast_ma[0] > self.slow_ma[0] and self.fast_ma[-1] <= self.slow_ma[-1]:
                # 金叉 - 首次买入
                size = int(self.broker.getcash() * 0.9 / close / 100) * 100
                if size >= 100:
                    self.order = self.buy(size=size)
                    self.avg_price = close
                    self.layers = 1
                    self.prev_cross = 1
            return
            
        # 有持仓时，马丁加仓
        if self.position and current_pnl < self.params.martingale_loss:
            if self.layers < self.params.martingale_layers:
                # 检查资金是否足够加仓
                available = self.broker.getcash()
                new_size = self.position.size  # 翻倍加仓
                cost = new_size * close
                
                if cost < available * 0.9:
                    self.order = self.buy(size=new_size)
                    # 更新均价
                    total = self.position.size + new_size
                    self.avg_price = (self.avg_price * self.position.size + close * new_size) / total
                    self.layers += 1


class DualMAWithPyramid(bt.Strategy):
    """
    双均线 + 金字塔加仓策略
    
    买入逻辑：双均线金叉
    加仓逻辑：每次加仓固定比例(20%)，最多加仓3次
    止盈：20%收益
    止损：10%亏损
    """
    params = dict(
        fast_period=5,
        slow_period=20,
        add_pct=0.2,         # 每次加仓20%
        max_adds=3,          # 最多加仓3次
        take_profit=0.20,    # 止盈20%
        stop_loss=-0.10,     # 止损10%
    )
    
    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period)
        
        self.avg_price = 0
        self.add_count = 0
        self.order = None
        self.entry_price = 0
        self.prev_cross = 0
        
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.avg_price = order.executed.price
                self.add_count += 1
        self.order = None
        
    def next(self):
        if self.order:
            return
            
        close = self.data.close[0]
        if close <= 0:
            return
        
        if self.position and self.avg_price > 0:
            pnl = (close - self.avg_price) / self.avg_price
        else:
            pnl = 0
        
        # === 卖出 ===
        
        # 止盈
        if self.position and pnl >= self.params.take_profit:
            self.order = self.close()
            self.avg_price = 0
            self.add_count = 0
            return
            
        # 止损
        if self.position and pnl < self.params.stop_loss:
            self.order = self.close()
            self.avg_price = 0
            self.add_count = 0
            return
            
        # 死叉
        if self.position and self.prev_cross > 0:
            if self.fast_ma[0] <= self.slow_ma[0]:
                self.order = self.close()
                self.avg_price = 0
                self.add_count = 0
                self.prev_cross = 0
                return
        
        # === 买入 ===
        
        if not self.position:
            if len(self) < self.params.slow_period + 5:
                return
                
            # 金叉买入
            if self.fast_ma[0] > self.slow_ma[0] and self.fast_ma[-1] <= self.slow_ma[-1]:
                size = int(self.broker.getcash() * 0.9 / close / 100) * 100
                if size >= 100:
                    self.order = self.buy(size=size)
                    self.avg_price = close
                    self.entry_price = close
                    self.add_count = 1
                    self.prev_cross = 1
            return
        
        # === 加仓 ===
        
        # 价格下跌5%且未超过最大加仓次数
        if self.position and pnl < -0.05 and self.add_count < self.params.max_adds:
            cash = self.broker.getcash()
            add_size = int(cash * self.params.add_pct / close / 100) * 100
            if add_size >= 100:
                self.order = self.buy(size=add_size)
                # 更新均价
                total = self.position.size + add_size
                self.avg_price = (self.avg_price * self.position.size + close * add_size) / total
                self.add_count += 1


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from data.data_loader import AShareDataLoader
    
    loader = AShareDataLoader()
    df = loader.get_backtrader_data("600519", "2007-01-01")
    
    if df is not None:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(DualMAWithMartingale)
        cerebro.adddata(bt.feeds.PandasData(dataname=df, datetime='date'))
        cerebro.broker.setcash(1000000)
        cerebro.broker.setcommission(commission=0.001)
        
        print("初始:", cerebro.broker.getcash())
        cerebro.run()
        print("最终:", cerebro.broker.getvalue())
    else:
        print("数据获取失败")