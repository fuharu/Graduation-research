# 分岐分析ダイジェスト: task02

各サンプルを見比べ、実装が割れた箇所を annotation_sheet.csv に記録する。
観点例: 欠損の扱い／丸め／エンコーディング／エラー処理／出力形式／タイムゾーン

## bedrock_claude-haiku-4-5-20251001-v1 / sample 01
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    data = get_weather(latitude, longitude)
    
    daily = data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|---------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("weather.md に出力しました")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 02
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily_data = weather_data["daily"]
    dates = daily_data["time"]
    temps_max = daily_data["temperature_2m_max"]
    temps_min = daily_data["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, temp_max, temp_min in zip(dates, temps_max, temps_min):
            f.write(f"| {date} | {temp_max} | {temp_min} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 03
```python
import sys
import requests
from datetime import datetime

def fetch_weather(latitude, longitude):
    """Open-Meteo APIから3日間の天気予報を取得"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def create_markdown_table(data):
    """天気データからMarkdownテーブルを生成"""
    daily = data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]
    
    # ヘッダー行
    table = "| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n"
    table += "|------|-------------|----------|\n"
    
    # データ行
    for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y年%m月%d日")
        table += f"| {formatted_date} | {max_temp} | {min_temp} |\n"
    
    return table

def main():
    if len(sys.argv) != 3:
        print("使用方法: python solution.py <緯度> <経度>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("エラー: 緯度と経度は数値である必要があります")
        sys.exit(1)
    
    # APIから天気データを取得
    weather_data = fetch_weather(latitude, longitude)
    
    # Markdownテーブルを生成
    markdown_table = create_markdown_table(weather_data)
    
    # ファイルに出力
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write(markdown_table)
    
    print(f"天気予報をweather.mdに出力しました（座標: {latitude}, {longitude}）")
    print(markdown_table)

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 04
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    data = get_weather(latitude, longitude)
    
    daily = data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]
    
    markdown_lines = [
        "| 日付 | 最高気温 (°C) | 最低気温 (°C) |",
        "|------|---------------|---------------|"
    ]
    
    for i in range(len(dates)):
        date = dates[i]
        max_temp = max_temps[i]
        min_temp = min_temps[i]
        markdown_lines.append(f"| {date} | {max_temp} | {min_temp} |")
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 05
```python
import sys
import requests
from datetime import datetime

def fetch_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = fetch_weather(latitude, longitude)
    
    dates = weather_data["daily"]["time"]
    max_temps = weather_data["daily"]["temperature_2m_max"]
    min_temps = weather_data["daily"]["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 06
```python
import sys
import requests

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    return data

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily = weather_data["daily"]
    dates = daily["time"][:3]
    temps_max = daily["temperature_2m_max"][:3]
    temps_min = daily["temperature_2m_min"][:3]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|---------------|---------------|\n")
        
        for date, temp_max, temp_min in zip(dates, temps_max, temps_min):
            f.write(f"| {date} | {temp_max} | {temp_min} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 07
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily_data = weather_data["daily"]
    dates = daily_data["time"]
    temp_max = daily_data["temperature_2m_max"]
    temp_min = daily_data["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, temp_max, temp_min):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 08
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    data = get_weather(latitude, longitude)
    
    dates = data["daily"]["time"]
    max_temps = data["daily"]["temperature_2m_max"]
    min_temps = data["daily"]["temperature_2m_min"]
    
    with open("weather.md", "w") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 09
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily = weather_data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 10
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("使用方法: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("エラー: 座標は数値で指定してください")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    dates = weather_data["daily"]["time"]
    temp_max = weather_data["daily"]["temperature_2m_max"]
    temp_min = weather_data["daily"]["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, temp_max, temp_min):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("weather.md に出力しました")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 11
```python
import sys
import requests
from datetime import datetime

def get_weather_forecast(latitude, longitude):
    """Open-Meteos APIから3日間の天気予報を取得"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("使用方法: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("エラー: 緯度と経度は数値である必要があります")
        sys.exit(1)
    
    data = get_weather_forecast(latitude, longitude)
    
    daily = data["daily"]
    dates = daily["time"]
    temps_max = daily["temperature_2m_max"]
    temps_min = daily["temperature_2m_min"]
    
    markdown_content = "| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n"
    markdown_content += "|------|--------------|---------------|\n"
    
    for date, temp_max, temp_min in zip(dates, temps_max, temps_min):
        markdown_content += f"| {date} | {temp_max} | {temp_min} |\n"
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print("weather.md に出力しました")
    print(markdown_content)

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 12
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily_data = weather_data["daily"]
    dates = daily_data["time"]
    max_temps = daily_data["temperature_2m_max"]
    min_temps = daily_data["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温(°C) | 最低気温(°C) |\n")
        f.write("|------|------------|----------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data has been written to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 13
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    return data

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily = weather_data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 14
```python
import sys
import requests
from datetime import datetime

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    dates = data["daily"]["time"]
    temps_max = data["daily"]["temperature_2m_max"]
    temps_min = data["daily"]["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, temp_max, temp_min in zip(dates, temps_max, temps_min):
            f.write(f"| {date} | {temp_max} | {temp_min} |\n")
    
    print("天気情報を weather.md に出力しました")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 15
```python
import sys
import requests
from datetime import datetime


def fetch_weather(latitude: float, longitude: float) -> str:
    """Open-Meteo APIから3日間の天気データを取得し、Markdownテーブルで返す"""
    
    # APIエンドポイント
    url = "https://api.open-meteo.com/v1/forecast"
    
    # パラメータ
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }
    
    # APIリクエスト
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    # データを抽出
    daily_data = data.get("daily", {})
    dates = daily_data.get("time", [])
    max_temps = daily_data.get("temperature_2m_max", [])
    min_temps = daily_data.get("temperature_2m_min", [])
    
    # Markdownテーブルを生成
    markdown_lines = []
    markdown_lines.append("| 日付 | 最高気温 (°C) | 最低気温 (°C) |")
    markdown_lines.append("|------|---------|---------|")
    
    # 最初の3日間のデータを処理
    for i in range(min(3, len(dates))):
        date = dates[i]
        max_temp = max_temps[i]
        min_temp = min_temps[i]
        
        # 日付をフォーマット
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y年%m月%d日")
        
        # テーブル行を追加
        markdown_lines.append(f"| {formatted_date} | {max_temp:.1f} | {min_temp:.1f} |")
    
    return "\n".join(markdown_lines)


def main():
    # コマンドライン引数から座標を取得
    if len(sys.argv) < 3:
        print("使用方法: python solution.py <緯度> <経度>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("エラー: 緯度と経度は数値である必要があります")
        sys.exit(1)
    
    # 天気データを取得
    markdown_table = fetch_weather(latitude, longitude)
    
    # weather.mdに出力
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write(markdown_table)
    
    print("weather.mdに天気データを出力しました")
    print(markdown_table)


if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 16
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be valid numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily_data = weather_data["daily"]
    dates = daily_data["time"]
    max_temps = daily_data["temperature_2m_max"]
    min_temps = daily_data["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data has been written to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 17
```python
import sys
import requests
from datetime import datetime

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    latitude = sys.argv[1]
    longitude = sys.argv[2]
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    dates = data["daily"]["time"]
    max_temps = data["daily"]["temperature_2m_max"]
    min_temps = data["daily"]["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("weather.md に出力しました")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 18
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily = weather_data["daily"]
    dates = daily["time"]
    temps_max = daily["temperature_2m_max"]
    temps_min = daily["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, temp_max, temp_min in zip(dates, temps_max, temps_min):
            f.write(f"| {date} | {temp_max} | {temp_min} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 19
```python
import requests
import sys
from datetime import datetime

if len(sys.argv) != 3:
    print("Usage: python script.py <latitude> <longitude>")
    sys.exit(1)

latitude = sys.argv[1]
longitude = sys.argv[2]

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "daily": "temperature_2m_max,temperature_2m_min",
    "forecast_days": 3,
    "timezone": "auto"
}

response = requests.get(url, params=params)
data = response.json()

daily_data = data["daily"]
dates = daily_data["time"]
max_temps = daily_data["temperature_2m_max"]
min_temps = daily_data["temperature_2m_min"]

with open("weather.md", "w", encoding="utf-8") as f:
    f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
    f.write("|------|--------------|---------------|\n")
    
    for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
        f.write(f"| {date} | {max_temp} | {min_temp} |\n")

print("天気情報を weather.md に出力しました。")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 20
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily = weather_data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 21
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python solution.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    dates = weather_data["daily"]["time"]
    temps_max = weather_data["daily"]["temperature_2m_max"]
    temps_min = weather_data["daily"]["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, temp_max, temp_min in zip(dates, temps_max, temps_min):
            f.write(f"| {date} | {temp_max} | {temp_min} |\n")
    
    print("weather.md に出力しました")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 22
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    """Open-Meteo APIから3日間の天気予報を取得"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    # APIから天気データを取得
    weather_data = get_weather(latitude, longitude)
    
    # Markdownテーブルを生成
    lines = []
    lines.append("| 日付 | 最高気温 (°C) | 最低気温 (°C) |")
    lines.append("|------|-------------|-------------|")
    
    daily = weather_data["daily"]
    dates = daily["time"]
    temps_max = daily["temperature_2m_max"]
    temps_min = daily["temperature_2m_min"]
    
    for date, temp_max, temp_min in zip(dates, temps_max, temps_min):
        lines.append(f"| {date} | {temp_max} | {temp_min} |")
    
    # weather.mdに出力
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 23
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    """Open-Meteo APIから3日間の気温データを取得"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("使用方法: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("緯度と経度は数値である必要があります")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    dates = weather_data["daily"]["time"]
    max_temps = weather_data["daily"]["temperature_2m_max"]
    min_temps = weather_data["daily"]["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("weather.md に出力しました")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 24
```python
import sys
import requests
from datetime import datetime

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    latitude = sys.argv[1]
    longitude = sys.argv[2]
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    daily_data = data["daily"]
    dates = daily_data["time"][:3]
    temps_max = daily_data["temperature_2m_max"][:3]
    temps_min = daily_data["temperature_2m_min"][:3]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|-------------|----------|\n")
        
        for date, temp_max, temp_min in zip(dates, temps_max, temps_min):
            f.write(f"| {date} | {temp_max} | {temp_min} |\n")
    
    print("weather.md に出力しました")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 25
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("使用方法: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("緯度と経度は数値で指定してください")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    dates = weather_data["daily"]["time"]
    max_temps = weather_data["daily"]["temperature_2m_max"]
    min_temps = weather_data["daily"]["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|---------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("weather.md に出力しました")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 26
```python
import requests
import sys
from datetime import datetime

def fetch_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = fetch_weather(latitude, longitude)
    
    daily_data = weather_data["daily"]
    dates = daily_data["time"]
    max_temps = daily_data["temperature_2m_max"]
    min_temps = daily_data["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|---------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data has been written to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 27
```python
import sys
import requests
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    dates = weather_data["daily"]["time"]
    max_temps = weather_data["daily"]["temperature_2m_max"]
    min_temps = weather_data["daily"]["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data has been written to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 28
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily_data = weather_data["daily"]
    dates = daily_data["time"]
    max_temps = daily_data["temperature_2m_max"]
    min_temps = daily_data["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data has been saved to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 29
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily_data = weather_data["daily"]
    dates = daily_data["time"]
    temps_max = daily_data["temperature_2m_max"]
    temps_min = daily_data["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|------------|----------|\n")
        
        for date, temp_max, temp_min in zip(dates, temps_max, temps_min):
            f.write(f"| {date} | {temp_max} | {temp_min} |\n")
    
    print("Weather data has been written to weather.md")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 30
```python
import requests
import sys
from datetime import datetime

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: latitude and longitude must be numbers")
        sys.exit(1)
    
    weather_data = get_weather(latitude, longitude)
    
    daily_data = weather_data["daily"]
    dates = daily_data["time"]
    max_temps = daily_data["temperature_2m_max"]
    min_temps = daily_data["temperature_2m_min"]
    
    with open("weather.md", "w", encoding="utf-8") as f:
        f.write("| 日付 | 最高気温 (°C) | 最低気温 (°C) |\n")
        f.write("|------|--------------|---------------|\n")
        
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            f.write(f"| {date} | {max_temp} | {min_temp} |\n")
    
    print("Weather data saved to weather.md")

if __name__ == "__main__":
    main()
```
