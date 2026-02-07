import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Clock } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SignalHistory = () => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSignalHistory = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/signals/history?limit=20`);
      setSignals(res.data.signals);
    } catch (error) {
      console.error('获取信号历史失败:', error);
      toast.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSignalHistory();
  }, []);

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'BUY':
        return 'text-[#10B981] bg-[#10B981]/10 border-[#10B981]';
      case 'SELL':
        return 'text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]';
      default:
        return 'text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]';
    }
  };

  const getSignalIcon = (signal) => {
    switch (signal) {
      case 'BUY':
        return <TrendingUp size={16} />;
      case 'SELL':
        return <TrendingDown size={16} />;
      default:
        return <Minus size={16} />;
    }
  };

  const getSignalText = (signal) => {
    switch (signal) {
      case 'BUY':
        return '买涨';
      case 'SELL':
        return '买跌';
      default:
        return '观望';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="p-6 lg:p-8" data-testid="signal-history-page">
      <div className="mb-6">
        <h1 className="text-3xl font-heading font-bold text-white mb-2">交易信号历史</h1>
        <p className="text-sm text-gray-400">查看历史交易信号记录</p>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-24 loading-skeleton rounded-sm"></div>
          ))}
        </div>
      ) : signals.length === 0 ? (
        <div className="glass-card rounded-sm p-12 text-center">
          <Clock size={48} className="text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">暂无信号历史</p>
        </div>
      ) : (
        <div className="space-y-4">
          {signals.map((signal, index) => (
            <motion.div
              key={signal.id || index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass-card rounded-sm p-5 hover:border-[#D4AF37]/50 transition-colors"
              data-testid={`signal-item-${index}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <span className={`flex items-center gap-2 px-3 py-1.5 rounded-sm text-sm font-bold border ${getSignalColor(signal.signal)}`}>
                      {getSignalIcon(signal.signal)}
                      {getSignalText(signal.signal)}
                    </span>
                    <span className="text-sm font-mono text-gray-400">
                      信心度: <span className="text-white">{signal.confidence}%</span>
                    </span>
                    {signal.current_price && (
                      <span className="text-sm text-gray-400">
                        价格: <span className="font-mono text-[#D4AF37]">${signal.current_price.toFixed(2)}</span>
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-gray-300 mb-3">{signal.recommendation}</p>

                  {/* 详细信号 */}
                  {signal.signals_detail && signal.signals_detail.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {signal.signals_detail.slice(0, 4).map((detail, idx) => (
                        <div
                          key={idx}
                          className="text-xs px-2 py-1 bg-white/5 rounded text-gray-400 border border-white/10"
                        >
                          {detail.indicator}: {detail.signal} ({detail.confidence}%)
                        </div>
                      ))}
                      {signal.signals_detail.length > 4 && (
                        <div className="text-xs px-2 py-1 bg-white/5 rounded text-gray-400">
                          +{signal.signals_detail.length - 4} 更多
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="text-right ml-4">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Clock size={12} />
                    <span>{formatTimestamp(signal.timestamp)}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SignalHistory;