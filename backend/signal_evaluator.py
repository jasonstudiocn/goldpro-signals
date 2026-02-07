from typing import Dict, List
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SignalEvaluator:
    """交易信号综合评估器"""
    
    def __init__(self):
        self.signal_weights = {
            'rsi': 0.15,
            'macd': 0.15,
            'bollinger': 0.15,
            'stochastic': 0.10,
            'ai_news': 0.20,
            'ai_chart': 0.15,
            'ai_sentiment': 0.10
        }
    
    def evaluate_signals(self, technical_indicators: Dict, ai_analysis: Dict = None) -> Dict:
        """综合评估所有信号
        
        Args:
            technical_indicators: 技术指标分析结果
            ai_analysis: AI分析结果（可选）
        
        Returns:
            综合评估结果，包含最终信号和信心度
        """
        buy_score = 0
        sell_score = 0
        total_weight = 0
        
        signals_detail = []
        
        # 评估RSI信号
        if technical_indicators.get('rsi') and technical_indicators['rsi'].get('signal'):
            rsi = technical_indicators['rsi']
            weight = self.signal_weights['rsi']
            confidence = rsi.get('confidence', 0) / 100
            
            if rsi['signal'] == 'BUY':
                buy_score += weight * confidence
            elif rsi['signal'] == 'SELL':
                sell_score += weight * confidence
            
            total_weight += weight
            signals_detail.append({
                'indicator': 'RSI',
                'signal': rsi['signal'],
                'confidence': rsi.get('confidence', 0),
                'value': rsi.get('value')
            })
        
        # 评估MACD信号
        if technical_indicators.get('macd') and technical_indicators['macd'].get('signal'):
            macd = technical_indicators['macd']
            weight = self.signal_weights['macd']
            confidence = macd.get('confidence', 0) / 100
            
            if macd['signal'] == 'BUY':
                buy_score += weight * confidence
            elif macd['signal'] == 'SELL':
                sell_score += weight * confidence
            
            total_weight += weight
            signals_detail.append({
                'indicator': 'MACD',
                'signal': macd['signal'],
                'confidence': macd.get('confidence', 0),
                'histogram': macd.get('histogram')
            })
        
        # 评估布林带信号
        if technical_indicators.get('bollinger') and technical_indicators['bollinger'].get('signal'):
            bb = technical_indicators['bollinger']
            weight = self.signal_weights['bollinger']
            confidence = bb.get('confidence', 0) / 100
            
            if bb['signal'] == 'BUY':
                buy_score += weight * confidence
            elif bb['signal'] == 'SELL':
                sell_score += weight * confidence
            
            total_weight += weight
            signals_detail.append({
                'indicator': 'Bollinger Bands',
                'signal': bb['signal'],
                'confidence': bb.get('confidence', 0)
            })
        
        # 评估随机震荡指标
        if technical_indicators.get('stochastic') and technical_indicators['stochastic'].get('signal'):
            stoch = technical_indicators['stochastic']
            weight = self.signal_weights['stochastic']
            confidence = stoch.get('confidence', 0) / 100
            
            if stoch['signal'] == 'BUY':
                buy_score += weight * confidence
            elif stoch['signal'] == 'SELL':
                sell_score += weight * confidence
            
            total_weight += weight
            signals_detail.append({
                'indicator': 'Stochastic',
                'signal': stoch['signal'],
                'confidence': stoch.get('confidence', 0)
            })
        
        # 评估AI分析结果
        if ai_analysis:
            # 新闻情绪
            if ai_analysis.get('news'):
                news = ai_analysis['news']
                weight = self.signal_weights['ai_news']
                confidence = news.get('confidence', 0) / 100
                
                if news.get('sentiment') == 'BULLISH':
                    buy_score += weight * confidence
                elif news.get('sentiment') == 'BEARISH':
                    sell_score += weight * confidence
                
                total_weight += weight
                signals_detail.append({
                    'indicator': 'AI新闻分析',
                    'signal': 'BUY' if news.get('sentiment') == 'BULLISH' else 'SELL' if news.get('sentiment') == 'BEARISH' else 'HOLD',
                    'confidence': news.get('confidence', 0),
                    'summary': news.get('summary', '')
                })
            
            # 图表形态
            if ai_analysis.get('chart'):
                chart = ai_analysis['chart']
                weight = self.signal_weights['ai_chart']
                confidence = chart.get('confidence', 0) / 100
                
                if chart.get('signal') == 'BUY':
                    buy_score += weight * confidence
                elif chart.get('signal') == 'SELL':
                    sell_score += weight * confidence
                
                total_weight += weight
                signals_detail.append({
                    'indicator': 'AI图表分析',
                    'signal': chart.get('signal', 'HOLD'),
                    'confidence': chart.get('confidence', 0),
                    'pattern': chart.get('pattern', '')
                })
            
            # 市场情绪
            if ai_analysis.get('sentiment'):
                sentiment = ai_analysis['sentiment']
                weight = self.signal_weights['ai_sentiment']
                confidence = sentiment.get('confidence', 0) / 100
                
                if sentiment.get('sentiment') == 'BULLISH':
                    buy_score += weight * confidence
                elif sentiment.get('sentiment') == 'BEARISH':
                    sell_score += weight * confidence
                
                total_weight += weight
                signals_detail.append({
                    'indicator': 'AI情绪分析',
                    'signal': 'BUY' if sentiment.get('sentiment') == 'BULLISH' else 'SELL' if sentiment.get('sentiment') == 'BEARISH' else 'HOLD',
                    'confidence': sentiment.get('confidence', 0)
                })
        
        # 计算最终信号
        if total_weight > 0:
            normalized_buy = (buy_score / total_weight) * 100
            normalized_sell = (sell_score / total_weight) * 100
        else:
            normalized_buy = 0
            normalized_sell = 0
        
        # 确定最终信号
        if normalized_buy > normalized_sell and normalized_buy > 60:
            final_signal = 'BUY'
            final_confidence = normalized_buy
        elif normalized_sell > normalized_buy and normalized_sell > 60:
            final_signal = 'SELL'
            final_confidence = normalized_sell
        else:
            final_signal = 'HOLD'
            final_confidence = max(normalized_buy, normalized_sell)
        
        return {
            'signal': final_signal,
            'confidence': round(final_confidence, 2),
            'buy_score': round(normalized_buy, 2),
            'sell_score': round(normalized_sell, 2),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'signals_detail': signals_detail,
            'recommendation': self._get_recommendation(final_signal, final_confidence)
        }
    
    def _get_recommendation(self, signal: str, confidence: float) -> str:
        """生成交易建议"""
        if signal == 'BUY' and confidence >= 80:
            return "强烈建议买入，多个指标高度一致"
        elif signal == 'BUY' and confidence >= 60:
            return "建议买入，指标显示上涨趋势"
        elif signal == 'SELL' and confidence >= 80:
            return "强烈建议卖出，多个指标高度一致"
        elif signal == 'SELL' and confidence >= 60:
            return "建议卖出，指标显示下跌趋势"
        else:
            return "建议观望，等待更明确信号"