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

## bedrock_claude-haiku-4-5-20251001-v1 / sample 09
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthを文字列に変換
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了: summary.csv に出力されました")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 10
```python
import pandas as pd
from datetime import datetime

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとに売上を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthをstring型に変換
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了。summary.csvに出力しました。")
print(summary.head(10))
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 11
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

# year_monthをstring型に変換（出力用）
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了: summary.csv に出力されました")
print(summary)
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 12
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthを文字列に変換
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("summary.csv に出力しました")
print(summary)
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 13
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateを日時型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算（quantity × unit_price）
df['sales'] = df['quantity'] * df['unit_price']

# 月を抽出
df['month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['month', 'store_id'])['sales'].sum().reset_index()

# monthをstring型に変換してCSV出力に対応
summary['month'] = summary['month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了: summary.csv を出力しました")
print(summary.head(10))
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 14
```python
import pandas as pd

# sales.csvを読み込む
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
print(summary)
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 15
```python
import pandas as pd

# sales.csvを読み込む
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
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 16
```python
import pandas as pd

# sales.csvを読み込み
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthを文字列に変換
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了。summary.csvに出力しました。")
print(summary)
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 17
```python
import pandas as pd

# sales.csvを読み込む
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

print("summary.csv に出力完了しました")
print(summary)
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 18
```python
import pandas as pd
import os

# Load the sales data
df = pd.read_csv('sales.csv')

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# Calculate sales
df['sales'] = df['quantity'] * df['unit_price']

# Extract year and month
df['year_month'] = df['date'].dt.to_period('M')

# Group by year_month and store_id, sum the sales
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# Rename columns for clarity
summary.columns = ['year_month', 'store_id', 'total_sales']

# Convert year_month back to string for CSV output
summary['year_month'] = summary['year_month'].astype(str)

# Output to CSV
summary.to_csv('summary.csv', index=False)

print("Summary data has been saved to summary.csv")
print(summary.head())
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 19
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthをstringに変換
summary['year_month'] = summary['year_month'].astype(str)

# カラム名を整理
summary.columns = ['date', 'store_id', 'total_sales']

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了。summary.csvに出力しました。")
print(summary.head())
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 20
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthを文字列に変換
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("summary.csvに出力しました")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 21
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthをstring型に変換（CSVに適した形式で出力）
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("summary.csvに集計結果を出力しました")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 22
```python
import pandas as pd

# sales.csvを読み込む
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

# カラム名を変更
summary.columns = ['month', 'store_id', 'total_sales']

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了。summary.csvに出力しました。")
print(summary.head())
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 23
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateを日時型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthを文字列に変換
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("summary.csv に出力しました")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 24
```python
import pandas as pd
from datetime import datetime

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateを日付型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# 結果をsummary.csvに出力
summary.to_csv('summary.csv', index=False)

print("summary.csvに集計結果を出力しました。")
print(summary.head())
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 25
```python
import pandas as pd
from datetime import datetime

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthを文字列に変換
summary['year_month'] = summary['year_month'].astype(str)

# カラム名を整理
summary.columns = ['month', 'store_id', 'total_sales']

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了: summary.csv に出力しました")
print(summary.head())
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 26
```python
import csv
from datetime import datetime
from collections import defaultdict

# sales.csvを読み込む
sales_data = defaultdict(float)

with open('sales.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = row['date']
        store_id = row['store_id']
        quantity = float(row['quantity'])
        unit_price = float(row['unit_price'])
        
        # 日付から年月を抽出
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        year_month = date_obj.strftime('%Y-%m')
        
        # 月ごと・店舗ごとのキーを作成
        key = (year_month, store_id)
        
        # 売上を計算して加算
        sales = quantity * unit_price
        sales_data[key] += sales

# summary.csvに出力
with open('summary.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['month', 'store_id', 'total_sales'])
    
    # キーでソートして出力
    for (month, store_id) in sorted(sales_data.keys()):
        writer.writerow([month, store_id, sales_data[(month, store_id)]])

print("summary.csvに出力しました")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 27
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthをstring型に変換（CSVに出力するため）
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了: summary.csv に出力しました")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 28
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをDatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# year_monthを文字列に変換（CSVに保存しやすくするため）
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了。summary.csvに出力しました。")
print(summary)
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 29
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# 年月をstring型に変換（CSVに出力するため）
summary['year_month'] = summary['year_month'].astype(str)

# summary.csvに出力
summary.to_csv('summary.csv', index=False)

print("summary.csvに出力しました。")
print(summary)
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 30
```python
import pandas as pd

# sales.csvを読み込む
df = pd.read_csv('sales.csv')

# dateカラムをdatetime型に変換
df['date'] = pd.to_datetime(df['date'])

# 売上を計算
df['sales'] = df['quantity'] * df['unit_price']

# 年月を抽出
df['year_month'] = df['date'].dt.to_period('M')

# 月ごと・店舗ごとの売上合計を集計
summary = df.groupby(['year_month', 'store_id'])['sales'].sum().reset_index()

# 年月をstring型に変換（CSV出力用）
summary['year_month'] = summary['year_month'].astype(str)

# 結果をsummary.csvに出力
summary.to_csv('summary.csv', index=False)

print("集計完了。結果をsummary.csvに出力しました。")
```
