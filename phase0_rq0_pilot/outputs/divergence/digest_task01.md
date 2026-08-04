# 分岐分析ダイジェスト: task01

各サンプルを見比べ、実装が割れた箇所を annotation_sheet.csv に記録する。
観点例: 欠損の扱い／丸め／エンコーディング／エラー処理／出力形式／タイムゾーン

## bedrock_claude-haiku-4-5-20251001-v1 / sample 01
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthをstring型に変換して出力用に整形
summary['year_month'] = summary['year_month'].astype(str)

# 列名を整理
summary.columns = ['month', 'store_id', 'total_sales']

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("summary.csv に出力しました")
print(summary)
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 02
```python
import pandas as pd

# Read the sales data
df = pd.read_csv('sales.csv')

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# Calculate sales amount
df['sales'] = df['quantity'] * df['unit_price']

# Extract year-month for grouping
df['year_month'] = df['date'].dt.to_period('M')

# Group by year_month and store_id, then sum the sales
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# Rename columns for clarity
summary.columns = ['month', 'store_id', 'total_sales']

# Sort by month and store_id
summary = summary.sort_values(['month', 'store_id'])

# Save to CSV
summary.to_csv('summary.csv', index=False)

print("Summary saved to summary.csv")
print(summary.head())
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 03
```python
import pandas as pd

# Read the sales.csv file
df = pd.read_csv('sales.csv')

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Calculate sales for each row
df['sales'] = df['quantity'] * df['unit_price']

# Extract year and month for grouping
df['year_month'] = df['date'].dt.to_period('M')

# Group by year_month and store_id, then sum the sales
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# Rename columns for clarity
summary.columns = ['month', 'store_id', 'total_sales']

# Convert year_month back to string format for CSV output
summary['month'] = summary['month'].astype(str)

# Write to summary.csv
summary.to_csv('summary.csv', index=False)

print("Summary data has been written to summary.csv")
print(summary.head())
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 04
```python
import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算（quantity × unit_price）
df['sales'] = df['quantity'] * df['unit_price']

# 月を抽出（YYYY-MM形式）
df['month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['month', 'store_id'])['sales'].sum().reset_index()

# month を文字列に変換して見やすくする
summary['month'] = summary['month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了：summary.csv に出力しました")
print("\n集計結果:")
print(summary)
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 05
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算（quantity × unit_price）
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthをstring型に変換して見やすくする
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了。summary.csvに出力しました。")
print(summary.head())
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 06
```python
import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthをstring型に変換
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了: summary.csv に出力しました")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 07
```python
import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthをstring型に変換
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("summary.csv を作成しました")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 08
```python
import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('sales.csv')

# dateをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthを文字列に変換（CSV出力用）
summary['year_month'] = summary['year_month'].astype(str)

# 列名を変更
summary.columns = ['month', 'store_id', 'total_sales']

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計が完了しました。summary.csvを出力しました。")
print(summary.head())
```
