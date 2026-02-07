import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TechnicalAnalysis = () => {
  const [indicators, setIndicators] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchTechnicalData = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/analysis/technical`);
      setIndicators(res.data);
    } catch (error) {
      console.error('获取技术指标失败:', error);
      toast.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTechnicalData();
  }, []);

  const getSignalIcon = (signal) => {
    switch (signal) {
      case 'BUY':
        return <TrendingUp size={18} className="text-[#10B981]" />;
      case 'SELL':
        return <TrendingDown size={18} className="text-[#EF4444]" />;
      default:
        return <Minus size={18} className="text-[#F59E0B]" />;
    }
  };

  const getSignalBadge = (signal) => {
    const colors = {
      BUY: 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]',
      SELL: 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]',
      HOLD: 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]',
    };
    const labels = { BUY: '买入', SELL: '卖出', HOLD: '观望' };

    return (
      <span className={`signal-badge px-3 py-1 rounded-sm text-xs border ${colors[signal] || colors.HOLD}`}>
        {labels[signal] || signal}
      </span>
    );
  };

  const IndicatorCard = ({ title, data, description }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="indicator-card rounded-sm p-5"
      data-testid={`indicator-${title}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-base font-heading font-bold text-white mb-1">{title}</h3>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
        {data?.signal && getSignalIcon(data.signal)}
      </div>

      <div className="space-y-3">
        {Object.entries(data || {}).map(([key, value]) => {
          if (key === 'signal') {
            return (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-gray-400">信号</span>
                {getSignalBadge(value)}
              </div>
            );
          }
          if (key === 'confidence' && typeof value === 'number') {
            return (
              <div key={key}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-400">信心度</span>
                  <span className="text-sm font-mono text-white">{value}%</span>
                </div>
                <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#D4AF37] transition-all"
                    style={{ width: `${value}%` }}
                  ></div>
                </div>
              </div>
            );
          }
          if (typeof value === 'number') {
            return (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-gray-400 capitalize">{key.replace('_', ' ')}</span>
                <span className="text-sm font-mono text-white">{value.toFixed(2)}</span>
              </div>
            );
          }
          if (typeof value === 'string' && key !== 'signal') {
            return (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-gray-400 capitalize">{key}</span>
                <span className="text-sm text-white">{value}</span>
              </div>
            );
          }
          return null;
        })}
      </div>
    </motion.div>
  );

  return (
    <div className="p-6 lg:p-8" data-testid="technical-analysis-page">
      <div className="mb-6">
        <h1 className="text-3xl font-heading font-bold text-white mb-2">技术指标分析</h1>
        <p className="text-sm text-gray-400">实时技术指标与买卖信号</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-48 loading-skeleton rounded-sm"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <IndicatorCard
            title="RSI (相对强弱指数)"
            data={indicators?.rsi}
            description="14周期 RSI"
          />
          <IndicatorCard
            title="MACD"
            data={indicators?.macd}
            description="移动平均收敛散度"
          />
          <IndicatorCard
            title="布林带"
            data={indicators?.bollinger}
            description="20周期 Bollinger Bands"
          />
          <IndicatorCard
            title="ATR (平均真实波幅)"
            data={indicators?.atr}
            description="14周期 ATR"
          />
          <IndicatorCard
            title="随机震荡指标"
            data={indicators?.stochastic}
            description="14周期 Stochastic"
          />
          <IndicatorCard
            title="移动平均线"
            data={{
              sma_20: indicators?.sma_20,
              sma_50: indicators?.sma_50,
              ema_20: indicators?.ema_20,
            }}
            description="SMA & EMA"
          />
        </div>
      )}
    </div>
  );
};

export default TechnicalAnalysis;