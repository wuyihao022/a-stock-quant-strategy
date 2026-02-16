"""获取沪深300成分股列表"""
import akshare as ak

# 获取沪深300成分股
print("获取沪深300成分股...")
df = ak.stock_hs300_stocks_symbol()

# 显示前几行
print(df.head(10))
print(f"\n总数: {len(df)}")

# 清理数据
df = df[['代码', '名称']].rename(columns={'代码': 'code', '名称': 'name'})
df['code'] = df['code'].astype(str).str.zfill(6)

# 保存
df.to_csv('hs300_stocks.csv', index=False, encoding='utf-8')
print(f"已保存到 hs300_stocks.csv")
print(df.head(20))