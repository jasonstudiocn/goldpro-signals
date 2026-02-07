from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
import os
import logging
from typing import Dict, Optional
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI驱动的市场分析"""
    
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            logger.warning("未找到EMERGENT_LLM_KEY，AI分析功能将不可用")
    
    async def analyze_news_sentiment(self, news_text: str = None) -> Dict:
        """分析新闻情绪"""
        if not self.api_key:
            return {'sentiment': 'NEUTRAL', 'confidence': 0, 'summary': '未配置API密钥'}
        
        try:
            # 模拟新闻数据（实际应该从新闻API获取）
            if not news_text:
                news_text = """近期金融市场新闻:
                1. 美联储维持利率不变，市场预期未来可能降息
                2. 美元指数小幅下跌，黄金获得支撑
                3. 地缘政治紧张局势升温，避险情绪上升
                4. 全球通胀数据显示价格压力持续
                """
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"news_analysis_{datetime.now().timestamp()}",
                system_message="你是专业的金融市场分析师，专注于黄金市场。分析新闻对黄金价格的影响。"
            ).with_model("openai", "gpt-5.2")
            
            prompt = f"""分析以下新闻对黄金价格的影响：

{news_text}

请提供:
1. 整体情绪（BULLISH/BEARISH/NEUTRAL）
2. 影响信心度（0-100）
3. 简短总结（50字以内）

请以JSON格式回复：{"sentiment": "BULLISH/BEARISH/NEUTRAL", "confidence": 数字, "summary": "总结"}"""
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            # 解析响应
            import json
            try:
                result = json.loads(response)
                return result
            except:
                # 如果无法解析JSON，返回默认值
                return {
                    'sentiment': 'NEUTRAL',
                    'confidence': 50,
                    'summary': response[:100] if response else '分析完成'
                }
        
        except Exception as e:
            logger.error(f"新闻情绪分析失败: {e}")
            return {'sentiment': 'NEUTRAL', 'confidence': 0, 'summary': f'分析失败: {str(e)}'}
    
    async def analyze_chart_pattern(self, chart_image_base64: str = None) -> Dict:
        """分析K线图形态"""
        if not self.api_key:
            return {'pattern': 'UNKNOWN', 'signal': 'HOLD', 'confidence': 0, 'description': '未配置API密钥'}
        
        try:
            # 如果没有提供图像，返回模拟结果
            if not chart_image_base64:
                return {
                    'pattern': 'ASCENDING_TRIANGLE',
                    'signal': 'BUY',
                    'confidence': 75,
                    'description': '检测到上升三角形态，可能突破上行'
                }
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"chart_analysis_{datetime.now().timestamp()}",
                system_message="你是技术分析专家，擅长识别K线图形态。"
            ).with_model("openai", "gpt-5.2")
            
            image_content = ImageContent(image_base64=chart_image_base64)
            
            prompt = """分析这个黄金K线图，识别：
1. 图形形态（如头肩顶、双底、三角形等）
2. 买卖信号（BUY/SELL/HOLD）
3. 信心度（0-100）
4. 简短描述（50字以内）

请以JSON格式回复：{"pattern": "形态名称", "signal": "BUY/SELL/HOLD", "confidence": 数字, "description": "描述"}"""
            
            response = await chat.send_message(UserMessage(
                text=prompt,
                file_contents=[image_content]
            ))
            
            import json
            try:
                result = json.loads(response)
                return result
            except:
                return {
                    'pattern': 'UNKNOWN',
                    'signal': 'HOLD',
                    'confidence': 50,
                    'description': response[:100] if response else '分析完成'
                }
        
        except Exception as e:
            logger.error(f"图表形态分析失败: {e}")
            return {'pattern': 'UNKNOWN', 'signal': 'HOLD', 'confidence': 0, 'description': f'分析失败: {str(e)}'}
    
    async def analyze_market_sentiment(self) -> Dict:
        """综合市场情绪分析"""
        if not self.api_key:
            return {'sentiment': 'NEUTRAL', 'confidence': 0, 'factors': []}
        
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"sentiment_analysis_{datetime.now().timestamp()}",
                system_message="你是市场情绪分析专家。"
            ).with_model("openai", "gpt-5.2")
            
            prompt = """基于当前黄金市场状况，分析整体市场情绪：
考虑因素：
- VIX恐慌指数
- 美元指数走势
- 避险情绪
- 社交媒体舆论

请以JSON格式回复：{"sentiment": "BULLISH/BEARISH/NEUTRAL", "confidence": 数字, "factors": ["因素1", "因素2"]}"""
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            import json
            try:
                result = json.loads(response)
                return result
            except:
                return {
                    'sentiment': 'NEUTRAL',
                    'confidence': 50,
                    'factors': ['无法解析分析结果']
                }
        
        except Exception as e:
            logger.error(f"市场情绪分析失败: {e}")
            return {'sentiment': 'NEUTRAL', 'confidence': 0, 'factors': [f'分析失败: {str(e)}']}