import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Brain, Newspaper, TrendingUp, Target, TrendingDown, TrendingUp as TrendingUpIcon, AlertTriangle, BarChart3, DollarSign, Globe } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIAnalysis = () => {
  const [aiData, setAiData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAIAnalysis = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/analysis/ai`);
      setAiData(res.data);
    } catch (error) {
      console.error('获取AI分析失败:', error);
      toast.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAIAnalysis();
  }, []);

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'BULLISH':
        return 'text-[#10B981] bg-[#10B981]/10 border-[#10B981]';
      case 'STRONG_BULLISH':
        return 'text-[#10B981] bg-[#10B981]/20 border-[#10B981]';
      case 'BEARISH':
        return 'text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]';
      case 'STRONG_BEARISH':
        return 'text-[#EF4444] bg-[#EF4444]/20 border-[#EF4444]';
      default:
        return 'text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]';
    }
  };

  const getSentimentText = (sentiment) => {
    const texts = {
      'BULLISH': '看涨',
      'STRONG_BULLISH': '强烈看涨',
      'BEARISH': '看跌',
      'STRONG_BEARISH': '强烈看跌',
      'NEUTRAL': '中性',
      'BUY': '买入',
      'SELL': '卖出',
      'HOLD': '观望'
    };
    return texts[sentiment] || sentiment;
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'HIGH':
        return 'text-[#EF4444]';
      case 'MEDIUM':
        return 'text-[#F59E0B]';
      case 'LOW':
        return 'text-[#10B981]';
      default:
        return 'text-gray-400';
    }
  };

  const ConfidenceBar = ({ value, label }) => (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-400">{label || '信心度'}</span>
        <span className="text-xs font-mono text-white">{value?.toFixed(1) || 0}%</span>
      </div>
      <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all ${
            value >= 70 ? 'bg-[#10B981]' : value >= 50 ? 'bg-[#F59E0B]' : 'bg-[#EF4444]'
          }`}
          style={{ width: `${Math.min(value || 0, 100)}%` }}
        ></div>
      </div>
    </div>
  );

  const KeyValueRow = ({ label, value, highlight = false }) => (
    <div className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
      <span className="text-sm text-gray-400">{label}</span>
      <span className={`text-sm font-mono ${highlight ? 'text-[#D4AF37]' : 'text-white'}`}>
        {value !== undefined && value !== null ? value : '-'}
      </span>
    </div>
  );

  const BulletList = ({ title, items }) => (
    <div className="mt-3">
      <p className="text-xs text-gray-400 mb-2">{title}</p>
      <ul className="space-y-1">
        {items?.map((item, index) => (
          <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
            <span className="text-[#D4AF37] mt-1.5 w-1.5 h-1.5 bg-[#D4AF37] rounded-full flex-shrink-0"></span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );

  const NewsAnalysisCard = ({ data }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-sm p-6 relative overflow-hidden"
      data-testid="ai-card-news"
    >
      <div className="absolute top-0 right-0 w-32 h-32 bg-[#D4AF37] opacity-5 rounded-full blur-3xl"></div>

      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-[#D4AF37]/10 rounded-sm">
            <Newspaper size={20} className="text-[#D4AF37]" />
          </div>
          <div>
            <h3 className="text-lg font-heading font-bold text-white">新闻情绪分析</h3>
            <p className="text-xs text-gray-500">基于宏观经济与地缘政治数据</p>
          </div>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => <div key={i} className="h-16 loading-skeleton rounded"></div>)}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-white/5 rounded-sm p-4 border border-white/10">
              <span className="text-sm text-gray-400">综合情绪</span>
              <span className={`px-3 py-1 rounded-sm text-xs font-bold border ${getSentimentColor(data?.sentiment)}`}>
                {getSentimentText(data?.sentiment)}
              </span>
            </div>

            <ConfidenceBar value={data?.confidence} label="分析信心度" />

            {data?.summary && (
              <div className="bg-white/5 rounded-sm p-4 border border-white/10">
                <p className="text-sm text-gray-300 leading-relaxed">{data.summary}</p>
              </div>
            )}

            <BulletList title="关键驱动因素" items={data?.key_drivers} />

            <div className="bg-white/5 rounded-sm p-4 border border-white/10 space-y-2">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <DollarSign size={14} className="text-[#10B981]" />
                <span>美联储政策</span>
              </div>
              <p className="text-xs text-gray-300 pl-6">{data?.federal_reserve_analysis || '-'}</p>

              <div className="flex items-center gap-2 text-sm text-gray-400 mt-3">
                <Globe size={14} className="text-[#F59E0B]" />
                <span>美元走势</span>
              </div>
              <p className="text-xs text-gray-300 pl-6">{data?.usd_impact || '-'}</p>

              <div className="flex items-center gap-2 text-sm text-gray-400 mt-3">
                <AlertTriangle size={14} className="text-[#EF4444]" />
                <span>地缘政治风险</span>
              </div>
              <p className="text-xs text-gray-300 pl-6">{data?.geopolitical_risk || '-'}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white/5 rounded-sm p-3 border border-white/10">
                <span className="text-xs text-gray-400">风险等级</span>
                <p className={`text-sm font-bold ${getRiskColor(data?.risk_level)}`}>
                  {data?.risk_level || '-'}
                </p>
              </div>
              <div className="bg-white/5 rounded-sm p-3 border border-white/10">
                <span className="text-xs text-gray-400">短期展望</span>
                <p className="text-sm text-white truncate">{data?.short_term_outlook?.slice(0, 15) || '-'}...</p>
              </div>
            </div>

            {data?.analysis_timestamp && (
              <p className="text-xs text-gray-500 text-right">
                更新: {new Date(data.analysis_timestamp).toLocaleString()}
              </p>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );

  const ChartAnalysisCard = ({ data }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="glass-card rounded-sm p-6 relative overflow-hidden"
      data-testid="ai-card-chart"
    >
      <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500 opacity-5 rounded-full blur-3xl"></div>

      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-500/10 rounded-sm">
            <TrendingUp size={20} className="text-blue-500" />
          </div>
          <div>
            <h3 className="text-lg font-heading font-bold text-white">K线图形态分析</h3>
            <p className="text-xs text-gray-500">基于价格走势与形态识别</p>
          </div>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => <div key={i} className="h-16 loading-skeleton rounded"></div>)}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-white/5 rounded-sm p-4 border border-white/10">
              <span className="text-sm text-gray-400">图表形态</span>
              <span className={`px-3 py-1 rounded-sm text-xs font-bold border ${getSentimentColor(data?.signal)}`}>
                {data?.pattern || '-'}
              </span>
            </div>

            <ConfidenceBar value={data?.confidence} label="形态可靠性" />

            <div className="bg-white/5 rounded-sm p-4 border border-white/10">
              <p className="text-sm text-gray-300 leading-relaxed">{data?.description || data?.analysis || '-'}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white/5 rounded-sm p-3 border border-white/10">
                <span className="text-xs text-gray-400">止损位</span>
                <p className="text-sm font-mono text-[#EF4444]">${data?.stop_loss || '-'}</p>
              </div>
              <div className="bg-white/5 rounded-sm p-3 border border-white/10">
                <span className="text-xs text-gray-400">止盈位</span>
                <p className="text-sm font-mono text-[#10B981]">${data?.take_profit || '-'}</p>
              </div>
            </div>

            <div className="bg-white/5 rounded-sm p-3 border border-white/10">
              <span className="text-xs text-gray-400">风险回报比</span>
              <p className="text-sm font-mono text-[#D4AF37]">{data?.risk_reward_ratio || '-'}</p>
            </div>

            <BulletList title="支撑位" items={data?.support_levels?.map(l => `$${l}`)} />
            <BulletList title="阻力位" items={data?.resistance_levels?.map(l => `$${l}`)} />

            {data?.key_levels && (
              <div className="bg-white/5 rounded-sm p-4 border border-white/10">
                <p className="text-xs text-gray-400 mb-2">关键价位</p>
                <div className="grid grid-cols-5 gap-2 text-center">
                  {['S2', 'S1', '枢轴', 'R1', 'R2'].map((label, i) => {
                    const values = [data.key_levels.s2, data.key_levels.s1, data.key_levels.pivot, data.key_levels.r1, data.key_levels.r2];
                    return (
                      <div key={i}>
                        <p className="text-xs text-gray-500">{label}</p>
                        <p className="text-xs font-mono text-white">{values[i] || '-'}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            <div className="bg-white/5 rounded-sm p-3 border border-white/10">
              <span className="text-xs text-gray-400">均线状态</span>
              <p className="text-xs text-gray-300 mt-1">{data?.moving_average_status?.sma_20 || '-'}</p>
              <p className="text-xs text-gray-300">{data?.moving_average_status?.sma_50 || '-'}</p>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );

  const SentimentAnalysisCard = ({ data }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="glass-card rounded-sm p-6 relative overflow-hidden"
      data-testid="ai-card-sentiment"
    >
      <div className="absolute top-0 right-0 w-32 h-32 bg-green-500 opacity-5 rounded-full blur-3xl"></div>

      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-green-500/10 rounded-sm">
            <Target size={20} className="text-green-500" />
          </div>
          <div>
            <h3 className="text-lg font-heading font-bold text-white">市场情绪分析</h3>
            <p className="text-xs text-gray-500">基于VIX、机构持仓等数据</p>
          </div>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => <div key={i} className="h-16 loading-skeleton rounded"></div>)}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-white/5 rounded-sm p-4 border border-white/10">
              <span className="text-sm text-gray-400">市场情绪</span>
              <span className={`px-3 py-1 rounded-sm text-xs font-bold border ${getSentimentColor(data?.overall)}`}>
                {getSentimentText(data?.overall)}
              </span>
            </div>

            <ConfidenceBar value={data?.confidence} label="分析信心度" />

            <div className="grid grid-cols-3 gap-3">
              <div className="bg-white/5 rounded-sm p-3 border border-white/10 text-center">
                <span className="text-xs text-gray-400">VIX指数</span>
                <p className="text-sm font-mono text-white">{data?.vix_index || '-'}</p>
                <p className="text-xs text-gray-500">{data?.vix_interpretation?.slice(0, 10) || '-'}...</p>
              </div>
              <div className="bg-white/5 rounded-sm p-3 border border-white/10 text-center">
                <span className="text-xs text-gray-400">美元指数</span>
                <p className="text-sm font-mono text-white">{data?.usd_index || '-'}</p>
                <p className="text-xs text-gray-500">{data?.usd_outlook?.slice(0, 10) || '-'}...</p>
              </div>
              <div className="bg-white/5 rounded-sm p-3 border border-white/10 text-center">
                <span className="text-xs text-gray-400">风险偏好</span>
                <p className={`text-sm font-bold ${getRiskColor(data?.risk_sentiment)}`}>{data?.risk_sentiment || '-'}</p>
              </div>
            </div>

            <BulletList title="黄金ETF资金流向" items={[data?.gold_etf_flows || '-']} />
            <BulletList title="对冲基金仓位" items={[data?.cftc_positions || '-']} />
            <BulletList title="散户情绪" items={[data?.retail_sentiment || '-']} />

            {data?.sentiment_gauge && (
              <div className="bg-white/5 rounded-sm p-4 border border-white/10">
                <p className="text-xs text-gray-400 mb-2">情绪仪表盘</p>
                <div className="flex items-center gap-1">
                  {['恐惧', '', '中性', '', '贪婪'].map((label, i) => {
                    const positions = ['extreme_fear', 'fear', 'neutral', 'greed', 'extreme_greed'];
                    const current = data.sentiment_gauge.current_position;
                    const idx = positions.indexOf(current);
                    const isActive = Math.abs(i - idx) <= 1;
                    return (
                      <div key={i} className="flex-1 text-center">
                        <div className={`h-2 rounded-sm ${isActive ? 'bg-[#D4AF37]' : 'bg-white/10'}`}></div>
                        <p className="text-[10px] text-gray-500 mt-1">{label}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {data?.contrarian_view && (
              <div className="bg-[#F59E0B]/10 rounded-sm p-4 border border-[#F59E0B]/20">
                <p className="text-xs text-[#F59E0B] mb-1">⚠️ 反向思维提示</p>
                <p className="text-sm text-gray-300">{data.contrarian_view}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );

  return (
    <div className="p-6 lg:p-8" data-testid="ai-analysis-page">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Brain size={32} className="text-[#D4AF37]" />
          <h1 className="text-3xl font-heading font-bold text-white">AI 智能分析</h1>
        </div>
        <p className="text-sm text-gray-400">基于大语言模型的新闻、图表与市场情绪综合分析</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <NewsAnalysisCard data={aiData?.news} />
        <ChartAnalysisCard data={aiData?.chart} />
      </div>

      <div className="grid grid-cols-1 gap-6">
        <SentimentAnalysisCard data={aiData?.sentiment} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-6 glass-card rounded-sm p-6"
      >
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 size={16} className="text-[#D4AF37]" />
          <h3 className="text-sm font-heading font-bold text-white">关于AI分析</h3>
        </div>
        <p className="text-xs text-gray-400 leading-relaxed mb-3">
          AI分析使用最新的大语言模型对市场新闻、K线图形态和整体市场情绪进行综合分析。
          分析维度包括：宏观经济指标、地缘政治风险、技术形态识别、机构资金流向、散户情绪指标等。
        </p>
        <p className="text-xs text-gray-500">
          数据来源: {aiData?.news?.data_sources?.join(' | ') || 'GoldPrice.org, Investing.com, Federal Reserve'}
        </p>
        <p className="text-xs text-[#EF4444] mt-2">
          ⚠️ AI分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。
        </p>
      </motion.div>
    </div>
  );
};

export default AIAnalysis;
