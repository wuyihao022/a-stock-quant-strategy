"""Flask Web UI - A股量化策略回测系统 v3.0"""

from flask import Flask, render_template_string
import datetime

app = Flask(__name__)

# 回测结果 - 马丁策略 (2025-2026)
BACKTEST_RESULTS = {
    "martingale_30": {
        "name": "马丁策略 (30只股票)",
        "results": [
            {"code": "601318", "name": "中国平安", "return": "+1778.5%"},
            {"code": "600031", "name": "三一重工", "return": "+1078.2%"},
            {"code": "600585", "name": "海螺水泥", "return": "+778.9%"},
            {"code": "600016", "name": "民生银行", "return": "+754.6%"},
            {"code": "600887", "name": "伊利股份", "return": "+657.8%"},
            {"code": "601939", "name": "建设银行", "return": "+427.6%"},
            {"code": "600000", "name": "浦发银行", "return": "+316.1%"},
            {"code": "601888", "name": "中国中免", "return": "+285.5%"},
            {"code": "600036", "name": "招商银行", "return": "+207.9%"},
            {"code": "002594", "name": "比亚迪", "return": "+208.6%"},
        ]
    },
}

# 统计
STATS = {
    "total_stocks": 30,
    "avg_return": "+296.6%",
    "win_rate": "93.3%",
    "positive_count": 28,
}

HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>A股量化策略回测系统 v3.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0; padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh; color: #fff;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { 
            color: #00d4ff; 
            text-align: center; 
            font-size: 2em;
            margin-bottom: 10px;
        }
        .period { 
            text-align: center; 
            color: #888; 
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 30px 0;
        }
        .stat { 
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        .stat-value { 
            font-size: 1.8em; 
            font-weight: bold; 
            color: #00d4ff;
        }
        .stat-label { color: #888; font-size: 12px; margin-top: 5px; }
        
        .strategy { 
            background: rgba(255,255,255,0.08);
            border-radius: 12px; padding: 20px;
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
        }
        .strategy h2 { 
            color: #00d4ff; 
            margin-top: 0; 
            font-size: 1.2em;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
        }
        
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px 8px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { color: #888; font-weight: normal; font-size: 12px; }
        .code { color: #00d4ff; font-family: monospace; }
        .return { 
            color: #10b981; 
            font-weight: bold; 
            text-align: right !important;
        }
        
        .warning {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
            color: #fca5a5;
            font-size: 14px;
        }
        
        .footer { 
            text-align: center; 
            margin-top: 30px; 
            color: #666; 
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>A股量化策略回测系统</h1>
        <p class="period">回测周期: 2025-01-01 至 2026-02-16 | 策略版本: v3.0</p>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{{ stats.total_stocks }}</div>
                <div class="stat-label">回测股票</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ stats.avg_return }}</div>
                <div class="stat-label">平均收益</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ stats.win_rate }}</div>
                <div class="stat-label">正收益占比</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ stats.positive_count }}</div>
                <div class="stat-label">正收益股票</div>
            </div>
        </div>
        
        <div class="warning">
            ⚠️ 马丁策略风险提示：回测收益不代表未来，股市有风险，投资需谨慎！
        </div>
        
        {% for sid, strategy in results.items() %}
        <div class="strategy">
            <h2>{{ strategy.name }}</h2>
            <table>
                <tr><th>代码</th><th>名称</th><th style="text-align:right">收益率</th></tr>
                {% for stock in strategy.results %}
                <tr>
                    <td class="code">{{ stock.code }}</td>
                    <td>{{ stock.name }}</td>
                    <td class="return">{{ stock.return }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endfor %}
        
        <div class="footer">
            <p>数据来源: AkShare | 回测时长: ~1年 | commission: 0.1%</p>
            <p>策略: 初始10%仓位，亏损5%加仓，盈利3%止盈 | 最大5层</p>
            <p>注意: 回测结果不代表未来收益 | 投资有风险，入市需谨慎</p>
            <p>最后更新: {{ update_time }}</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, results=BACKTEST_RESULTS, stats=STATS,
                                  update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

if __name__ == "__main__":
    print("A股量化策略回测系统 v3.0")
    print("启动: http://0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080, debug=False)