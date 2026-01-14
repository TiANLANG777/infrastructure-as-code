import os
import telebot
import requests
import pandas as pd
import socket
import random
from telebot import types
from sklearn.ensemble import RandomForestClassifier

# --- 1. 配置 ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY') 

bot = telebot.TeleBot(TOKEN)

# --- 2. 准备 AI 模型 ---
if os.path.exists('weather.csv'):
    df = pd.read_csv('weather.csv')
    # 数据清洗：把 Yes/No 变成 1/0
    if df['RainTomorrow'].dtype == 'object':
        df['RainTomorrow'] = df['RainTomorrow'].map({'Yes': 1, 'No': 0})
    df = df.fillna(0)
    
    # 使用 Temp (温度) 和 Humidity (湿度) 作为特征
    X = df[['Temp', 'Humidity']] 
    y = df['RainTomorrow']
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
else:
    # 备用逻辑，防止无文件报错
    X = [[-5, 80], [20, 40]]
    y = [1, 0]
    model = RandomForestClassifier()
    model.fit(X, y)

# --- 3. 获取真实数据函数 ---
def get_real_weather_spb():
    """从 OpenWeatherMap 获取圣彼得堡的真实数据"""
    city = "Saint Petersburg"
    
    # 优先使用 API 获取真实值
    if OPENWEATHER_API_KEY:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            res = requests.get(url).json()
            
            # 提取我们需要的所有真实字段
            return {
                "temp": res['main']['temp'],          # 真实温度
                "humidity": res['main']['humidity'],  # 真实湿度
                "wind": res['wind']['speed'],         # 真实风速
                "desc": res['weather'][0]['description'].capitalize(), # 真实天气描述
                "city": city,
                "is_real": True # 标记为真实数据
            }
        except Exception as e:
            print(f"API Error: {e}")
            pass
    
    # 如果 API 失败，返回模拟数据 (兜底)
    return {
        "temp": round(random.uniform(-5.0, 3.0), 1),
        "humidity": random.randint(70, 95),
        "wind": random.randint(1, 8),
        "desc": "Simulated Clouds",
        "city": "Saint Petersburg (Sim)",
        "is_real": False
    }

def get_system_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return f"{hostname} / {ip_address}"

# --- 4. 消息交互逻辑 ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # 创建按钮菜单
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_weather = types.KeyboardButton('🌦 Real Weather + AI')
    btn_status = types.KeyboardButton('🖥 System Status')
    markup.add(btn_weather, btn_status)

    bot.reply_to(message, 
        "🤖 <b>System Ready.</b>\nSelect an option to fetch live data from Saint Petersburg:", 
        parse_mode='HTML', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🌦 Real Weather + AI')
def weather_btn(message):
    try:
        # 1️⃣ 获取真实数据 (Real Data)
        data = get_real_weather_spb()
        
        # 2️⃣ AI 进行推理 (AI Inference)
        # 将真实的温度和湿度喂给模型
        rain_prob = model.predict([[data['temp'], data['humidity']]])[0]
        
        # 3️⃣ 生成结果文案
        if rain_prob == 1:
            ai_verdict = "🌧️ <b>YES</b> (High Risk of Rain/Snow)"
        else:
            ai_verdict = "☁️ <b>NO</b> (Likely Dry)"

        # 数据来源标记
        source_tag = "🟢 Live API Data" if data['is_real'] else "🔴 Simulated Data"

        # 4️⃣ 组装最终消息
        response = f"""
🏛️ <b>Weather Report: {data['city']}</b>
━━━━━━━━━━━━━━━━━━
📊 <b>REAL-TIME VALUES ({source_tag})</b>
🌡️ <b>Temp:</b>     {data['temp']} °C
💧 <b>Humidity:</b> {data['humidity']} %
💨 <b>Wind:</b>     {data['wind']} m/s
👀 <b>Weather:</b>  {data['desc']}

🧠 <b>AI PREDICTION (RandomForest)</b>
<i>Based on current Temp & Humidity:</i>
━━━━━━━━━━━━━━━━━━
🔮 <b>Will it Rain?</b>  {ai_verdict}

🤖 <i>Powered by OpenWeatherMap & Jenkins CI/CD</i>
        """
        bot.reply_to(message, response, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

@bot.message_handler(func=lambda message: message.text == '🖥 System Status')
def status_btn(message):
    info = get_system_info()
    bot.reply_to(message, f"📦 <b>Container Info:</b>\n{info}", parse_mode='HTML')

# 启动
bot.polling()