# A股量化交易策略

基于 AkShare 数据的 A 股量化交易策略，包含选股系统、回测框架和 Web UI。

## 策略逻辑

选股条件：
- 大市值（流通市值前 200）
- 低 PE（市盈率 < 20）
- 高股息（股息率 > 2%）
- ROE > 10%

择时：Supertrend 超级趋势指标

## 项目结构

```
a-stock-quant-strategy/
├── requirements.txt      # 依赖
├── strategy/
│   ├── base.py          # 基础策略类和 Supertrend 计算
│   └── selectors.py     # 选股器
├── data/
│   └── data_loader.py   # AkShare 数据加载
├── backtest/
│   └── run_backtest.py  # 回测脚本
└── web/
    └── app.py           # Flask Web UI
```

## 安装

```bash
pip install -r requirements.txt
```

## 使用

### 回测
```bash
python backtest/run_backtest.py
```

### Web UI
```bash
python web/app.py
```

然后访问 http://localhost:5000

## 数据来源

- AkShare（免费，无需 API Key）
- 东方财富网

## License

MIT
