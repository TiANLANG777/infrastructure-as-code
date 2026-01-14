import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pythonjsonlogger import jsonlogger

# --- 1. 专业级 DevOps 日志配置 ---
logger = logging.getLogger()
logHandler = logging.StreamHandler()
# 使用专业的 JSON Formatter，自动包含时间戳、日志级别等
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s api_path=%(api_path)s method=%(method)s status_code=%(status_code)s duration_ms=%(duration_ms)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Tianlang DevOps Monitor")

# 设置模板目录
templates = Jinja2Templates(directory="templates")

# --- 2. 性能监控中间件 (Middleware) ---
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # 记录结构化日志
    logger.info("request_processed", extra={
        'api_path': request.url.path,
        'method': request.method,
        'status_code': response.status_code,
        'duration_ms': round(process_time, 2)
    })
    return response

# --- 3. 业务路由 ---

# 健康检查接口 (供 K8s 使用)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "component": "backend"}

# 首页 - 后端动态渲染 HTML
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # 获取环境变量 (K8s 传入)
    pod_name = os.getenv("K8S_POD_NAME", "Unknown-Local-Host")
    env_type = os.getenv("ENV_TYPE", "Development")
    
    logger.info(f"Rendering index page for pod: {pod_name}", extra={'api_path': '/', 'method': 'GET', 'status_code': 200, 'duration_ms': 0})

    # 将数据注入模板
    return templates.TemplateResponse("index.html", {
        "request": request,
        "student_name": "Тянь Лан (Tianlang)",
        "pod_name": pod_name,
        "env_type": env_type,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S UTC")
    })
