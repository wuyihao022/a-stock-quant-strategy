"""
马丁策略 (Martingale Strategy) - 修正版
核心思想：亏损后加倍仓位，反弹时一次收回所有亏损
"""

import backtrader as bt


class MartingaleStrategy(bt.Strategy):
    """
    马丁格尔策略修正版
    
    参数:
        initial_pct: 初始买入资金比例 (默认10%)
        max_loss_rate: 单次亏损阈值 (默认-5%)
        take_profit_rate: 止盈比例 (默认+3%)
        max_layers: 最大加仓层数 (默认5层)
    """
    params = dict(
        initial_pct=0.1,         # 初始买入10%
        max_loss_rate=-0.05,     # 亏损5%触发加仓
        take_profit_rate=0.03,   # 盈利3%止盈
        max_layers=5,            # 最大加仓5层
    )

    def __init__(self):
        self.buy_price = 0       # 持仓成本价
        self.total_cost = 0      # 总投入成本
        self.layers = 0          # 当前层数
        self.pending_order = None
        self.total_trades = 0    # 交易次数
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Acpected]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.total_cost += order.executed.size * order.executed.price
                self.total_trades += 1
            self.pending_order = None

    def next(self):
        if self.pending_order:
            return
            
        close = self.data.close[0]
        if close <= 0:
            return
        
        # 计算当前持仓盈亏
        if self.position:
            current_pnl = (close - self.buy_price) / self.buy_price
        else:
            current_pnl = 0
        
        # 1. 检查止盈 - 盈利达到3%卖出全部
        if self.position and current_pnl >= self.params.take_profit_rate:
            self.pending_order = self.close()
            self.log(f'止盈卖出: 价格={close:.2f}, 盈利={current_pnl*100:.1f}%')
            self.buy_price = 0
            self.layers = 0
            self.total_cost = 0
            return
        
        # 2. 检查加仓 - 亏损达到5%且未达到最大层数
        if self.position and current_pnl < self.params.max_loss_rate:
            if self.layers < self.params.max_layers:
                # 计算可用资金
                total_value = self.broker.getvalue()
                position_value = self.position.size * close
                available_cash = total_value - position_value
                
                # 加仓量 = 当前持仓量的2倍
                new_size = self.position.size
                
                # 检查资金是否足够
                cost = new_size * close
                if cost < available_cash * 0.95:  # 留5%缓冲
                    self.pending_order = self.buy(size=new_size)
                    # 更新均价（加权平均）
                    total_shares = self.position.size + new_size
                    self.buy_price = (self.buy_price * self.position.size + close * new_size) / total_shares
                    self.layers += 1
                    self.log(f'加仓{self.layers}层: 价格={close:.2f}, 数量={new_size}, 盈亏={current_pnl*100:.1f}%')
            else:
                # 超过最大层数，止损
                self.pending_order = self.close()
                self.log(f'达到最大层数{self.layers}层，止损: 价格={close:.2f}')
                self.buy_price = 0
                self.layers = 0
                self.total_cost = 0
            return
        
        # 3. 初始建仓 - 买入10%
        if not self.position and self.layers == 0:
            cash = self.broker.getcash()
            size = int(cash * self.params.initial_pct / close / 100) * 100
            if size >= 100:
                self.pending_order = self.buy(size=size)
                self.buy_price = close
                self.total_cost = size * close
                self.layers = 1
                self.log(f'初始建仓: 价格={close:.2f}, 数量={size}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(f'{dt.isoformat()} {txt}')


class MartingaleConservative(bt.Strategy):
    """
    保守版马丁策略 - 每次加仓固定比例
    """
    params = dict(
        initial_pct=0.2,         # 初始买入20%
        add_pct=0.2,             # 每次加仓20%
        stop_loss=-0.10,         # 亏损10%止损
        take_profit=0.05,        # 盈利5%止盈
    )
    
    def __init__(self):
        self.buy_price = 0
        self.layers = 0
        self.pending_order = None
        
    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.pending_order = None
            
    def next(self):
        if self.pending_order:
            return
            
        close = self.data.close[0]
        if close <= 0 or not self.position:
            return
            
        pnl = (close - self.buy_price) / self.buy_price
        
        # 止盈
        if pnl >= self.params.take_profit:
            self.pending_order = self.close()
            self.buy_price = 0
            self.layers = 0
            self.log(f'止盈 {pnl*100:.1f}%')
            return
            
        # 止损/加仓
        if pnl < self.params.stop_loss:
            # 加仓
            if self.layers < 3:
                cash = self.broker.getcash()
                size = int(cash * self.params.add_pct / close / 100) * 100
                if size >= 100:
                    self.pending_order = self.buy(size=size)
                    total = self.position.size + size
                    self.buy_price = (self.buy_price * self.position.size + close * size) / total
                    self.layers += 1
            else:
                # 止损
                self.pending_order = self.close()
                self.buy_price = 0
                self.layers = 0

    def log(self, txt, dt=None):
        pass


if __name__ == "__main__":
    # 测试
    import sys
    sys.path.insert(0, '.')
    from data.data_loader import AShareDataLoader
    
    loader = AShareDataLoader()
    df = loader.get_daily_bars("600519", "2024-01-01")
    
    if df is not None and len(df) > 100:
        df = df[df['close'] > 0][['date','open','high','low','close','volume']]
        df = df.set_index('date')
        
        cerebro = bt.Cerebro()
        cerebro.addstrategy(MartingaleStrategy)
        cerebro.adddata(bt.feeds.PandasData(dataname=df))
        cerebro.broker.setcash(1000000)
        cerebro.broker.setcommission(commission=0.001)
        
        initial = cerebro.broker.getcash()
        cerebro.run()
        final = cerebro.broker.getvalue()
        
        print(f"初始: {initial:,.0f}")
        print(f"最终: {final:,.0f}")
        print(f"收益: {(final-initial)/initial*100:+.1f}%")
    else:
        print("数据获取失败")