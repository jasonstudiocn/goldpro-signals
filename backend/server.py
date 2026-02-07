from fastapi import FastAPI, APIRouter, BackgroundTasks, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from data_fetcher import GoldDataFetcher
from technical_analysis import TechnicalAnalyzer
from ai_analysis import AIAnalyzer
from signal_evaluator import SignalEvaluator

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="黄金交易分析系统")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# 初始化服务
data_fetcher = GoldDataFetcher()
ai_analyzer = AIAnalyzer()
signal_evaluator = SignalEvaluator()

# Pydantic Models
class GoldPrice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    price: float
    change: float
    change_percent: float
    timestamp: str
    currency: str
    unit: str

class TechnicalIndicators(BaseModel):
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_20: Optional[float] = None
    rsi: dict
    macd: dict
    bollinger: dict
    atr: dict
    stochastic: dict

class TradingSignal(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal: str  # BUY, SELL, HOLD
    confidence: float
    buy_score: float
    sell_score: float
    timestamp: str
    signals_detail: List[dict]
    recommendation: str
    current_price: Optional[float] = None

class EmailAlert(BaseModel):
    email: EmailStr
    signal_id: str

class UserSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    alert_threshold: float = 70.0  # 信号信心度阈值
    enabled: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@api_router.get("/")
async def root():
    return {"message": "黄金交易分析系统 API"}

@api_router.get("/price/current", response_model=GoldPrice)
async def get_current_price():
    """获取实时黄金价格"""
    price_data = data_fetcher.fetch_real_time_price()
    if not price_data:
        raise HTTPException(status_code=500, detail="无法获取实时价格")
    
    # 保存到数据库
    await db.price_history.insert_one(price_data)
    
    return price_data

@api_router.get("/price/history")
async def get_price_history(days: int = 30):
    """获取历史价格数据"""
    historical_data = data_fetcher.fetch_historical_data(days)
    return {"data": historical_data, "days": days}

@api_router.get("/analysis/technical", response_model=TechnicalIndicators)
async def get_technical_analysis():
    """获取技术指标分析"""
    # 获取历史数据
    historical_data = data_fetcher.fetch_historical_data(60)
    
    # 计算技术指标
    analyzer = TechnicalAnalyzer(historical_data)
    indicators = analyzer.get_all_indicators()
    
    # 保存到数据库
    indicators_record = {
        **indicators,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    await db.technical_indicators.insert_one(indicators_record)
    
    return indicators

@api_router.get("/analysis/ai")
async def get_ai_analysis():
    """获取AI分析结果"""
    news_analysis = await ai_analyzer.analyze_news_sentiment()
    chart_analysis = await ai_analyzer.analyze_chart_pattern()
    sentiment_analysis = await ai_analyzer.analyze_market_sentiment()
    
    result = {
        'news': news_analysis,
        'chart': chart_analysis,
        'sentiment': sentiment_analysis,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    # 保存到数据库
    await db.ai_analysis.insert_one(result)
    
    return result

@api_router.get("/signals/current", response_model=TradingSignal)
async def get_current_signal():
    """获取当前交易信号"""
    # 获取技术指标
    historical_data = data_fetcher.fetch_historical_data(60)
    analyzer = TechnicalAnalyzer(historical_data)
    technical_indicators = analyzer.get_all_indicators()
    
    # 获取AI分析
    ai_analysis = {
        'news': await ai_analyzer.analyze_news_sentiment(),
        'chart': await ai_analyzer.analyze_chart_pattern(),
        'sentiment': await ai_analyzer.analyze_market_sentiment()
    }
    
    # 综合评估
    signal = signal_evaluator.evaluate_signals(technical_indicators, ai_analysis)
    
    # 获取当前价格
    current_price_data = data_fetcher.fetch_real_time_price()
    if current_price_data:
        signal['current_price'] = current_price_data['price']
    
    # 保存到数据库
    signal_record = TradingSignal(**signal)
    await db.trading_signals.insert_one(signal_record.model_dump())
    
    return signal_record

@api_router.get("/signals/history")
async def get_signal_history(limit: int = 50):
    """获取历史交易信号"""
    signals = await db.trading_signals.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"signals": signals, "count": len(signals)}

@api_router.post("/settings")
async def save_user_settings(settings: UserSettings):
    """保存用户设置"""
    # 检查是否已存在
    existing = await db.user_settings.find_one({"email": settings.email})
    
    settings_dict = settings.model_dump()
    
    if existing:
        # 更新
        await db.user_settings.update_one(
            {"email": settings.email},
            {"$set": settings_dict}
        )
    else:
        # 创建
        await db.user_settings.insert_one(settings_dict)
    
    return {"status": "success", "message": "设置已保存"}

@api_router.get("/settings/{email}")
async def get_user_settings(email: str):
    """获取用户设置"""
    settings = await db.user_settings.find_one({"email": email}, {"_id": 0})
    if not settings:
        raise HTTPException(status_code=404, detail="未找到设置")
    return settings

@api_router.get("/dashboard/summary")
async def get_dashboard_summary():
    """获取仪表盘概览数据"""
    # 当前价格
    current_price = data_fetcher.fetch_real_time_price()
    
    # 最新信号
    latest_signal = await db.trading_signals.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
    
    # 统计信息
    total_signals = await db.trading_signals.count_documents({})
    
    return {
        'current_price': current_price,
        'latest_signal': latest_signal,
        'total_signals': total_signals,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()