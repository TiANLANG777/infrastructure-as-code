import os
import time
import logging
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pythonjsonlogger import jsonlogger
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta

# --- 1. 日志设置 ---
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s api_path=%(api_path)s duration_ms=%(duration_ms)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Tianlang DevOps AI Weather")
templates = Jinja2Templates(directory="templates")

# --- 2. AI 模型配置 ---
API_KEY = '6594e88cbf3897837d19109296973949'  # 你的 API Key
CITY = 'Beijing'  # 默认城市
MODEL = None  # 全局模型变量

# --- 3. 机器学习核心逻辑 (从 Notebook 移植) ---
def train_model_startup():
    """系统启动时训练模型，避免每次刷新网页都训练"""
    global MODEL
    try:
        if not os.path.exists('weather.csv'):
            logger.warning("weather.csv not found, skipping AI training.", extra={'api_path': 'init', 'duration_ms': 0})
            return

        df = pd.read_csv('weather.csv').dropna()
        # 简单的数据准备：使用前一天的温度预测后一天
        X = df['Temp'].values[:-1].reshape(-1, 1)
        y = df['Temp'].values[1:]
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        MODEL = model
        logger.info("AI Model trained successfully!", extra={'api_path': 'init', 'duration_ms': 0})
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}", extra={'api_path': 'init', 'duration_ms': 0})

def predict_future_temps(current_temp):
    """递归预测未来 5 小时温度"""
    if MODEL is None:
        return [current_temp] * 5  # 如果模型没训练好，返回当前温度作为兜底
    
    preds = []
    last_val = current_temp
    for _ in range(5):
        next_val = MODEL.predict([[last_val]])[0]
        preds.append(next_val)
        last_val = next_val
    return preds

def get_weather_plot():
    """获取实时天气并生成 Plotly 图表 HTML"""
    try:
        # 1. 调用 OpenWeatherMap API
        url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'
        res = requests.get(url).json()
        current_temp = res['main']['temp']
        description = res['weather'][0]['description']
        
        # 2. 使用 AI 模型预测
        future_temps = predict_future_temps(current_temp)
        
        # 3. 生成 Plotly 图表
        times = [(datetime.now() + timedelta(hours=i+1)).strftime("%H:00") for i in range(5)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times, y=future_temps, 
            mode='lines+markers',
            name='AI Prediction',
            line=dict(color='#00f2ea', width=3)
        ))
        
        fig.update_layout(
            title=f'{CITY} 未来5小时 AI 温度预测 (Current: {current_temp}°C)',
            paper_bgcolor='rgba(0,0,0,0)', # 透明背景
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c9d1d9'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#30363d'),
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        
        # 转换为 HTML div 字符串，不包含完整的 html 标签，只包含 div
        return pio.to_html(fig, full_html=False, include_plotlyjs='cdn'), current_temp, description
        
    except Exception as e:
        logger.error(f"Weather generation failed: {str(e)}", extra={'api_path': 'plot', 'duration_ms': 0})
        return "<div>Error loading weather data</div>", 0, "Unknown"

# --- 4. 生命周期与路由 ---
@app.on_event("startup")
async def startup_event():
    train_model_startup()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    start = time.time()
    
    # 获取图表 HTML
    plot_html, temp, desc = get_weather_plot()
    
    pod_name = os.getenv("K8S_POD_NAME", "Local-Dev")
    
    # 记录日志
    logger.info("rendering_dashboard", extra={
        'api_path': '/', 
        'duration_ms': round((time.time()-start)*1000, 2)
    })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "student_name": "Тянь Лан (Tianlang)",
        "pod_name": pod_name,
        "plot_div": plot_html,  # 注入图表代码
        "current_temp": temp,
        "weather_desc": desc,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.get("/health")
def health():
    return {"status": "ok"}
