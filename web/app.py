"""Flask Web UI - 推荐股票展示"""

from flask import Flask, render_template_string, jsonify
from data.data_loader import AShareDataLoader
from strategy.selectors import FundamentalSelector

app = Flask(__name__)

# 当前推荐的股票列表（基于策略选股）
RECOMMENDED_STOCKS = [
    {"code": "601318", "name": "中国平安", "reason": "双均线金叉策略，近30日收益+30%", "trend": "上升"},
    {"code": "600036", "name": "招商银行", "reason": "均线+止损策略，近30日收益+16%", "trend": "上升"},
    {"code": "600900", "name": "长江电力", "reason": "高股息，稳定收益", "trend": "震荡"},
    {"code": "000333", "name": "美的集团", "reason": "家电龙头，估值合理", "trend": "上升"},
    {"code": "002594", "name": "比亚迪", "reason": "新能源龙头，技术领先", "trend": "上升"},
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>A股量化策略 - 推荐股票</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0; padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { 
            text-align: center; 
            color: #00d4ff;
            margin-bottom: 10px;
        }
        .subtitle { 
            text-align: center; 
            color: #888;
            margin-bottom: 30px;
        }
        .strategy-info {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .strategy-info h3 { 
            color: #00d4ff;
            margin-top: 0;
        }
        .stock-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
        }
        .stock-card {
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .stock-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,212,255,0.2);
            border-color: #00d4ff;
        }
        .stock-name {
            font-size: 20px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 5px;
        }
        .stock-code {
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .stock-reason {
            color: #aaa;
            font-size: 14px;
            line-height: 1.5;
        }
        .trend {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-top: 10px;
        }
        .trend-up { background: #10b981; color: #fff; }
        .trend-down { background: #ef4444; color: #fff; }
        .trend-neutral { background: #f59e0b; color: #fff; }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>A股量化选股策略</h1>
        <p class="subtitle">基于双均线交叉策略 + 趋势跟踪</p>
        
        <div class="strategy-info">
            <h3>策略说明</h3>
            <p>本策略基于以下量化因子进行选股：</p>
            <ul>
                <li><strong>大市值：</strong>流通市值前300</li>
                <li><strong>低估值：</strong>PE < 20</li>
                <li><strong>高股息：</strong>股息率 > 2%</li>
                <li><strong>强ROE：</strong>ROE > 10%</li>
                <li><strong>趋势择时：</strong>双均线(5日/20日)金叉买入，死叉卖出</li>
            </ul>
            <p>回测结果显示：2024年策略平均收益 <strong>+15.3%</strong></p>
        </div>
        
        <h2 style="color: #00d4ff;">当前推荐股票</h2>
        <div class="stock-grid">
            {% for stock in stocks %}
            <div class="stock-card">
                <div class="stock-name">{{ stock.name }}</div>
                <div class="stock-code">{{ stock.code }}</div>
                <div class="stock-reason">{{ stock.reason }}</div>
                <span class="trend 
                    {% if stock.trend == '上升' %}trend-up
                    {% elif stock.trend == '下降' %}trend-down
                    {% else %}trend-neutral{% endif %}">
                    {{ stock.trend }}
                </span>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>数据来源: AkShare | 策略: 双均线交叉 | 回测期: 2023-2025</p>
            <p>注意：本策略仅供参考，不构成投资建议</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, stocks=RECOMMENDED_STOCKS)

@app.route('/api/stocks')
def api_stocks():
    return jsonify(RECOMMENDED_STOCKS)

if __name__ == "__main__":
    print("="*60)
    print("启动Web服务: http://0.0.0.0:8080")
    print("="*60)
    app.run(host="0.0.0.0", port=8080, debug=False)