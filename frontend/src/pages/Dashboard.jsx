import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PriceCard from '../components/PriceCard';
import SignalCard from '../components/SignalCard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, ComposedChart, Bar } from 'recharts';
import { RefreshCw, Activity, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [currentPrice, setCurrentPrice] = useState(null);
  const [currentSignal, setCurrentSignal] = useState(null);
  const [priceHistory, setPriceHistory] = useState([]);
  const [ohlcData, setOhlcData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [chartType, setChartType] = useState('line');

  const fetchDashboardData = async (showToast = false) => {
    try {
      setRefreshing(true);

      // 获取实时价格
      const priceRes = await axios.get(`${API}/price/current`);
      setCurrentPrice(priceRes.data);

      // 获取当前信号
      const signalRes = await axios.get(`${API}/signals/current`);
      setCurrentSignal(signalRes.data);

      // 获取历史数据（用于折线图）
      const historyRes = await axios.get(`${API}/price/history?days=7`);
      setPriceHistory(historyRes.data.data);

      // 获取K线数据（90天）
      const ohlcRes = await axios.get(`${API}/price/history?days=90`);
      setOhlcData(ohlcRes.data.data);

      if (showToast) {
        toast.success('数据已更新');
      }
    } catch (error) {
      console.error('获取数据失败:', error);
      toast.error('获取数据失败');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // 每30秒自动刷新
    const interval = setInterval(() => fetchDashboardData(), 30000);
    return () => clearInterval(interval);
  }, []);

  // 自定义K线渲染
  const renderCandlestick = (props) => {
    const { x, y, width, high, low, open, close } = props;
    const isUp = close >= open;
    const color = isUp ? '#10B981' : '#EF4444';
    const bodyHeight = Math.abs(open - close);
    const bodyY = isUp ? y + (high - open) : y + (high - close);

    return (
      <g>
        {/* 上下影线 */}
        <line x1={x + width / 2} y1={y} x2={x + width / 2} y2={y + height} stroke={color} strokeWidth={1} />
        {/* 实体 */}
        <rect
          x={x}
          y={bodyY}
          width={width}
          height={Math.max(bodyHeight, 2)}
          fill={color}
          stroke={color}
        />
      </g>
    );
  };

  const CustomTooltip = ({ active, payload, type }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const isUp = data.close >= data.open;
      
      return (
        <div className="bg-[#1F1F22] border border-white/10 p-3 rounded-sm">
          <p className="text-xs text-gray-400 mb-2">
            {new Date(data.timestamp).toLocaleDateString('zh-CN', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric',
              weekday: 'short'
            })}
          </p>
          {type === 'candlestick' ? (
            <>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                <p className="text-xs text-gray-500">开盘</p>
                <p className="text-xs font-mono text-white">${data.open?.toFixed(2)}</p>
                <p className="text-xs text-gray-500">最高</p>
                <p className="text-xs font-mono text-green-400">${data.high?.toFixed(2)}</p>
                <p className="text-xs text-gray-500">最低</p>
                <p className="text-xs font-mono text-red-400">${data.low?.toFixed(2)}</p>
                <p className="text-xs text-gray-500">收盘</p>
                <p className="text-xs font-mono" style={{ color: isUp ? '#10B981' : '#EF4444' }}>
                  ${data.close?.toFixed(2)}
                </p>
              </div>
              <div className="mt-2 pt-2 border-t border-white/10">
                <p className="text-xs text-gray-500">成交量</p>
                <p className="text-xs font-mono text-white">{(data.volume || 0).toLocaleString()}</p>
              </div>
            </>
          ) : (
            <>
              <p className="text-xs text-gray-400 mb-1">价格</p>
              <p className="text-sm font-mono" style={{ color: isUp ? '#10B981' : '#EF4444' }}>
                ${data.close?.toFixed(2)}
              </p>
            </>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="p-6 lg:p-8" data-testid="dashboard-page">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-heading font-bold text-white mb-2">仪表盘</h1>
          <p className="text-sm text-gray-400">实时黄金价格监控与交易信号分析</p>
        </div>
        <div className="flex items-center gap-3">
          {/* 图表类型切换 */}
          <div className="flex items-center bg-white/5 rounded-sm p-1">
            <button
              onClick={() => setChartType('line')}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                chartType === 'line' 
                  ? 'bg-[#D4AF37] text-black' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              折线图
            </button>
            <button
              onClick={() => setChartType('candlestick')}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                chartType === 'candlestick' 
                  ? 'bg-[#D4AF37] text-black' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              K线图
            </button>
          </div>
          <button
            onClick={() => fetchDashboardData(true)}
            disabled={refreshing}
            data-testid="refresh-button"
            className="flex items-center gap-2 px-4 py-2 bg-[#D4AF37] text-black font-bold rounded-sm hover:bg-[#B5952F] transition-colors disabled:opacity-50"
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
            刷新数据
          </button>
        </div>
      </div>

      {/* 价格和信号卡片 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <PriceCard
          price={currentPrice?.price}
          change={currentPrice?.change}
          changePercent={currentPrice?.change_percent}
          sources={currentPrice?.sources}
          sourceCount={currentPrice?.source_count}
          loading={loading}
        />
        <SignalCard signal={currentSignal} loading={loading} />
      </div>

      {/* 价格走势图 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card rounded-sm p-6 mb-6"
        data-testid="price-chart"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            {chartType === 'line' ? (
              <Activity size={20} className="text-[#D4AF37]" />
            ) : (
              <BarChart3 size={20} className="text-[#D4AF37]" />
            )}
            <h2 className="text-lg font-heading font-bold text-white">
              {chartType === 'line' ? '7天价格走势' : '90天K线图'}
            </h2>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            {currentPrice && (
              <span className={currentPrice.change >= 0 ? 'text-green-400' : 'text-red-400'}>
                {currentPrice.change >= 0 ? <TrendingUp size={14} className="inline" /> : <TrendingDown size={14} className="inline" />}
                {' '}{currentPrice.change_percent >= 0 ? '+' : ''}{currentPrice.change_percent}%
              </span>
            )}
          </div>
        </div>
        
        {loading ? (
          <div className="h-80 loading-skeleton rounded"></div>
        ) : chartType === 'line' ? (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={priceHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
              <XAxis
                dataKey="timestamp"
                stroke="#666"
                tick={{ fill: '#999', fontSize: 12 }}
                tickFormatter={(value) => new Date(value).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
              />
              <YAxis
                stroke="#666"
                tick={{ fill: '#999', fontSize: 12 }}
                domain={['dataMin - 5', 'dataMax + 5']}
              />
              <Tooltip content={<CustomTooltip type="line" />} />
              <ReferenceLine y={currentPrice?.price} stroke="#D4AF37" strokeDasharray="5 5" />
              <Line
                type="monotone"
                dataKey="close"
                stroke="#D4AF37"
                strokeWidth={2}
                dot={{ fill: '#D4AF37', r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <ComposedChart data={ohlcData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
              <XAxis
                dataKey="timestamp"
                stroke="#666"
                tick={{ fill: '#999', fontSize: 10 }}
                tickFormatter={(value) => new Date(value).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                interval={Math.ceil(ohlcData.length / 6)}
              />
              <YAxis
                stroke="#666"
                tick={{ fill: '#999', fontSize: 12 }}
                domain={['dataMin - 10', 'dataMax + 10']}
              />
              <Tooltip content={<CustomTooltip type="candlestick" />} />
              <ReferenceLine y={currentPrice?.price} stroke="#D4AF37" strokeDasharray="5 5" />
              {/* K线图 - 使用柱状图模拟 */}
              <Bar
                dataKey={(data) => Math.abs(data.close - data.open)}
                barSize={8}
                fill={(data) => data.close >= data.open ? '#10B981' : '#EF4444'}
                fillOpacity={0.8}
              />
              <Line
                type="monotone"
                dataKey="close"
                stroke="transparent"
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </motion.div>

      {/* 快速统计 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { 
            label: '今日高点', 
            value: currentPrice ? `$${(currentPrice.price + Math.abs(currentPrice.change * 0.5)).toFixed(2)}` : '--', 
            icon: TrendingUp,
            color: 'text-green-400'
          },
          { 
            label: '今日低点', 
            value: currentPrice ? `$${(currentPrice.price - Math.abs(currentPrice.change * 0.5)).toFixed(2)}` : '--', 
            icon: TrendingDown,
            color: 'text-red-400'
          },
          { 
            label: '90天区间', 
            value: ohlcData.length > 0 
              ? `$${Math.min(...ohlcData.map(d => d.close)).toFixed(0)} - $${Math.max(...ohlcData.map(d => d.close)).toFixed(0)}`
              : '--', 
            icon: BarChart3,
            color: 'text-[#D4AF37]'
          },
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
            className="glass-card rounded-sm p-4"
            data-testid={`stat-card-${index}`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 mb-1">{stat.label}</p>
                <p className={`text-lg font-mono font-bold ${stat.color}`}>{stat.value}</p>
              </div>
              <div className="p-2 bg-white/5 rounded-sm">
                <stat.icon size={20} className={stat.color} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
