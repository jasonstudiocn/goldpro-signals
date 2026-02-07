import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Brain, Newspaper, TrendingUp, Target } from 'lucide-react';
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
        return 'text-[#10B981] bg-[#10B981]/10';
      case 'BEARISH':
        return 'text-[#EF4444] bg-[#EF4444]/10';
      default:
        return 'text-[#F59E0B] bg-[#F59E0B]/10';
    }
  };

  const getSentimentText = (sentiment) => {
    switch (sentiment) {
      case 'BULLISH':
        return '看涨';
      case 'BEARISH':
        return '看跌';
      default:
        return '中性';
    }
  };

  const AnalysisCard = ({ title, icon: Icon, data, type }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-sm p-6 relative overflow-hidden"
      data-testid={`ai-card-${type}`}
    >
      {/* 背景效果 */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-[#D4AF37] opacity-5 rounded-full blur-3xl"></div>

      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-[#D4AF37]/10 rounded-sm">
            <Icon size={20} className="text-[#D4AF37]" />
          </div>
          <h3 className="text-lg font-heading font-bold text-white">{title}</h3>
        </div>

        {loading ? (
          <div className="space-y-3">
            <div className="h-4 loading-skeleton rounded"></div>
            <div className="h-4 loading-skeleton rounded w-3/4"></div>
            <div className="h-20 loading-skeleton rounded"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* 情绪/信号 */}
            {(data?.sentiment || data?.signal) && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">分析结果</span>
                <span className={`px-3 py-1 rounded-sm text-xs font-bold ${getSentimentColor(data.sentiment || data.signal)}`}>
                  {data.sentiment ? getSentimentText(data.sentiment) : data.signal}
                </span>
              </div>
            )}

            {/* 信心度 */}
            {data?.confidence !== undefined && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">信心度</span>
                  <span className="text-sm font-mono text-white">{data.confidence}%</span>
                </div>
                <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#D4AF37] transition-all"
                    style={{ width: `${data.confidence}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* 描述/总结 */}
            {(data?.summary || data?.description) && (
              <div className="bg-white/5 rounded-sm p-4 border border-white/10">
                <p className="text-sm text-gray-300 leading-relaxed">
                  {data.summary || data.description}
                </p>
              </div>
            )}

            {/* 形态 */}
            {data?.pattern && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">图表形态</span>
                <span className="text-sm font-mono text-[#D4AF37]">{data.pattern}</span>
              </div>
            )}

            {/* 因素列表 */}
            {data?.factors && data.factors.length > 0 && (
              <div>
                <p className="text-sm text-gray-400 mb-2">关键因素</p>
                <ul className="space-y-1">
                  {data.factors.map((factor, index) => (
                    <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                      <span className="text-[#D4AF37] mt-1">•</span>
                      <span>{factor}</span>
                    </li>
                  ))}
                </ul>
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
          <h1 className="text-3xl font-heading font-bold text-white">AI 分析</h1>
        </div>
        <p className="text-sm text-gray-400">基于AI的新闻、图表形态和市场情绪分析</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <AnalysisCard
          title="新闻情绪分析"
          icon={Newspaper}
          data={aiData?.news}
          type="news"
        />
        <AnalysisCard
          title="K线图形态识别"
          icon={TrendingUp}
          data={aiData?.chart}
          type="chart"
        />
      </div>

      <div className="grid grid-cols-1 gap-6">
        <AnalysisCard
          title="市场情绪分析"
          icon={Target}
          data={aiData?.sentiment}
          type="sentiment"
        />
      </div>

      {/* AI分析说明 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-6 glass-card rounded-sm p-6"
      >
        <h3 className="text-sm font-heading font-bold text-white mb-3">关于AI分析</h3>
        <p className="text-xs text-gray-400 leading-relaxed">
          AI分析使用最新的大语言模型对市场新闻、K线图形态和整体市场情绪进行综合分析。
          这些分析结果将与技术指标相结合，共同形成最终的交易信号。
          请注意，AI分析仅供参考，不构成投资建议。
        </p>
      </motion.div>
    </div>
  );
};

export default AIAnalysis;