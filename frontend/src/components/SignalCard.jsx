import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const IndicatorBox = ({ name, signal, confidence }) => {
  const getSignalStyle = () => {
    switch (signal) {
      case 'BUY':
        return 'border-green-500/50 bg-green-500/10 text-green-400';
      case 'SELL':
        return 'border-red-500/50 bg-red-500/10 text-red-400';
      default:
        return 'border-gray-600/50 bg-gray-500/10 text-gray-400';
    }
  };

  const getSignalIcon = () => {
    switch (signal) {
      case 'BUY':
        return <TrendingUp size={12} />;
      case 'SELL':
        return <TrendingDown size={12} />;
      default:
        return <Minus size={12} />;
    }
  };

  const getConfidenceLabel = (conf) => {
    if (conf >= 80) return '高';
    if (conf >= 60) return '中';
    if (conf >= 40) return '低';
    return '观望';
  };

  return (
    <div className={`flex flex-col items-center p-2 rounded border ${getSignalStyle()} min-w-[60px]`}>
      <div className="flex items-center gap-1 mb-1">
        {getSignalIcon()}
        <span className="text-[10px] font-medium">{name}</span>
      </div>
      <span className="text-xs font-bold">{signal || '观望'}</span>
      {confidence > 0 && (
        <span className="text-[9px] opacity-70 mt-1">{getConfidenceLabel(confidence)} {confidence.toFixed(0)}%</span>
      )}
    </div>
  );
};

const SignalCard = ({ signal, loading: signalLoading }) => {
  const [indicators, setIndicators] = useState({});
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchIndicators = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API}/analysis/technical`);
      if (response.ok) {
        const data = await response.json();
        setIndicators(data);
        setLastUpdate(new Date());
      }
    } catch (err) {
      console.error('Failed to fetch indicators:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndicators();
    const interval = setInterval(fetchIndicators, 60000);
    return () => clearInterval(interval);
  }, []);

  const indicatorList = [
    { name: 'RSI', key: 'rsi', signalKey: 'signal', confKey: 'confidence' },
    { name: 'MACD', key: 'macd', signalKey: 'signal', confKey: 'confidence' },
    { name: 'MA20', key: 'sma_20', signalKey: null, confKey: null },
    { name: 'MA50', key: 'sma_50', signalKey: null, confKey: null },
    { name: 'MA200', key: 'sma_200', signalKey: null, confKey: null },
    { name: 'BOLL', key: 'bollinger', signalKey: 'signal', confKey: 'confidence' },
    { name: 'ATR', key: 'atr', signalKey: null, confKey: null },
    { name: 'STOCH', key: 'stochastic', signalKey: 'signal', confKey: 'confidence' },
    { name: 'CCI', key: 'cci', signalKey: 'signal', confKey: 'confidence' },
    { name: 'MFI', key: 'mfi', signalKey: 'signal', confKey: 'confidence' },
    { name: 'W%R', key: 'williams_r', signalKey: 'signal', confKey: 'confidence' },
    { name: 'OBV', key: 'obv', signalKey: 'signal', confKey: 'confidence' },
    { name: 'ADX', key: 'adx', signalKey: 'signal', confKey: 'confidence' },
    { name: 'ROC', key: 'roc', signalKey: 'signal', confKey: 'confidence' },
  ];

  if (signalLoading) {
    return (
      <div className="glass-card rounded-sm p-6" data-testid="signal-card-loading">
        <div className="h-6 w-24 loading-skeleton rounded mb-4"></div>
        <div className="h-32 loading-skeleton rounded"></div>
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
      <div className="absolute top-0 right-0 w-40 h-40 blur-3xl opacity-10"
        style={{
          background: signal.signal === 'BUY' ? '#10B981' : signal.signal === 'SELL' ? '#EF4444' : '#F59E0B'
        }}
      ></div>

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-gray-400">当前交易信号</p>
          <button
            onClick={fetchIndicators}
            className="p-1 hover:bg-white/10 rounded transition-colors"
            title="刷新指标"
          >
            <RefreshCw size={14} className={`text-gray-500 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="flex items-center gap-4 mb-4">
          <div className={`p-3 rounded-sm border ${getSignalColor(signal.signal)} bg-opacity-10`}>
            {signal.signal === 'BUY' ? (
              <TrendingUp size={24} />
            ) : signal.signal === 'SELL' ? (
              <TrendingDown size={24} />
            ) : (
              <Minus size={24} />
            )}
          </div>
          <div>
            <h3 className={`text-2xl font-heading font-bold ${getSignalColor(signal.signal)}`}>
              {getSignalText(signal.signal)}
            </h3>
            <p className="text-sm text-gray-400">
              信心度: <span className="font-mono text-white">{signal.confidence}%</span>
            </p>
          </div>
        </div>

        <div className="border-t border-white/10 pt-4 mb-4">
          <p className="text-sm text-gray-300">{signal.recommendation}</p>
        </div>

        <div className="border-t border-white/10 pt-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs text-gray-400">技术指标分析</p>
            {lastUpdate && (
              <span className="text-[10px] text-gray-600">
                {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </div>

          {loading ? (
            <div className="grid grid-cols-7 gap-2">
              {[...Array(14)].map((_, i) => (
                <div key={i} className="h-14 bg-white/5 rounded animate-pulse"></div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-7 gap-2">
              {indicatorList.map((ind) => {
                const indicator = indicators[ind.key];
                
                let signalResult = null;
                let confidenceResult = 0;

                if (indicator && ind.signalKey && typeof indicator === 'object') {
                  signalResult = indicator[ind.signalKey];
                }
                if (indicator && ind.confKey && typeof indicator === 'object') {
                  const conf = indicator[ind.confKey];
                  confidenceResult = typeof conf === 'number' ? conf : 0;
                }

                return (
                  <IndicatorBox
                    key={ind.key}
                    name={ind.name}
                    signal={signalResult}
                    confidence={confidenceResult}
                  />
                );
              })}
            </div>
          )}
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
