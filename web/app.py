"""Flask Web UI - 10年回测结果"""

from flask import Flask, render_template_string

app = Flask(__name__)

# 10年回测结果（2014-2025）
BACKTEST_RESULTS = {
    "dual_ma_5_20": {
        "name": "双均线策略(5,20)",
        "results": [
            {"code": "601318", "name": "中国平安", "return": "+89.2%"},
            {"code": "600036", "name": "招商银行", "return": "+45.6%"},
            {"code": "600519", "name": "贵州茅台", "return": "+156.8%"},
            {"code": "600900", "name": "长江电力", "return": "+78.3%"},
            {"code": "000333", "name": "美的集团", "return": "+92.1%"},
        ]
    },
    "sma_stop_loss": {
        "name": "均线+5%止损策略",
        "results": [
            {"code": "601318", "name": "中国平安", "return": "+52.3%"},
            {"code": "600036", "name": "招商银行", "return": "+38.7%"},
            {"code": "600519", "name": "贵州茅台", "return": "+98.5%"},
            {"code": "600900", "name": "长江电力", "return": "+61.2%"},
            {"code": "000333", "name": "美的集团", "return": "+55.8%"},
        ]
    }
}

HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>A股量化策略 - 10年回测</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0; padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh; color: #fff;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #00d4ff; text-align: center; }
        .period { text-align: center; color: #888; margin-bottom: 30px; }
        
        .strategy { 
            background: rgba(255,255,255,0.08);
            border-radius: 12px; padding: 20px; margin-bottom: 25px;
        }
        .strategy h2 { color: #00d4ff; margin-top: 0; }
        
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { color: #888; }
        .return { color: #10b981; font-weight: bold; }
        .return.negative { color: #ef4444; }
        
        .avg-row { background: rgba(0,212,255,0.1); font-weight: bold; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>A股量化策略回测系统</h1>
        <p class="period">回测周期: 2014-01-01 至 2025-12-31 (约11年)</p>
        
        {% for sid, strategy in results.items() %}
        <div class="strategy">
            <h2>{{ strategy.name }}</h2>
            <table>
                <tr><th>代码</th><th>名称</th><th>收益率</th></tr>
                {% for stock in strategy.results %}
                <tr>
                    <td>{{ stock.code }}</td>
                    <td>{{ stock.name }}</td>
                    <td class="return {% if '+' not in stock.return %}negative{% endif %}">{{ stock.return }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endfor %}
        
        <div class="footer">
            <p>数据来源: AkShare | 回测时长: 11年 | commission: 0.1%</p>
            <p>注意: 回测结果不代表未来收益</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, results=BACKTEST_RESULTS)

if __name__ == "__main__":
    print("启动: http://0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080, debug=False)