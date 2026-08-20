"""
Data API Service - 自动赚钱 API 服务
提供 URL 短链接、图片处理、PDF 转换、文本分析等 API
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
import hashlib
import time
import random
import asyncio
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

app = FastAPI(
    title="Data API Service",
    description="自动赚钱 API 服务 - 按调用次数收费",
    version="1.0.0"
)

# 数据库初始化
DB_PATH = Path.home() / "桌面" / "data-api-service" / "api.db"
DB_PATH.parent.mkdir(exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            user_email TEXT NOT NULL,
            usage_count INTEGER DEFAULT 0,
            monthly_limit INTEGER DEFAULT 1000,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class ShortenRequest(BaseModel):
    url: str
    custom_code: Optional[str] = None

class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str
    created_at: str

@app.get("/")
async def root():
    return {
        "message": "Data API Service - 自动赚钱服务",
        "version": "1.0.0",
        "endpoints": [
            "/api/v1/shorten",
            "/api/v1/resolve/{code}",
            "/api/v1/stats"
        ]
    }

@app.post("/api/v1/shorten", response_model=ShortenResponse)
async def shorten_url(request: ShortenRequest):
    """创建短链接"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 生成短代码
    if request.custom_code:
        code = request.custom_code
    else:
        code = hashlib.md5(f"{request.url}{time.time()}".encode()).hexdigest()[:8]
    
    # 检查是否已存在
    cursor.execute("SELECT id FROM urls WHERE code = ?", (code,))
    if cursor.fetchone():
        code = hashlib.md5(f"{request.url}{time.time()}{random.randint(1,1000)}".encode()).hexdigest()[:8]
    
    try:
        cursor.execute(
            "INSERT INTO urls (code, original_url) VALUES (?, ?)",
            (code, request.url)
        )
        conn.commit()
        short_url = f"https://api.data-service.com/{code}"
        return ShortenResponse(
            code=code,
            short_url=short_url,
            original_url=request.url,
            created_at=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/api/v1/resolve/{code}")
async def resolve_url(code: str):
    """解析短链接"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT original_url, clicks FROM urls WHERE code = ?", (code,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="URL not found")
    
    # 增加点击计数
    cursor.execute("UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    
    return {
        "original_url": row[0],
        "clicks": row[1] + 1
    }

@app.get("/api/v1/stats")
async def get_stats():
    """获取统计信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM urls")
    total_urls = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(clicks) FROM urls")
    total_clicks = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM api_keys WHERE status = 'active'")
    total_users = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_urls": total_urls,
        "total_clicks": total_clicks,
        "total_users": total_users,
        "revenue_estimate": f"${total_clicks * 0.001:.2f}"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "data-api"}
