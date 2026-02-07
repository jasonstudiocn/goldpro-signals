import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react';

const SignalCard = ({ signal, loading }) => {
  if (loading) {
    return (
      <div className="glass-card rounded-sm p-6" data-testid="signal-card-loading">
        <div className="h-6 w-24 loading-skeleton rounded mb-4"></div>
        <div className="h-20 loading-skeleton rounded"></div>
      </div>
    );
  }

  if (!signal) {
    return null;
  }

  const getSignalColor = (sig) => {
    switch (sig) {
      case 'BUY':
        return 'text-[#10B981] border-[#10B981]';
      case 'SELL':
        return 'text-[#EF4444] border-[#EF4444]';
      default:
        return 'text-[#F59E0B] border-[#F59E0B]';
    }
  };

  const getSignalIcon = (sig) => {
    switch (sig) {
      case 'BUY':
        return <TrendingUp size={24} />;
      case 'SELL':
        return <TrendingDown size={24} />;
      default:
        return <Minus size={24} />;
    }
  };

  const getSignalText = (sig) => {
    switch (sig) {
      case 'BUY':
        return '买涨';
      case 'SELL':
        return '买跌';
      default:
        return '观望';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card rounded-sm p-6 relative overflow-hidden"
      data-testid="signal-card"
    >
      {/* 背景发光效果 */}
      <div className="absolute top-0 right-0 w-40 h-40 blur-3xl opacity-10"
        style={{
          background: signal.signal === 'BUY' ? '#10B981' : signal.signal === 'SELL' ? '#EF4444' : '#F59E0B'
        }}
      ></div>

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-gray-400">当前交易信号</p>
          <AlertCircle size={16} className="text-gray-500" />
        </div>

        <div className="flex items-center gap-4 mb-4">
          <div className={`p-3 rounded-sm border ${getSignalColor(signal.signal)} bg-opacity-10`}>
            {getSignalIcon(signal.signal)}
          </div>
          <div>
            <h3 className={`text-2xl font-heading font-bold ${getSignalColor(signal.signal)}`} data-testid="signal-type">
              {getSignalText(signal.signal)}
            </h3>
            <p className="text-sm text-gray-400">信心度: <span className="font-mono text-white" data-testid="signal-confidence">{signal.confidence}%</span></p>
          </div>
        </div>

        <div className="border-t border-white/10 pt-4">
          <p className="text-sm text-gray-300" data-testid="signal-recommendation">{signal.recommendation}</p>
        </div>

        {signal.current_price && (
          <div className="mt-4 text-xs text-gray-500">
            当前价格: <span className="font-mono text-[#D4AF37]">${signal.current_price.toFixed(2)}</span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default SignalCard;