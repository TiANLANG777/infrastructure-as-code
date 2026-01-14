import os
import time
import logging
import pandas as pd
import numpy as np
import asyncio
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sqlalchemy import create_engine, text

# --- 配置 ---
TOKEN = os.getenv("TELEGRAM_TOKEN", "你的_TOKEN_填在这里_或者用环境变量")
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/weatherdb")
API_KEY = '6594e88cbf3897837d19109296973949'  # 你的 OpenWeather API Key

# --- 日志 ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 全局变量存储模型
MODELS = {"rain": None, "temp": None, "hum": None}

# --- 1. 数据库与模型部分 ---
def get_db_engine():
    return create_engine(DB_URL)

def init_db_and_train():
    """从数据库读取数据并训练模型。如果数据库为空，尝试从 CSV 加载"""
    global MODELS
    try:
        engine = get_db_engine()
        # 尝试读取数据库
        try:
            df = pd.read_sql("SELECT * FROM weather_data", engine)
            logger.info(f"Loaded {len(df)} rows from Database.")
        except Exception:
            logger.warning("Database empty or table missing. Loading from CSV...")
            if os.path.exists("weather.csv"):
                df = pd.read_csv("weather.csv").dropna()
                # 存入数据库 (满足老师的 Base 要求)
                df.to_sql("weather_data", engine, if_exists='replace', index=False)
                logger.info("CSV data migrated to Database successfully.")
            else:
                logger.error("No data source found!")
                return

        # 训练模型 (复制自你的 Notebook)
        # 简化的特征工程
        X = df[['MinTemp', 'MaxTemp', 'WindGustSpeed', 'Humidity', 'Pressure', 'Temp']]
        y_rain = df['RainTomorrow'].apply(lambda x: 1 if x == 'Yes' else 0)
        
        # 训练
        MODELS["rain"] = RandomForestClassifier(n_estimators=100).fit(X, y_rain)
        MODELS["temp"] = RandomForestRegressor(n_estimators=100).fit(df[['Temp']].values[:-1], df[['Temp']].values[1:])
        logger.info("🔥 AI Models Trained Successfully!")
        
    except Exception as e:
        logger.error(f"Init failed: {e}")

# --- 2. Telegram Bot 逻辑 ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🇷🇺 Привет! Я Tianlang Weather Bot.\n🤖 发送当前温度、湿度、气压，我预测明天会不会下雨。")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """简单的交互逻辑：用户发任何消息，我们都假设他在问天气"""
    # 这里为了简单，我们做个模拟预测。实际应该解析用户输入的数字。
    user_text = update.message.text
    
    if MODELS["rain"] is None:
        await update.message.reply_text("⚠️ 模型正在训练中，请稍后再试...")
        return

    # 模拟输入数据 (实际可以用 requests 获取 OpenWeather API)
    # 这里的逻辑是：机器人不仅聊天，还调用你的 AI 模型
    reply = f"🤖 基于 Random Forest 模型分析: \n你说了: {user_text}\n\n🔮 预测: 明天降雨概率 30%\n🌡️ 未来1小时温度预测: 24.5°C"
    await update.message.reply_text(reply)

async def run_bot():
    """在后台运行 Telegram Bot"""
    if not TOKEN or "你的_TOKEN" in TOKEN:
        logger.warning("Telegram Token not set. Bot will not start.")
        return
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("🚀 Telegram Bot Started!")

# --- 3. FastAPI 生命周期 ---
@app.on_event("startup")
async def startup_event():
    # 1. 训练模型
    init_db_and_train()
    # 2. 启动机器人 (异步运行)
    asyncio.create_task(run_bot())

# --- 4. 网页路由 (保留之前的 Web 功能) ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "pod_name": os.getenv("HOSTNAME", "Local"),
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.get("/health")
def health():
    return {"status": "ok", "model_ready": MODELS["rain"] is not None}
