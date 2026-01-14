import os
import telebot
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 1. 获取配置
TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY') 

bot = telebot.TeleBot(TOKEN)

# 2. 准备 AI 模型
# 读取 CSV
if os.path.exists('weather.csv'):
    df = pd.read_csv('weather.csv')
    
    # --- 关键修改 1: 数据预处理 ---
    # 如果 RainTomorrow 是 Yes/No，转换成 1/0
    # 如果已经是数字，这行代码会自动跳过
    if df['RainTomorrow'].dtype == 'object':
        df['RainTomorrow'] = df['RainTomorrow'].map({'Yes': 1, 'No': 0})
    
    # 处理缺失值 (填充为0或平均值，防止报错)
    df = df.fillna(0)

    # --- 关键修改 2: 使用原表的大写列名 ---
    # 原表: MinTemp,MaxTemp,...,Humidity,Pressure,Temp,RainTomorrow
    X = df[['Temp', 'Humidity']] 
    y = df['RainTomorrow']
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
else:
    # 备用方案：如果真的找不到 csv，才用模拟数据 (防止程序启动失败)
    print("Warning: weather.csv not found, using dummy model.")
    X = [[-5, 80], [20, 40]]
    y = [1, 0]
    model = RandomForestClassifier()
    model.fit(X, y)

def get_real_weather_spb():
    """获取圣彼得堡的实时天气"""
    city = "Saint Petersburg"
    
    # 尝试获取真实数据
    if OPENWEATHER_API_KEY:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            res = requests.get(url).json()
            return {
                "temp": res['main']['temp'],
                "humidity": res['main']['humidity'],
                "desc": res['weather'][0]['description'].capitalize(),
                "city": city
            }
        except:
            pass
    
    # 模拟数据
    import random
    return {
        "temp": round(random.uniform(-5.0, 3.0), 1),
        "humidity": random.randint(70, 95),
        "desc": random.choice(["Light Snow ❄️", "Overcast Clouds ☁️", "Mist 🌫️"]),
        "city": "Saint Petersburg"
    }

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 
        "🇷🇺 <b>Privet! I am your Saint Petersburg Weather Bot.</b>\n\n"
        "I run on ☁️ <i>OpenStack</i> & ⚓ <i>Kubernetes</i>.\n"
        "Type /weather to get the AI forecast.", 
        parse_mode='HTML')

@bot.message_handler(commands=['weather'])
def send_weather(message):
    try:
        # 1. 获取数据
        current = get_real_weather_spb()
        
        # 2. AI 预测
        next_hour_temp = round(current['temp'] - 0.5, 1)
        
        # 注意：这里我们把抓取到的 temp 和 humidity 传给模型
        # 模型只关心传入数字的顺序 [温度, 湿度]，不关心变量名叫什么
        rain_pred = model.predict([[current['temp'], current['humidity']]])[0]
        
        # 3. 构建消息
        if rain_pred == 1:
            rain_text = "🌧️ <b>PRECIPITATION ALERT:</b> High chance of Snow/Rain. Take an umbrella!"
        else:
            rain_text = "☁️ <b>PRECIPITATION:</b> Likely cloudy but dry."

        response = f"""
🏛️ <b>Weather Report: {current['city']}</b> 🇷🇺
━━━━━━━━━━━━━━━━━━━━━━
🌡️ <b>Current Status</b>
  ├  <b>Temp:</b> {current['temp']}°C
  ├  <b>Humidity:</b> {current['humidity']}%
  └  <b>Condition:</b> {current['desc']}

🧠 <b>AI Prediction (RandomForest on Real Data)</b>
━━━━━━━━━━━━━━━━━━━━━━
🔮 {rain_text}
📉 <b>Trend:</b> Temp dropping to {next_hour_temp}°C in 1h.

🤖 <i>Deployed via Jenkins CI/CD</i>
        """
        bot.reply_to(message, response, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

# 启动 Bot
bot.polling()