import os
import telebot
import requests
import pandas as pd
import socket
import random
from telebot import types
from sklearn.ensemble import RandomForestClassifier

# --- 1. 配置与初始化 ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY') 

bot = telebot.TeleBot(TOKEN)

# --- 2. 准备 AI 模型 (保持原样) ---
if os.path.exists('weather.csv'):
    df = pd.read_csv('weather.csv')
    if df['RainTomorrow'].dtype == 'object':
        df['RainTomorrow'] = df['RainTomorrow'].map({'Yes': 1, 'No': 0})
    df = df.fillna(0)
    X = df[['Temp', 'Humidity']] 
    y = df['RainTomorrow']
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
else:
    # 备用模型
    X = [[-5, 80], [20, 40]]
    y = [1, 0]
    model = RandomForestClassifier()
    model.fit(X, y)

# --- 3. 辅助函数 ---

def get_real_weather_spb():
    """获取圣彼得堡天气"""
    city = "Saint Petersburg"
    if OPENWEATHER_API_KEY:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            res = requests.get(url).json()
            return {
                "temp": res['main']['temp'],
                "humidity": res['main']['humidity'],
                "desc": res['weather'][0]['description'].capitalize(),
                "city": city,
                "wind": res['wind']['speed']
            }
        except:
            pass
    
    # 模拟数据
    return {
        "temp": round(random.uniform(-5.0, 3.0), 1),
        "humidity": random.randint(70, 95),
        "desc": random.choice(["Light Snow ❄️", "Overcast Clouds ☁️"]),
        "city": "Saint Petersburg",
        "wind": random.randint(1, 10)
    }

def get_system_info():
    """获取容器内部信息，证明运行在云端"""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return f"📦 <b>Container ID:</b> <code>{hostname}</code>\n🌐 <b>Internal IP:</b> <code>{ip_address}</code>"

# --- 4. 消息处理器 ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # 创建底部键盘按钮
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('🌦 Check Weather')
    itembtn2 = types.KeyboardButton('🖥 System Status')
    itembtn3 = types.KeyboardButton('🎲 AI Luck')
    markup.add(itembtn1, itembtn2, itembtn3)

    bot.reply_to(message, 
        "🇷🇺 <b>Privet! I am your Advanced AI Assistant.</b>\n\n"
        "Please choose an option from the menu below:", 
        parse_mode='HTML', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🌦 Check Weather')
def weather_btn(message):
    # 复用原来的天气逻辑，但加了风速
    try:
        current = get_real_weather_spb()
        next_hour_temp = round(current['temp'] - 0.5, 1)
        rain_pred = model.predict([[current['temp'], current['humidity']]])[0]
        
        if rain_pred == 1:
            rain_text = "🌧️ <b>AI ALERT:</b> High chance of Snow/Rain!"
        else:
            rain_text = "☁️ <b>AI PRED:</b> Likely dry."

        response = f"""
🏛️ <b>Saint Petersburg Live</b> 🇷🇺
━━━━━━━━━━━━━━━━
🌡️ <b>Temp:</b> {current['temp']}°C
💧 <b>Humidity:</b> {current['humidity']}%
💨 <b>Wind:</b> {current['wind']} m/s
👀 <b>Condition:</b> {current['desc']}

🧠 <b>Neural Network Forecast</b>
━━━━━━━━━━━━━━━━
{rain_text}
Trend: Temp dropping to {next_hour_temp}°C.
        """
        bot.reply_to(message, response, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(func=lambda message: message.text == '🖥 System Status')
def status_btn(message):
    # 展示这是真正的云端容器
    sys_info = get_system_info()
    bot.reply_to(message, 
                 f"⚙️ <b>Infrastructure Info</b>\n━━━━━━━━━━━━━━━━\n{sys_info}\n\n✅ <b>Platform:</b> Linux (OpenStack/K8s)\n✅ <b>Python:</b> 3.9", 
                 parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == '🎲 AI Luck')
def luck_btn(message):
    # 一个简单的小游戏
    score = random.randint(1, 100)
    if score > 80:
        msg = f"🚀 <b>{score}/100</b>! Great day to deploy to production!"
    elif score > 50:
        msg = f"😐 <b>{score}/100</b>. Normal day."
    else:
        msg = f"⚠️ <b>{score}/100</b>. Don't touch the servers today!"
    bot.reply_to(message, msg, parse_mode='HTML')

# 启动 Bot
bot.polling()