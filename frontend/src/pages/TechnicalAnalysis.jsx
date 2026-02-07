import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Activity, TrendingUp as TrendingUpIcon, TrendingDown as TrendingDownIcon } from 'lucide-react';
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
      case 'STRONG_BUY':
        return <TrendingUpIcon size={18} className="text-[#10B981]" />;
      case 'STRONG_SELL':
        return <TrendingDownIcon size={18} className="text-[#EF4444]" />;
      default:
        return <Minus size={18} className="text-[#F59E0B]" />;
    }
  };

  const getSignalBadge = (signal) => {
    const colors = {
      BUY: 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]',
      SELL: 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]',
      HOLD: 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]',
      STRONG_BUY: 'bg-[#10B981]/20 text-[#10B981] border-[#10B981]',
      STRONG_SELL: 'bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]',
    };
    const labels = {
      BUY: '买入',
      SELL: '卖出',
      HOLD: '观望',
      STRONG_BUY: '强烈买入',
      STRONG_SELL: '强烈卖出',
    };

    return (
      <span className={`signal-badge px-3 py-1 rounded-sm text-xs border ${colors[signal] || colors.HOLD}`}>
        {labels[signal] || signal}
      </span>
    );
  };

  const formatValue = (key, value) => {
    if (typeof value === 'number') {
      if (key.includes('confidence') || key.includes('percent') || key.includes('ratio')) {
        return `${value.toFixed(2)}%`;
      }
      return value.toFixed(2);
    }
    if (typeof value === 'boolean') {
      return value ? '是' : '否';
    }
    return value;
  };

  const getDisplayName = (key) => {
    const names = {
      sma_20: 'SMA 20',
      sma_50: 'SMA 50',
      sma_200: 'SMA 200',
      ema_20: 'EMA 20',
      ema_12: 'EMA 12',
      ema_26: 'EMA 26',
      value: '当前值',
      signal: '信号',
      confidence: '信心度',
      trend: '趋势',
      overbought: '超买',
      oversold: '超卖',
      volatility: '波动性',
      histogram: '柱状图',
      histogram_trend: '柱状趋势',
      macd_above_signal: 'MACD在信号线上',
      bandwidth: '带宽',
      position: '价位位置',
      squeeze: '挤压',
      k: '%K',
      d: '%D',
      k_above_d: 'K在D上方',
      atr_percent: 'ATR占比',
      atr_rank: 'ATR排名',
      strong_overbought: '强超买',
      strong_oversold: '强超卖',
      ma: '均线值',
      divergence: '背离',
      adx: 'ADX值',
      plus_di: '+DI',
      minus_di: '-DI',
      trend_strength: '趋势强度',
      trend_direction: '趋势方向',
      momentum: '动量',
      fibonacci: '斐波那契',
      pivot: '枢轴点',
      r1: '阻力1',
      r2: '阻力2',
      r3: '阻力3',
      s1: '支撑1',
      s2: '支撑2',
      s3: '支撑3',
      current_price: '当前价格',
      above_vwap: '在VWAP上方',
      upper: '上轨',
      middle: '中轨',
      lower: '下轨',
      width: '通道宽度',
      cross: '交叉',
      tenkan: '转换线',
      kijun: '基准线',
      senkou_a: '先行线A',
      senkou_b: '先行线B',
      cloud_bullish: '云图看涨',
      price_above_cloud: '价格在云图上方',
      support_levels: '支撑位',
      resistance_levels: '阻力位',
      nearest_support: '最近支撑',
      nearest_resistance: '最近阻力',
      volume_ratio: '成交量比',
      current_volume: '当前成交量',
      average_volume: '平均成交量',
      high_volume: '高成交量',
      low_volume: '低成交量',
      price_change_pct: '价格变化%',
      description: '描述',
    };
    return names[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const IndicatorCard = ({ title, data, description }) => {
    if (!data || Object.keys(data).length === 0) return null;

    return (
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
          {Object.entries(data).map(([key, value]) => {
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
                    <span className="text-sm font-mono text-white">{value.toFixed(2)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        value >= 70 ? 'bg-[#10B981]' : value >= 50 ? 'bg-[#F59E0B]' : 'bg-[#EF4444]'
                      }`}
                      style={{ width: `${Math.min(value, 100)}%` }}
                    ></div>
                  </div>
                </div>
              );
            }
            if (typeof value === 'number' || typeof value === 'string' || typeof value === 'boolean') {
              return (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">{getDisplayName(key)}</span>
                  <span className="text-sm font-mono text-white">{formatValue(key, value)}</span>
                </div>
              );
            }
            if (typeof value === 'object' && value !== null) {
              return (
                <div key={key} className="mt-2">
                  <span className="text-xs text-gray-500 block mb-1">{getDisplayName(key)}</span>
                  <div className="pl-2 border-l-2 border-white/10 space-y-1">
                    {Object.entries(value).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between">
                        <span className="text-xs text-gray-400">{getDisplayName(k)}</span>
                        <span className="text-xs font-mono text-gray-300">{formatValue(k, v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            }
            return null;
          })}
        </div>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="p-6 lg:p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-heading font-bold text-white mb-2">技术指标分析</h1>
          <p className="text-sm text-gray-400">加载中...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
            <div key={i} className="h-48 loading-skeleton rounded-sm"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8" data-testid="technical-analysis-page">
      <div className="mb-6">
        <h1 className="text-3xl font-heading font-bold text-white mb-2">技术指标分析</h1>
        <p className="text-sm text-gray-400">全面的技术分析指标与买卖信号</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <IndicatorCard
          title="RSI (相对强弱指数)"
          data={indicators?.rsi}
          description="14周期 RSI - 动量指标"
        />
        <IndicatorCard
          title="RSI 背离"
          data={indicators?.rsi_divergence}
          description="RSI 背离检测"
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
          description="14周期 ATR - 波动性指标"
        />
        <IndicatorCard
          title="随机震荡指标"
          data={indicators?.stochastic}
          description="14周期 Stochastic"
        />
        <IndicatorCard
          title="Williams %R"
          data={indicators?.williams_r}
          description="Williams %R 指标"
        />
        <IndicatorCard
          title="CCI (商品通道指数)"
          data={indicators?.cci}
          description="20周期 CCI"
        />
        <IndicatorCard
          title="MFI (资金流量指数)"
          data={indicators?.mfi}
          description="14周期 MFI"
        />
        <IndicatorCard
          title="OBV (能量潮)"
          data={indicators?.obv}
          description="能量潮指标"
        />
        <IndicatorCard
          title="ADX (平均方向指数)"
          data={indicators?.adx}
          description="14周期 ADX - 趋势强度"
        />
        <IndicatorCard
          title="ROC (变动率)"
          data={indicators?.roc}
          description="10周期 ROC"
        />
        <IndicatorCard
          title="动量指标"
          data={indicators?.momentum}
          description="价格动量分析"
        />
        <IndicatorCard
          title="斐波那契回撤"
          data={indicators?.fibonacci}
          description="斐波那契支撑阻力位"
        />
        <IndicatorCard
          title="枢轴点"
          data={indicators?.pivot_points}
          description="Pivot Points 关键位"
        />
        <IndicatorCard
          title="VWAP"
          data={indicators?.vwap}
          description="成交量加权平均价格"
        />
        <IndicatorCard
          title="唐奇安通道"
          data={indicators?.donchian}
          description="Donchian Channels"
        />
        <IndicatorCard
          title="抛物线 SAR"
          data={indicators?.parabolic_sar}
          description="Parabolic SAR"
        />
        <IndicatorCard
          title="成交量分析"
          data={indicators?.volume}
          description="成交量指标"
        />
        <IndicatorCard
          title="金叉死叉"
          data={indicators?.cross_signals}
          description="Golden/Death Cross"
        />
        <IndicatorCard
          title="一目均衡表"
          data={indicators?.ichimoku}
          description="Ichimoku Cloud"
        />
        <IndicatorCard
          title="支撑阻力位"
          data={indicators?.support_resistance}
          description="支撑与阻力位"
        />
        <IndicatorCard
          title="移动平均线"
          data={{
            sma_20: indicators?.sma_20,
            sma_50: indicators?.sma_50,
            sma_200: indicators?.sma_200,
            ema_20: indicators?.ema_20,
            ema_12: indicators?.ema_12,
            ema_26: indicators?.ema_26,
          }}
          description="SMA & EMA 移动平均线"
        />
      </div>
    </div>
  );
};

export default TechnicalAnalysis;
