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
