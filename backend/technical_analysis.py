import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """技术指标分析器 - 增强版"""

    def __init__(self, price_data: List[Dict]):
        """初始化分析器

        Args:
            price_data: 包含OHLC数据的列表
        """
        self.df = pd.DataFrame(price_data)
        if not self.df.empty:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df.set_index('timestamp', inplace=True)
            self.df.sort_index(inplace=True)

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

    def calculate_sma_200(self) -> float:
        """计算200日简单移动平均线 - 长期趋势指标"""
        if len(self.df) < 200:
            return None
        return float(self.df['close'].rolling(window=200).mean().iloc[-1])

    def calculate_sma_50(self) -> float:
        """计算50日简单移动平均线"""
        return self.calculate_sma(50)

    def calculate_ema_12(self) -> float:
        """计算12日指数移动平均线"""
        if len(self.df) < 12:
            return None
        return float(self.df['close'].ewm(span=12, adjust=False).mean().iloc[-1])

    def calculate_ema_26(self) -> float:
        """计算26日指数移动平均线"""
        if len(self.df) < 26:
            return None
        return float(self.df['close'].ewm(span=26, adjust=False).mean().iloc[-1])

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

        prev_rsi = float(rsi.iloc[-2]) if len(rsi) > 1 else current_rsi

        if current_rsi > 70:
            signal = 'SELL'
            confidence = min((current_rsi - 70) / 30 * 100, 100)
        elif current_rsi < 30:
            signal = 'BUY'
            confidence = min((30 - current_rsi) / 30 * 100, 100)
        else:
            signal = 'HOLD'
            confidence = 100 - abs(current_rsi - 50) * 2

        rsi_trend = 'rising' if current_rsi > prev_rsi else 'falling' if current_rsi < prev_rsi else 'neutral'

        return {
            'value': round(current_rsi, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'trend': rsi_trend,
            'overbought': current_rsi > 70,
            'oversold': current_rsi < 30
        }

    def calculate_rsi_divergence(self) -> Dict:
        """检测RSI背离"""
        if len(self.df) < 30:
            return {'divergence': None, 'signal': 'HOLD', 'confidence': 0}

        prices = self.df['close'].values
        rsi_values = self.calculate_rsi(14)['value']

        if rsi_values is None:
            return {'divergence': None, 'signal': 'HOLD', 'confidence': 0}

        recent_highs = prices[-14:]
        recent_lows = prices[-14:]

        higher_highs = max(recent_highs[-7:]) > max(recent_highs[:7])
        lower_highs = max(recent_highs[-7:]) < max(recent_highs[:7])

        current_price = prices[-1]
        highest_price = max(prices[-14:])

        if higher_highs and current_price < highest_price * 0.98:
            return {
                'divergence': 'BULLISH',
                'signal': 'BUY',
                'confidence': 75,
                'description': '价格创新低但RSI未创新低，可能出现反转上涨'
            }
        elif lower_highs and current_price > lowest_price * 1.02 if (lowest_price := min(prices[-14:])) else False:
            return {
                'divergence': 'BEARISH',
                'signal': 'SELL',
                'confidence': 75,
                'description': '价格创新高但RSI未创新高，可能出现反转下跌'
            }

        return {'divergence': None, 'signal': 'HOLD', 'confidence': 0, 'description': '未检测到明显背离'}

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

        hist_trend = 'increasing' if current_hist > prev_hist else 'decreasing'

        if current_hist > 0 and prev_hist <= 0:
            signal = 'BUY'
            confidence = min(abs(current_hist) * 10, 100)
        elif current_hist < 0 and prev_hist >= 0:
            signal = 'SELL'
            confidence = min(abs(current_hist) * 10, 100)
        elif current_macd > current_signal:
            signal = 'BUY'
            confidence = 60
        elif current_macd < current_signal:
            signal = 'SELL'
            confidence = 60
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'macd': round(current_macd, 2),
            'signal_line': round(current_signal, 2),
            'histogram': round(current_hist, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'histogram_trend': hist_trend,
            'macd_above_signal': current_macd > current_signal
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

        bandwidth = (upper - lower) / middle * 100
        position = (current_price - lower) / (upper - lower) * 100 if upper != lower else 50

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
            'confidence': round(confidence, 2),
            'bandwidth': round(bandwidth, 2),
            'position': round(position, 2),
            'squeeze': bandwidth < 10
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

        atr_percent = (current_atr / current_price) * 100 if (current_price := float(self.df['close'].iloc[-1])) else 0

        if current_atr > avg_atr * 1.5:
            volatility = 'HIGH'
            confidence = 80
            signal = 'SELL' if current_atr > avg_atr * 2 else 'HOLD'
        elif current_atr < avg_atr * 0.5:
            volatility = 'LOW'
            confidence = 80
            signal = 'BUY' if current_atr < avg_atr * 0.3 else 'HOLD'
        else:
            volatility = 'NORMAL'
            confidence = 60
            signal = 'HOLD'

        return {
            'value': round(current_atr, 2),
            'volatility': volatility,
            'signal': signal,
            'confidence': round(confidence, 2),
            'atr_percent': round(atr_percent, 2),
            'atr_rank': round((current_atr / atr.max()) * 100, 2) if len(atr) > 1 else 50
        }

    def calculate_stochastic(self, period: int = 14, smooth_k: int = 3) -> Dict:
        """计算随机震荡指标"""
        if len(self.df) < period:
            return {'k': None, 'd': None, 'signal': 'HOLD', 'confidence': 0}

        low_min = self.df['low'].rolling(window=period).min()
        high_max = self.df['high'].rolling(window=period).max()

        k_percent = 100 * ((self.df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=smooth_k).mean()

        current_k = float(k_percent.iloc[-1])
        current_d = float(d_percent.iloc[-1])

        if current_k > 80 and current_d > 80:
            signal = 'SELL'
            confidence = min((current_k - 80) / 20 * 100, 100)
        elif current_k < 20 and current_d < 20:
            signal = 'BUY'
            confidence = min((20 - current_k) / 20 * 100, 100)
        elif current_k > current_d and current_k < 80:
            signal = 'BUY'
            confidence = 60
        elif current_k < current_d and current_k > 20:
            signal = 'SELL'
            confidence = 60
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'k': round(current_k, 2),
            'd': round(current_d, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'k_above_d': current_k > current_d
        }

    def calculate_williams_r(self, period: int = 14) -> Dict:
        """计算Williams %R指标"""
        if len(self.df) < period:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}

        high_max = self.df['high'].rolling(window=period).max()
        low_min = self.df['low'].rolling(window=period).min()

        williams_r = -100 * ((high_max - self.df['close']) / (high_max - low_min))

        current_value = float(williams_r.iloc[-1])

        if current_value >= -20:
            signal = 'SELL'
            confidence = min((abs(current_value) - 80) / 20 * 100, 100)
        elif current_value <= -80:
            signal = 'BUY'
            confidence = min((80 - abs(current_value)) / 20 * 100, 100)
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'value': round(current_value, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'overbought': current_value >= -20,
            'oversold': current_value <= -80
        }

    def calculate_cci(self, period: int = 20) -> Dict:
        """计算商品通道指数(CCI)"""
        if len(self.df) < period:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}

        typical_price = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        sma = typical_price.rolling(window=period).mean()
        mean_deviation = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)

        cci = (typical_price - sma) / (0.015 * mean_deviation)

        current_cci = float(cci.iloc[-1])

        if current_cci > 100:
            signal = 'SELL'
            confidence = min((current_cci - 100) / 200 * 100, 100)
        elif current_cci < -100:
            signal = 'BUY'
            confidence = min((abs(current_cci) - 100) / 200 * 100, 100)
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'value': round(current_cci, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'strong_overbought': current_cci > 200,
            'strong_oversold': current_cci < -200
        }

    def calculate_mfi(self, period: int = 14) -> Dict:
        """计算资金流量指数(MFI)"""
        if len(self.df) < period + 1:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}

        typical_price = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        raw_money_flow = typical_price * self.df['volume']

        money_flow_sign = np.where(typical_price > typical_price.shift(1), 1, -1)
        positive_money_flow = raw_money_flow.where(money_flow_sign == 1, 0)
        negative_money_flow = raw_money_flow.where(money_flow_sign == -1, 0)

        positive_mf_sum = positive_money_flow.rolling(window=period).sum()
        negative_mf_sum = negative_money_flow.rolling(window=period).sum()

        money_ratio = positive_mf_sum / negative_mf_sum
        mfi = 100 - (100 / (1 + money_ratio))

        current_mfi = float(mfi.iloc[-1])

        if current_mfi > 80:
            signal = 'SELL'
            confidence = min((current_mfi - 80) / 20 * 100, 100)
        elif current_mfi < 20:
            signal = 'BUY'
            confidence = min((20 - current_mfi) / 20 * 100, 100)
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'value': round(current_mfi, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'overbought': current_mfi > 80,
            'oversold': current_mfi < 20
        }

    def calculate_obv(self) -> Dict:
        """计算能量潮指标(OBV)"""
        if len(self.df) < 2:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}

        obv = [0]
        for i in range(1, len(self.df)):
            if self.df['close'].iloc[i] > self.df['close'].iloc[i-1]:
                obv.append(obv[-1] + self.df['volume'].iloc[i])
            elif self.df['close'].iloc[i] < self.df['close'].iloc[i-1]:
                obv.append(obv[-1] - self.df['volume'].iloc[i])
            else:
                obv.append(obv[-1])

        self.df['obv'] = obv

        obv_ma = self.df['obv'].rolling(window=9).mean()
        current_obv = float(self.df['obv'].iloc[-1])
        obv_ma_value = float(obv_ma.iloc[-1])

        obv_trend = 'rising' if current_obv > obv_ma_value else 'falling' if current_obv < obv_ma_value else 'neutral'

        price_trend = 'rising' if self.df['close'].iloc[-1] > self.df['close'].iloc[-5] else 'falling'

        if obv_trend == 'rising' and price_trend == 'rising':
            signal = 'BUY'
            confidence = 70
        elif obv_trend == 'falling' and price_trend == 'rising':
            signal = 'SELL'
            confidence = 65
        elif obv_trend == 'rising' and price_trend == 'falling':
            signal = 'BUY'
            confidence = 65
        elif obv_trend == 'falling' and price_trend == 'falling':
            signal = 'SELL'
            confidence = 70
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'value': current_obv,
            'ma': obv_ma_value,
            'signal': signal,
            'confidence': round(confidence, 2),
            'trend': obv_trend,
            'divergence': 'positive' if (price_trend == 'rising' and obv_trend == 'falling') else 'negative' if (price_trend == 'falling' and obv_trend == 'rising') else 'none'
        }

    def calculate_adx(self, period: int = 14) -> Dict:
        """计算平均方向指数(ADX)"""
        if len(self.df) < period + 1:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}

        plus_di = 100 * (self.df['high'].diff())
        minus_di = 100 * (-self.df['low'].diff())

        plus_di = plus_di.rolling(window=period).mean()
        minus_di = minus_di.rolling(window=period).mean()

        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        current_adx = float(adx.iloc[-1])
        current_plus_di = float(plus_di.iloc[-1])
        current_minus_di = float(minus_di.iloc[-1])

        if current_adx > 25:
            trend_strength = 'STRONG'
        elif current_adx > 20:
            trend_strength = 'MODERATE'
        else:
            trend_strength = 'WEAK'

        if current_plus_di > current_minus_di:
            trend_direction = 'BULLISH'
            signal = 'BUY'
        elif current_minus_di > current_plus_di:
            trend_direction = 'BEARISH'
            signal = 'SELL'
        else:
            trend_direction = 'NEUTRAL'
            signal = 'HOLD'

        confidence = min(current_adx, 100)

        return {
            'adx': round(current_adx, 2),
            'plus_di': round(current_plus_di, 2),
            'minus_di': round(current_minus_di, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'trend_strength': trend_strength,
            'trend_direction': trend_direction
        }

    def calculate_roc(self, period: int = 10) -> Dict:
        """计算变动率(ROC)"""
        if len(self.df) < period:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}

        roc = ((self.df['close'] - self.df['close'].shift(period)) / self.df['close'].shift(period)) * 100

        current_roc = float(roc.iloc[-1])

        if current_roc > 5:
            signal = 'BUY'
            confidence = min(current_roc * 10, 100)
        elif current_roc < -5:
            signal = 'SELL'
            confidence = min(abs(current_roc) * 10, 100)
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'value': round(current_roc, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'momentum': 'strong' if abs(current_roc) > 10 else 'moderate' if abs(current_roc) > 5 else 'weak'
        }

    def calculate_momentum(self, period: int = 10) -> Dict:
        """计算动量指标"""
        if len(self.df) < period:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}

        momentum = self.df['close'] - self.df['close'].shift(period)

        current_momentum = float(momentum.iloc[-1])
        avg_momentum = float(momentum.mean())

        if current_momentum > 50:
            signal = 'BUY'
            confidence = min((current_momentum - 50) / 2, 100)
        elif current_momentum < -50:
            signal = 'SELL'
            confidence = min((abs(current_momentum) - 50) / 2, 100)
        elif current_momentum > avg_momentum * 1.5:
            signal = 'BUY'
            confidence = 70
        elif current_momentum < avg_momentum * 0.5:
            signal = 'SELL'
            confidence = 70
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'value': round(current_momentum, 2),
            'average': round(avg_momentum, 2),
            'signal': signal,
            'confidence': round(confidence, 2)
        }

    def calculate_fibonacci_retracement(self) -> Dict:
        """计算斐波那契回撤位"""
        if len(self.df) < 2:
            return {'levels': None, 'signal': 'HOLD', 'confidence': 0}

        high_price = self.df['high'].max()
        low_price = self.df['low'].min()

        diff = high_price - low_price

        fib_levels = {
            '0%': round(high_price, 2),
            '23.6%': round(high_price - 0.236 * diff, 2),
            '38.2%': round(high_price - 0.382 * diff, 2),
            '50%': round(high_price - 0.5 * diff, 2),
            '61.8%': round(high_price - 0.618 * diff, 2),
            '78.6%': round(high_price - 0.786 * diff, 2),
            '100%': round(low_price, 2)
        }

        current_price = float(self.df['close'].iloc[-1])

        nearest_support = None
        nearest_resistance = None

        for level, price in fib_levels.items():
            if price < current_price:
                nearest_support = {'level': level, 'price': price}
            elif price > current_price and nearest_resistance is None:
                nearest_resistance = {'level': level, 'price': price}
                break

        return {
            'levels': fib_levels,
            'current_price': current_price,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'signal': 'HOLD',
            'confidence': 50
        }

    def calculate_pivot_points(self) -> Dict:
        """计算枢轴点"""
        if len(self.df) < 1:
            return {'pivot': None, 'signal': 'HOLD', 'confidence': 0}

        prev_high = float(self.df['high'].iloc[-1])
        prev_low = float(self.df['low'].iloc[-1])
        prev_close = float(self.df['close'].iloc[-1])

        pivot = (prev_high + prev_low + prev_close) / 3

        r1 = 2 * pivot - prev_low
        r2 = pivot + (prev_high - prev_low)
        r3 = prev_high + 2 * (pivot - prev_low)

        s1 = 2 * pivot - prev_high
        s2 = pivot - (prev_high - prev_low)
        s3 = prev_low - 2 * (prev_high - pivot)

        current_price = prev_close

        if current_price > r1:
            signal = 'BUY'
            confidence = 70
        elif current_price < s1:
            signal = 'SELL'
            confidence = 70
        elif current_price > pivot:
            signal = 'BUY'
            confidence = 55
        elif current_price < pivot:
            signal = 'SELL'
            confidence = 55
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'pivot': round(pivot, 2),
            'r1': round(r1, 2),
            'r2': round(r2, 2),
            'r3': round(r3, 2),
            's1': round(s1, 2),
            's2': round(s2, 2),
            's3': round(s3, 2),
            'current_price': current_price,
            'signal': signal,
            'confidence': round(confidence, 2)
        }

    def calculate_vwap(self) -> Dict:
        """计算成交量加权平均价格(VWAP)"""
        if len(self.df) < 1:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}

        typical_price = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        vwap = (typical_price * self.df['volume']).cumsum() / self.df['volume'].cumsum()

        current_vwap = float(vwap.iloc[-1])
        current_price = float(self.df['close'].iloc[-1])

        if current_price > current_vwap:
            signal = 'BUY'
            confidence = min((current_price - current_vwap) / current_vwap * 100 * 10, 100)
        elif current_price < current_vwap:
            signal = 'SELL'
            confidence = min((current_vwap - current_price) / current_vwap * 100 * 10, 100)
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'value': round(current_vwap, 2),
            'current_price': current_price,
            'signal': signal,
            'confidence': round(confidence, 2),
            'above_vwap': current_price > current_vwap
        }

    def calculate_donchian_channels(self, period: int = 20) -> Dict:
        """计算唐奇安通道"""
        if len(self.df) < period:
            return {'upper': None, 'middle': None, 'lower': None, 'signal': 'HOLD', 'confidence': 0}

        upper = self.df['high'].rolling(window=period).max()
        lower = self.df['low'].rolling(window=period).min()
        middle = (upper + lower) / 2

        current_price = float(self.df['close'].iloc[-1])
        current_upper = float(upper.iloc[-1])
        current_lower = float(lower.iloc[-1])

        if current_price >= current_upper:
            signal = 'BUY'
            confidence = 80
        elif current_price <= current_lower:
            signal = 'SELL'
            confidence = 80
        else:
            signal = 'HOLD'
            confidence = 50

        channel_width = current_upper - current_lower

        return {
            'upper': round(current_upper, 2),
            'middle': round(float(middle.iloc[-1]), 2),
            'lower': round(current_lower, 2),
            'width': round(channel_width, 2),
            'signal': signal,
            'confidence': round(confidence, 2)
        }

    def calculate_parabolic_sar(self, af: float = 0.02, max_af: float = 0.2) -> Dict:
        """计算抛物线SAR"""
        if len(self.df) < 2:
            return {'value': None, 'signal': 'HOLD', 'confidence': 0}

        high = self.df['high'].values
        low = self.df['low'].values
        close = self.df['close'].values

        sar = np.zeros(len(close))
        trend = np.zeros(len(close))
        ep = np.zeros(len(close))
        af_array = np.zeros(len(close))

        sar[0] = low[0]
        trend[0] = 1
        ep[0] = high[0]
        af_array[0] = af

        for i in range(1, len(close)):
            if trend[i-1] == 1:
                sar[i] = sar[i-1] + af_array[i-1] * (ep[i-1] - sar[i-1])
                if high[i] > ep[i-1]:
                    ep[i] = high[i]
                    af_array[i] = min(af_array[i-1] + af, max_af)
                    trend[i] = 1
                else:
                    ep[i] = ep[i-1]
                    af_array[i] = af_array[i-1]
                    trend[i] = 1
                if sar[i] > low[i]:
                    trend[i] = -1
                    sar[i] = high[i-1]
                    ep[i] = low[i]
                    af_array[i] = af
            else:
                sar[i] = sar[i-1] + af_array[i-1] * (ep[i-1] - sar[i-1])
                if low[i] < ep[i-1]:
                    ep[i] = low[i]
                    af_array[i] = min(af_array[i-1] + af, max_af)
                    trend[i] = -1
                else:
                    ep[i] = ep[i-1]
                    af_array[i] = af_array[i-1]
                    trend[i] = -1
                if sar[i] < high[i]:
                    trend[i] = 1
                    sar[i] = low[i-1]
                    ep[i] = high[i]
                    af_array[i] = af

        current_sar = float(sar[-1])
        current_price = close[-1]
        current_trend = 'BULLISH' if trend[-1] == 1 else 'BEARISH'

        if trend[-1] == 1 and current_price > current_sar:
            signal = 'BUY'
            confidence = 75
        elif trend[-1] == -1 and current_price < current_sar:
            signal = 'SELL'
            confidence = 75
        elif trend[-1] == 1 and current_price < current_sar:
            signal = 'SELL'
            confidence = 70
        elif trend[-1] == -1 and current_price > current_sar:
            signal = 'BUY'
            confidence = 70
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'value': round(current_sar, 2),
            'current_price': round(current_price, 2),
            'trend': current_trend,
            'signal': signal,
            'confidence': round(confidence, 2)
        }

    def calculate_volume_analysis(self) -> Dict:
        """成交量分析"""
        if len(self.df) < 10:
            return {'volume': None, 'signal': 'HOLD', 'confidence': 0}

        current_volume = int(self.df['volume'].iloc[-1])
        avg_volume = int(self.df['volume'].rolling(window=20).mean().iloc[-1])
        volume_ma5 = int(self.df['volume'].rolling(window=5).mean().iloc[-1])

        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

        price_change = self.df['close'].iloc[-1] - self.df['close'].iloc[-2]
        price_change_pct = (price_change / self.df['close'].iloc[-2]) * 100

        if volume_ratio > 2 and price_change > 0:
            signal = 'STRONG_BUY'
            confidence = 85
        elif volume_ratio > 2 and price_change < 0:
            signal = 'STRONG_SELL'
            confidence = 85
        elif volume_ratio > 1.5 and price_change > 0:
            signal = 'BUY'
            confidence = 70
        elif volume_ratio > 1.5 and price_change < 0:
            signal = 'SELL'
            confidence = 70
        elif volume_ratio < 0.5:
            signal = 'HOLD'
            confidence = 60
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'current_volume': current_volume,
            'average_volume': avg_volume,
            'volume_ratio': round(volume_ratio, 2),
            'volume_ma5': volume_ma5,
            'price_change_pct': round(price_change_pct, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'high_volume': volume_ratio > 1.5,
            'low_volume': volume_ratio < 0.7
        }

    def detect_golden_cross_death_cross(self) -> Dict:
        """检测金叉和死叉"""
        if len(self.df) < 50:
            return {'cross': None, 'signal': 'HOLD', 'confidence': 0}

        sma_50 = self.df['close'].rolling(window=50).mean()
        sma_200 = self.df['close'].rolling(window=200).mean()

        if len(sma_50) < 2 or len(sma_200) < 2:
            return {'cross': None, 'signal': 'HOLD', 'confidence': 0}

        prev_50 = float(sma_50.iloc[-2])
        prev_200 = float(sma_200.iloc[-2])
        curr_50 = float(sma_50.iloc[-1])
        curr_200 = float(sma_200.iloc[-1])

        if prev_50 <= prev_200 and curr_50 > curr_200:
            return {
                'cross': 'GOLDEN_CROSS',
                'signal': 'BUY',
                'confidence': 85,
                'description': '50日均线向上突破200日均线，看涨信号'
            }
        elif prev_50 >= prev_200 and curr_50 < curr_200:
            return {
                'cross': 'DEATH_CROSS',
                'signal': 'SELL',
                'confidence': 85,
                'description': '50日均线向下突破200日均线，看跌信号'
            }
        elif curr_50 > curr_200:
            return {
                'cross': 'BULLISH_ABOVE',
                'signal': 'BUY',
                'confidence': 60,
                'description': '50日均线在200日均线上方，牛市格局'
            }
        elif curr_50 < curr_200:
            return {
                'cross': 'BEARISH_BELOW',
                'signal': 'SELL',
                'confidence': 60,
                'description': '50日均线在200日均线下方，熊市格局'
            }

        return {'cross': None, 'signal': 'HOLD', 'confidence': 50}

    def calculate_ichimoku_cloud(self) -> Dict:
        """计算一目均衡表(Ichimoku Cloud) - 简化版"""
        if len(self.df) < 52:
            return {'tenkan': None, 'kijun': None, 'senkou_a': None, 'senkou_b': None, 'signal': 'HOLD', 'confidence': 0}

        high_9 = self.df['high'].rolling(window=9).max()
        low_9 = self.df['low'].rolling(window=9).min()
        tenkan_sen = (high_9 + low_9) / 2

        high_26 = self.df['high'].rolling(window=26).max()
        low_26 = self.df['low'].rolling(window=26).min()
        kijun_sen = (high_26 + low_26) / 2

        high_52 = self.df['high'].rolling(window=52).max()
        low_52 = self.df['low'].rolling(window=52).min()
        senkou_span_b = (high_52 + low_52) / 2

        senkou_span_a = (tenkan_sen + kijun_sen) / 2

        current_tenkan = float(tenkan_sen.iloc[-1])
        current_kijun = float(kijun_sen.iloc[-1])
        current_senkou_a = float(senkou_span_a.iloc[-26]) if len(senkou_span_a) > 26 and not np.isnan(senkou_span_a.iloc[-26]) else None
        current_senkou_b = float(senkou_span_b.iloc[-26]) if len(senkou_span_b) > 26 and not np.isnan(senkou_span_b.iloc[-26]) else None

        current_price = float(self.df['close'].iloc[-1])

        if current_senkou_a is None or current_senkou_b is None:
            return {
                'tenkan': round(current_tenkan, 2),
                'kijun': round(current_kijun, 2),
                'senkou_a': None,
                'senkou_b': None,
                'signal': 'HOLD',
                'confidence': 0,
                'description': '数据不足，无法计算完整云图'
            }

        cloud_bullish = current_senkou_a > current_senkou_b
        price_above_cloud = current_price > max(current_senkou_a, current_senkou_b)

        if current_tenkan > current_kijun and cloud_bullish and price_above_cloud:
            signal = 'STRONG_BUY'
            confidence = 85
        elif current_tenkan < current_kijun and not cloud_bullish and current_price < min(current_senkou_a, current_senkou_b):
            signal = 'STRONG_SELL'
            confidence = 85
        elif current_tenkan > current_kijun:
            signal = 'BUY'
            confidence = 65
        elif current_tenkan < current_kijun:
            signal = 'SELL'
            confidence = 65
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'tenkan': round(current_tenkan, 2),
            'kijun': round(current_kijun, 2),
            'senkou_a': round(current_senkou_a, 2),
            'senkou_b': round(current_senkou_b, 2),
            'signal': signal,
            'confidence': round(confidence, 2),
            'cloud_bullish': cloud_bullish,
            'price_above_cloud': price_above_cloud
        }

    def calculate_support_resistance(self) -> Dict:
        """计算支撑和阻力位"""
        if len(self.df) < 20:
            return {'support': None, 'resistance': None, 'signal': 'HOLD', 'confidence': 0}

        prices = self.df['close'].values

        support_levels = []
        resistance_levels = []

        for i in range(20, len(prices)):
            window = prices[max(0, i-20):i+1]
            local_min = min(window)
            local_max = max(window)

            if prices[i] == local_min:
                support_levels.append(local_min)
            if prices[i] == local_max:
                resistance_levels.append(local_max)

        current_price = prices[-1]

        support_levels = sorted(list(set(support_levels)))[:5]
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:5]

        nearest_support = None
        for support in sorted(support_levels, reverse=True):
            if support < current_price:
                nearest_support = support
                break

        nearest_resistance = None
        for resistance in sorted(resistance_levels):
            if resistance > current_price:
                nearest_resistance = resistance
                break

        return {
            'support_levels': [round(s, 2) for s in support_levels],
            'resistance_levels': [round(r, 2) for r in resistance_levels],
            'nearest_support': round(nearest_support, 2) if nearest_support else None,
            'nearest_resistance': round(nearest_resistance, 2) if nearest_resistance else None,
            'current_price': round(current_price, 2),
            'signal': 'HOLD',
            'confidence': 50
        }

    def get_all_indicators(self) -> Dict:
        """获取所有技术指标"""
        return {
            'sma_20': self.calculate_sma(20),
            'sma_50': self.calculate_sma(50),
            'sma_200': self.calculate_sma_200(),
            'ema_20': self.calculate_ema(20),
            'ema_12': self.calculate_ema_12(),
            'ema_26': self.calculate_ema_26(),
            'rsi': self.calculate_rsi(),
            'rsi_divergence': self.calculate_rsi_divergence(),
            'macd': self.calculate_macd(),
            'bollinger': self.calculate_bollinger_bands(),
            'atr': self.calculate_atr(),
            'stochastic': self.calculate_stochastic(),
            'williams_r': self.calculate_williams_r(),
            'cci': self.calculate_cci(),
            'mfi': self.calculate_mfi(),
            'obv': self.calculate_obv(),
            'adx': self.calculate_adx(),
            'roc': self.calculate_roc(),
            'momentum': self.calculate_momentum(),
            'fibonacci': self.calculate_fibonacci_retracement(),
            'pivot_points': self.calculate_pivot_points(),
            'vwap': self.calculate_vwap(),
            'donchian': self.calculate_donchian_channels(),
            'parabolic_sar': self.calculate_parabolic_sar(),
            'volume': self.calculate_volume_analysis(),
            'cross_signals': self.detect_golden_cross_death_cross(),
            'ichimoku': self.calculate_ichimoku_cloud(),
            'support_resistance': self.calculate_support_resistance()
        }
