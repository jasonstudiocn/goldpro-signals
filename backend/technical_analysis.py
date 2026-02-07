import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """技术指标分析器"""
    
    def __init__(self, price_data: List[Dict]):
        """初始化分析器
        
        Args:
            price_data: 包含OHLC数据的列表
        """
        self.df = pd.DataFrame(price_data)
        if not self.df.empty:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df.set_index('timestamp', inplace=True)
    
    def calculate_sma(self, period: int = 20) -> float:
        """计算简单移动平均线"""
        if len(self.df) < period:
            return None
        return float(self.df['close'].rolling(window=period).mean().iloc[-1])
    
    def calculate_ema(self, period: int = 20) -> float:
        """计算指数移动平均线"""
        if len(self.df) < period:
            return None
        return float(self.df['close'].ewm(span=period, adjust=False).mean().iloc[-1])
    
    def calculate_rsi(self, period: int = 14) -> Dict:
        """计算RSI指标"""
        if len(self.df) < period + 1:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}
        
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1])
        
        # 生成信号
        if current_rsi > 70:
            signal = 'SELL'
            confidence = min((current_rsi - 70) / 30 * 100, 100)
        elif current_rsi < 30:
            signal = 'BUY'
            confidence = min((30 - current_rsi) / 30 * 100, 100)
        else:
            signal = 'HOLD'
            confidence = 100 - abs(current_rsi - 50) * 2
        
        return {
            'value': round(current_rsi, 2),
            'signal': signal,
            'confidence': round(confidence, 2)
        }
    
    def calculate_macd(self) -> Dict:
        """计算MACD指标"""
        if len(self.df) < 26:
            return {'macd': None, 'signal_line': None, 'histogram': None, 'signal': 'HOLD', 'confidence': 0}
        
        exp1 = self.df['close'].ewm(span=12, adjust=False).mean()
        exp2 = self.df['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal_line
        
        current_macd = float(macd.iloc[-1])
        current_signal = float(signal_line.iloc[-1])
        current_hist = float(histogram.iloc[-1])
        prev_hist = float(histogram.iloc[-2]) if len(histogram) > 1 else 0
        
        # 生成信号
        if current_hist > 0 and prev_hist <= 0:
            signal = 'BUY'
            confidence = min(abs(current_hist) * 10, 100)
        elif current_hist < 0 and prev_hist >= 0:
            signal = 'SELL'
            confidence = min(abs(current_hist) * 10, 100)
        else:
            signal = 'HOLD'
            confidence = 50
        
        return {
            'macd': round(current_macd, 2),
            'signal_line': round(current_signal, 2),
            'histogram': round(current_hist, 2),
            'signal': signal,
            'confidence': round(confidence, 2)
        }
    
    def calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2) -> Dict:
        """计算布林带"""
        if len(self.df) < period:
            return {'upper': None, 'middle': None, 'lower': None, 'signal': 'HOLD', 'confidence': 0}
        
        sma = self.df['close'].rolling(window=period).mean()
        std = self.df['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = float(self.df['close'].iloc[-1])
        upper = float(upper_band.iloc[-1])
        middle = float(sma.iloc[-1])
        lower = float(lower_band.iloc[-1])
        
        # 生成信号
        if current_price >= upper:
            signal = 'SELL'
            confidence = min((current_price - upper) / (upper - middle) * 100, 100)
        elif current_price <= lower:
            signal = 'BUY'
            confidence = min((lower - current_price) / (middle - lower) * 100, 100)
        else:
            signal = 'HOLD'
            confidence = 50
        
        return {
            'upper': round(upper, 2),
            'middle': round(middle, 2),
            'lower': round(lower, 2),
            'current_price': round(current_price, 2),
            'signal': signal,
            'confidence': round(confidence, 2)
        }
    
    def calculate_atr(self, period: int = 14) -> Dict:
        """计算平均真实波幅"""
        if len(self.df) < period:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}
        
        high_low = self.df['high'] - self.df['low']
        high_close = np.abs(self.df['high'] - self.df['close'].shift())
        low_close = np.abs(self.df['low'] - self.df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(window=period).mean()
        
        current_atr = float(atr.iloc[-1])
        avg_atr = float(atr.mean())
        
        # ATR主要用于波动性判断，不直接产生买卖信号
        if current_atr > avg_atr * 1.5:
            volatility = 'HIGH'
            confidence = 80
        elif current_atr < avg_atr * 0.5:
            volatility = 'LOW'
            confidence = 80
        else:
            volatility = 'NORMAL'
            confidence = 60
        
        return {
            'value': round(current_atr, 2),
            'volatility': volatility,
            'signal': 'HOLD',
            'confidence': round(confidence, 2)
        }
    
    def calculate_stochastic(self, period: int = 14) -> Dict:
        """计算随机震荡指标"""
        if len(self.df) < period:
            return {'k': None, 'd': None, 'signal': 'HOLD', 'confidence': 0}
        
        low_min = self.df['low'].rolling(window=period).min()
        high_max = self.df['high'].rolling(window=period).max()
        
        k_percent = 100 * ((self.df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=3).mean()
        
        current_k = float(k_percent.iloc[-1])
        current_d = float(d_percent.iloc[-1])
        
        # 生成信号
        if current_k > 80 and current_d > 80:
            signal = 'SELL'
            confidence = min((current_k - 80) / 20 * 100, 100)
        elif current_k < 20 and current_d < 20:
            signal = 'BUY'
            confidence = min((20 - current_k) / 20 * 100, 100)
        else:
            signal = 'HOLD'
            confidence = 50
        
        return {
            'k': round(current_k, 2),
            'd': round(current_d, 2),
            'signal': signal,
            'confidence': round(confidence, 2)
        }
    
    def get_all_indicators(self) -> Dict:
        """获取所有技术指标"""
        return {
            'sma_20': self.calculate_sma(20),
            'sma_50': self.calculate_sma(50),
            'ema_20': self.calculate_ema(20),
            'rsi': self.calculate_rsi(),
            'macd': self.calculate_macd(),
            'bollinger': self.calculate_bollinger_bands(),
            'atr': self.calculate_atr(),
            'stochastic': self.calculate_stochastic()
        }