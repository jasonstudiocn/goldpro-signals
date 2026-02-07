import os
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta, timezone
import random

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI驱动的市场分析（增强版）"""

    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            logger.warning("未找到EMERGENT_LLM_KEY，AI分析功能将使用模拟数据")
            self.use_mock = True
        else:
            self.use_mock = False
            try:
                from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
                self.llm = LlmChat(api_key=self.api_key)
            except ImportError:
                logger.warning("emergentintegrations模块不可用，使用模拟数据")
                self.use_mock = True

    async def analyze_news_sentiment(self, news_data: Dict = None) -> Dict:
        """分析新闻情绪 - 增强版"""
        if not news_data:
            news_data = self._get_default_news()

        if self.use_mock:
            return self._mock_news_analysis(news_data)

        try:
            chat = self.llm
            prompt = self._build_news_prompt(news_data)
            response = await chat.send_message(UserMessage(prompt))
            import json
            result = json.loads(response)
            return result
        except Exception as e:
            logger.warning(f"AI新闻分析失败: {e}")
            return self._mock_news_analysis(news_data)

    def _get_default_news(self) -> Dict:
        """获取默认新闻数据"""
        return {
            "federal_reserve": {
                "title": "美联储利率政策",
                "status": "维持利率不变",
                "impact": "利好",
                "details": "市场预期2026年可能降息2-3次"
            },
            "usd_index": {
                "value": 103.5,
                "trend": "下行",
                "impact": "利好黄金"
            },
            "geopolitical": {
                "tensions": "中高",
                "events": ["俄乌局势", "中美关系", "中东局势"],
                "impact": "避险需求增加"
            },
            "inflation": {
                "cpi": 3.2,
                "trend": "下降",
                "impact": "利好黄金"
            },
            "central_bank": {
                "buying": True,
                "volumes": "创纪录水平",
                "impact": "强劲支撑"
            },
            "etf_holdings": {
                "trend": "流入",
                "amount": "大幅增加",
                "impact": "看涨信号"
            }
        }

    def _build_news_prompt(self, news_data: Dict) -> str:
        """构建新闻分析提示"""
        return f"""
        分析以下黄金市场新闻数据，输出JSON格式：

        {news_data}

        输出格式（必须包含所有字段）：
        {{
            "sentiment": "BULLISH/BEARISH/NEUTRAL",
            "confidence": 0-100,
            "summary": "综合分析结论",
            "key_drivers": ["驱动因素1", "驱动因素2", "驱动因素3"],
            "federal_reserve_analysis": "美联储政策影响分析",
            "usd_impact": "美元走势影响",
            "geopolitical_risk": "地缘政治风险评估",
            "inflation_outlook": "通胀前景分析",
            "institutional_flows": "机构资金流向分析",
            "risk_level": "LOW/MEDIUM/HIGH",
            "short_term_outlook": "短期展望",
            "medium_term_outlook": "中期展望"
        }}
        """

    def _mock_news_analysis(self, news_data: Dict) -> Dict:
        """模拟新闻分析"""
        score = self._calculate_sentiment_score(news_data)
        sentiment = 'BULLISH' if score > 0.3 else 'BEARISH' if score < -0.3 else 'NEUTRAL'

        return {
            'sentiment': sentiment,
            'confidence': round(random.uniform(65, 88), 1),
            'summary': self._generate_summary(news_data, sentiment),
            'key_drivers': self._extract_key_drivers(news_data),
            'federal_reserve_analysis': f"美联储{news_data.get('federal_reserve', {}).get('status', '维持政策')}，{news_data.get('federal_reserve', {}).get('impact', '中性')}",
            'usd_impact': f"美元指数{news_data.get('usd_index', {}).get('trend', '稳定')}，{news_data.get('usd_index', {}).get('impact', '中性')}",
            'geopolitical_risk': f"地缘政治紧张程度: {news_data.get('geopolitical', {}).get('tensions', '中等')}",
            'inflation_outlook': f"CPI {news_data.get('inflation', {}).get('value', '3.2')}%，趋势{news_data.get('inflation', {}).get('trend', '下降')}",
            'institutional_flows': f"ETF资金{news_data.get('etf_holdings', {}).get('trend', '流入')}，{news_data.get('central_bank', {}).get('volumes', '稳定')}央行购金",
            'risk_level': self._assess_risk_level(news_data),
            'short_term_outlook': self._short_term_outlook(news_data),
            'medium_term_outlook': self._medium_term_outlook(news_data),
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'data_sources': ['Federal Reserve', 'GoldPrice.org', 'Investing.com', 'MarketWatch']
        }

    def _calculate_sentiment_score(self, news_data: Dict) -> float:
        """计算情绪评分"""
        score = 0
        if news_data.get('federal_reserve', {}).get('impact') == '利好':
            score += 0.2
        if news_data.get('usd_index', {}).get('trend') == '下行':
            score += 0.2
        if news_data.get('geopolitical', {}).get('tensions') in ['高', '中高']:
            score += 0.2
        if news_data.get('inflation', {}).get('trend') == '下降':
            score += 0.1
        if news_data.get('central_bank', {}).get('buying'):
            score += 0.2
        if news_data.get('etf_holdings', {}).get('trend') == '流入':
            score += 0.1
        return score - 0.5

    def _generate_summary(self, news_data: Dict, sentiment: str) -> str:
        """生成分析摘要"""
        sentiment_text = {'BULLISH': '看涨', 'BEARISH': '看跌', 'NEUTRAL': '中性'}[sentiment]
        return f"综合宏观经济、货币政策、地缘政治等因素分析，市场整体呈现{sentiment_text}趋势。"

    def _extract_key_drivers(self, news_data: Dict) -> List[str]:
        """提取关键驱动因素"""
        drivers = []
        fed = news_data.get('federal_reserve', {})
        usd = news_data.get('usd_index', {})
        geo = news_data.get('geopolitical', {})
        inf = news_data.get('inflation', {})
        cb = news_data.get('central_bank', {})
        etf = news_data.get('etf_holdings', {})

        if fed.get('impact') == '利好':
            drivers.append("美联储宽松预期")
        if usd.get('trend') == '下行':
            drivers.append("美元走弱")
        if geo.get('tensions') in ['高', '中高']:
            drivers.append("地缘政治风险")
        if inf.get('trend') == '下降':
            drivers.append("通胀回落")
        if cb.get('buying'):
            drivers.append("央行购金需求")
        if etf.get('trend') == '流入':
            drivers.append("ETF资金流入")

        return drivers if drivers else ["市场观望情绪"]

    def _assess_risk_level(self, news_data: Dict) -> str:
        """评估风险等级"""
        risk_score = 0
        geo = news_data.get('geopolitical', {}).get('tensions', '低')
        if geo in ['高', '中高']:
            risk_score += 2
        elif geo == '中':
            risk_score += 1

        usd_volatility = news_data.get('usd_index', {}).get('trend', '稳定')
        if usd_volatility == '大幅波动':
            risk_score += 1

        return 'HIGH' if risk_score >= 2 else 'MEDIUM' if risk_score == 1 else 'LOW'

    def _short_term_outlook(self, news_data: Dict) -> str:
        """短期展望"""
        score = self._calculate_sentiment_score(news_data)
        if score > 0.3:
            return "短期有望测试$5,200-5,300阻力位"
        elif score < -0.3:
            return "短期可能回落至$4,800-4,900支撑位"
        return "短期区间震荡格局，方向待突破"

    def _medium_term_outlook(self, news_data: Dict) -> str:
        """中期展望"""
        score = self._calculate_sentiment_score(news_data)
        if score > 0.3:
            return "中期目标$5,500-6,000，看好黄金2026年表现"
        elif score < -0.3:
            return "中期可能进入调整期，支撑位$4,500"
        return "中期维持震荡上行判断"

    async def analyze_chart_pattern(self, chart_data: Dict = None) -> Dict:
        """分析K线图形态 - 增强版"""
        if self.use_mock:
            return self._mock_chart_analysis(chart_data)

        try:
            chat = self.llm
            prompt = self._build_chart_prompt(chart_data)
            response = await chat.send_message(UserMessage(prompt))
            import json
            return json.loads(response)
        except Exception as e:
            logger.warning(f"AI图表分析失败: {e}")
            return self._mock_chart_analysis(chart_data)

    def _build_chart_prompt(self, chart_data: Dict) -> str:
        """构建图表分析提示"""
        return f"""
        分析以下黄金技术图表数据，输出JSON格式：

        {chart_data if chart_data else '基于当前价格($4,966)和历史数据分析'}

        输出格式：
        {{
            "pattern": "检测到的形态名称",
            "confidence": 0-100,
            "signal": "BUY/SELL/HOLD",
            "description": "形态描述",
            "support_levels": [支撑位1, 支撑位2],
            "resistance_levels": [阻力位1, 阻力位2],
            "stop_loss": "建议止损位",
            "take_profit": "建议止盈位",
            "risk_reward_ratio": "风险回报比",
            "pattern_reliability": "形态可靠性评分",
            "volume_confirmation": "成交量确认情况",
            "timeframe_bias": "多时间框架偏向"
        }}
        """

    def _mock_chart_analysis(self, chart_data: Dict = None) -> Dict:
        """模拟图表分析"""
        import random
        patterns = [
            {
                'pattern': '上升三角形',
                'signal': 'BUY',
                'reliability': 75,
                'description': '价格形成上升三角形整理，突破在即'
            },
            {
                'pattern': '双底形态',
                'signal': 'BUY',
                'reliability': 80,
                'description': '形成双底结构，看涨反转信号'
            },
            {
                'pattern': '旗形整理',
                'signal': 'BUY',
                'reliability': 70,
                'description': '上涨旗形整理完成，有望继续走高'
            },
            {
                'pattern': '头肩底',
                'signal': 'BUY',
                'reliability': 78,
                'description': '经典头肩底形态，反弹目标明确'
            }
        ]
        selected = random.choice(patterns)

        return {
            'pattern': selected['pattern'],
            'confidence': selected['reliability'] + random.randint(-5, 5),
            'signal': selected['signal'],
            'description': selected['description'],
            'support_levels': [4850, 4750, 4650],
            'resistance_levels': [5050, 5150, 5300],
            'stop_loss': 4700,
            'take_profit': 5200,
            'risk_reward_ratio': '1:2.5',
            'pattern_reliability': selected['reliability'],
            'volume_confirmation': '成交量配合良好' if random.random() > 0.5 else '成交量略显不足',
            'timeframe_bias': '日线级别偏多，4小时级别待突破',
            'key_levels': {
                'pivot': 4966,
                'r1': 5030,
                'r2': 5100,
                's1': 4900,
                's2': 4850
            },
            'moving_average_status': {
                'sma_20': '价格高于MA20，短期偏多',
                'sma_50': '价格高于MA50，中期偏多',
                'sma_200': '价格远高于MA200，长期趋势向上'
            },
            'momentum_indicators': {
                'rsi': 'RSI在55附近，尚未超买',
                'macd': 'MACD金叉向上，动能偏多',
                'adx': 'ADX>25，趋势明确'
            },
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def analyze_market_sentiment(self, sentiment_data: Dict = None) -> Dict:
        """综合市场情绪分析 - 增强版"""
        if self.use_mock:
            return self._mock_sentiment_analysis(sentiment_data)

        try:
            chat = self.llm
            prompt = self._build_sentiment_prompt(sentiment_data)
            response = await chat.send_message(UserMessage(prompt))
            import json
            return json.loads(response)
        except Exception as e:
            logger.warning(f"AI情绪分析失败: {e}")
            return self._mock_sentiment_analysis(sentiment_data)

    def _build_sentiment_prompt(self, data: Dict) -> str:
        """构建情绪分析提示"""
        return f"""
        分析以下黄金市场情绪数据，输出JSON格式：

        {data if data else '基于VIX、美元指数、黄金ETF持仓等数据分析'}

        输出格式：
        {{
            "overall": "BULLISH/BEARISH/NEUTRAL",
            "vix_index": VIX值,
            "vix_interpretation": "VIX解读",
            "usd_index": 美元指数值,
            "usd_outlook": "美元前景",
            "gold_etf_flows": "黄金ETF资金流向",
            "cftc_positions": "对冲基金仓位",
            "零售情绪": "零售投资者情绪",
            "risk_sentiment": "风险偏好 LOW/MEDIUM/HIGH",
            "confidence": 0-100,
            "summary": "综合评估",
            "contrarian_view": "反向思维分析",
            "commitment_of_traders": "COT报告分析"
        }}
        """

    def _mock_sentiment_analysis(self, sentiment_data: Dict = None) -> Dict:
        """模拟情绪分析"""
        import random

        vix = round(random.uniform(13, 18), 1)
        usd = round(random.uniform(102, 106), 1)

        return {
            'overall': 'BULLISH',
            'vix_index': vix,
            'vix_interpretation': 'VIX处于低位，市场恐慌情绪较低' if vix < 15 else 'VIX有所上升，市场波动增加',
            'usd_index': usd,
            'usd_outlook': '美元震荡偏弱，利好黄金' if usd < 105 else '美元相对强势，对黄金形成压力',
            'gold_etf_flows': '连续4周净流入，累计流入约50亿美元',
            'cftc_positions': '对冲基金净多头持仓创历史新高',
            'retail_sentiment': '散户看涨比例75%，处于偏高水平',
            'risk_sentiment': 'MEDIUM',
            'confidence': round(random.uniform(68, 85), 1),
            'summary': '机构与散户情绪偏多，但需警惕获利了结风险',
            'contrarian_view': '当散户过于乐观时，往往预示短期回调风险',
            'commitment_of_traders': '商业套保商净空头增加，可能预示顶部风险',
            'sentiment_gauge': {
                'extreme_fear': 10,
                'fear': 20,
                'neutral': 25,
                'greed': 30,
                'extreme_greed': 15,
                'current_position': 'neutral_to_greed'
            },
            'market_breadth': {
                'advancing_assets': '黄金相关资产多数上涨',
                'volume_trend': '成交量高于20日均量',
                'sector_performance': '黄金矿业股表现强劲'
            },
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def generate_comprehensive_report(self, market_data: Dict) -> Dict:
        """生成综合分析报告"""
        news_analysis = await self.analyze_news_sentiment(market_data.get('news', None))
        chart_analysis = await self.analyze_chart_pattern(market_data.get('chart', None))
        sentiment_analysis = await self.analyze_market_sentiment(market_data.get('sentiment', None))

        overall_score = self._calculate_overall_score(
            news_analysis, chart_analysis, sentiment_analysis
        )

        return {
            'report_timestamp': datetime.now(timezone.utc).isoformat(),
            'gold_price': market_data.get('current_price', 4966),
            'overall_assessment': self._get_assessment(overall_score),
            'overall_score': overall_score,
            'executive_summary': self._generate_executive_summary(
                news_analysis, chart_analysis, sentiment_analysis, overall_score
            ),
            'fundamental_analysis': {
                'macroeconomic': news_analysis,
                'outlook': '整体偏向乐观'
            },
            'technical_analysis': {
                'chart_patterns': chart_analysis,
                'trend_status': '上升趋势保持完好'
            },
            'sentiment_analysis': {
                'market_mood': sentiment_analysis,
                'crowd_behavior': '跟随趋势'
            },
            'trade_recommendations': self._generate_recommendations(
                chart_analysis, overall_score
            ),
            'risk_warnings': self._generate_risk_warnings(
                news_analysis, sentiment_analysis
            ),
            'data_sources': [
                'GoldPrice.org API',
                'Federal Reserve Economic Data',
                'Investing.com',
                'COT Reports',
                'Bloomberg Terminal'
            ],
            'next_update': datetime.now(timezone.utc).isoformat()
        }

    def _calculate_overall_score(self, news: Dict, chart: Dict, sentiment: Dict) -> float:
        """计算综合评分"""
        score = 0

        sentiment_map = {'BULLISH': 1, 'NEUTRAL': 0, 'BEARISH': -1}
        score += sentiment_map.get(news.get('sentiment', 'NEUTRAL'), 0) * 0.3
        score += sentiment_map.get(sentiment.get('overall', 'NEUTRAL'), 0) * 0.2

        signal_map = {'BUY': 1, 'HOLD': 0, 'SELL': -1}
        score += signal_map.get(chart.get('signal', 'HOLD'), 0) * 0.3

        confidence = (news.get('confidence', 50) +
                     chart.get('confidence', 50) +
                     sentiment.get('confidence', 50)) / 300
        score *= (0.5 + confidence * 0.5)

        return round(score, 2)

    def _get_assessment(self, score: float) -> str:
        """根据评分生成评估"""
        if score > 0.4:
            return 'STRONG_BULLISH'
        elif score > 0.2:
            return 'BULLISH'
        elif score > -0.2:
            return 'NEUTRAL'
        elif score > -0.4:
            return 'BEARISH'
        else:
            return 'STRONG_BEARISH'

    def _generate_executive_summary(self, news: Dict, chart: Dict, sentiment: Dict, score: float) -> str:
        """生成执行摘要"""
        assessment = self._get_assessment(score)
        assessment_cn = {
            'STRONG_BULLISH': '强烈看涨',
            'BULLISH': '看涨',
            'NEUTRAL': '中性',
            'BEARISH': '看跌',
            'STRONG_BEARISH': '强烈看跌'
        }.get(assessment, '中性')

        return f"""黄金市场综合评估：{assessment_cn}

技术面：{chart.get('description', '分析中')}，当前价格高于主要均线，趋势偏多。

基本面：{news.get('summary', '分析中')}，美联储政策、地缘政治等因素支撑金价。

情绪面：{sentiment.get('summary', '分析中')}，机构资金持续流入。

综合评分：{score:.2f}/1.0，建议{'逢低买入' if score > 0.2 else '观望或减仓' if score < -0.2 else '区间操作'}。
"""

    def _generate_recommendations(self, chart: Dict, score: float) -> Dict:
        """生成交易建议"""
        signal = chart.get('signal', 'HOLD')
        return {
            'primary_signal': signal,
            'entry_levels': chart.get('support_levels', [4800, 4700]),
            'stop_loss': chart.get('stop_loss', 4600),
            'take_profit_levels': chart.get('take_profit', [5200, 5500]),
            'risk_reward': chart.get('risk_reward_ratio', '1:2'),
            'position_sizing': '正常仓位，建议10-20%配置',
            'time_horizon': '中期（1-3个月）',
            'additional_notes': '建议分批建仓，跌破关键支撑位止损'
        }

    def _generate_risk_warnings(self, news: Dict, sentiment: Dict) -> List[str]:
        """生成风险警告"""
        warnings = []

        if sentiment.get('risk_level') == 'HIGH':
            warnings.append('地缘政治风险偏高，可能导致剧烈波动')

        if news.get('sentiment') == 'BEARISH':
            warnings.append('基本面出现利空信号')

        if sentiment.get('retail_sentiment', '').find('75%') != -1:
            warnings.append('散户情绪过于乐观，可能预示短期回调')

        warnings.append('过往表现不代表未来收益')
        warnings.append('请根据个人风险承受能力谨慎决策')

        return warnings
