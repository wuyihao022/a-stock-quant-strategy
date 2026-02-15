"""Flask Web UI：展示当前推荐股票。"""

from __future__ import annotations

from flask import Flask, render_template_string

from data.data_loader import AShareDataLoader
from strategy.selectors import SelectorService

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>A股量化选股</title>
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; }
      table { border-collapse: collapse; width: 100%; }
      th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
      th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align: left; }
      th { background: #f6f6f6; }
    </style>
  </head>
  <body>
    <h1>当前推荐股票</h1>
    <p>策略：大市值 + 低PE + 高股息 + ROE&gt;10%</p>
    <table>
      <thead>
        <tr>
          <th>代码</th>
          <th>名称</th>
          <th>总市值</th>
          <th>PE</th>
          <th>股息率</th>
          <th>ROE</th>
          <th>评分</th>
        </tr>
      </thead>
      <tbody>
        {% for row in rows %}
        <tr>
          <td>{{ row.symbol }}</td>
          <td>{{ row.name }}</td>
          <td>{{ "{:,}".format(row.market_cap|int) }}</td>
          <td>{{ "%.2f"|format(row.pe) }}</td>
          <td>{{ "%.2f%%"|format(row.dividend_yield * 100) }}</td>
          <td>{{ "%.2f"|format(row.roe) }}</td>
          <td>{{ "%.3f"|format(row.score) }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </body>
</html>
"""


@app.route("/")
def index():
    loader = AShareDataLoader()
    service = SelectorService(loader)

    try:
        picks = service.get_recommendations(top_n=20)
        rows = picks.to_dict(orient="records")
    except Exception as exc:
        rows = []
        return f"<h3>数据加载失败: {exc}</h3>", 500

    return render_template_string(HTML_TEMPLATE, rows=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
