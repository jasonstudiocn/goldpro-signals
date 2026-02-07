import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PriceCard from '../components/PriceCard';
import SignalCard from '../components/SignalCard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { RefreshCw, Activity, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [currentPrice, setCurrentPrice] = useState(null);
  const [currentSignal, setCurrentSignal] = useState(null);
  const [priceHistory, setPriceHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async (showToast = false) => {
    try {
      setRefreshing(true);

      // 获取实时价格
      const priceRes = await axios.get(`${API}/price/current`);
      setCurrentPrice(priceRes.data);

      // 获取当前信号
      const signalRes = await axios.get(`${API}/signals/current`);
      setCurrentSignal(signalRes.data);

      // 获取历史数据
      const historyRes = await axios.get(`${API}/price/history?days=7`);
      setPriceHistory(historyRes.data.data);

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

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#1F1F22] border border-white/10 p-3 rounded-sm">
          <p className="text-xs text-gray-400 mb-1">价格</p>
          <p className="text-sm font-mono text-[#D4AF37]">${payload[0].value.toFixed(2)}</p>
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
        <div className="flex items-center gap-2 mb-4">
          <Activity size={20} className="text-[#D4AF37]" />
          <h2 className="text-lg font-heading font-bold text-white">7天价格走势</h2>
        </div>
        {loading ? (
          <div className="h-64 loading-skeleton rounded"></div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
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
              <Tooltip content={<CustomTooltip />} />
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
        )}
      </motion.div>

      {/* 快速统计 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: '今日高点', value: currentPrice ? `$${(currentPrice.price + Math.abs(currentPrice.change)).toFixed(2)}` : '--', icon: TrendingUp },
          { label: '今日低点', value: currentPrice ? `$${(currentPrice.price - Math.abs(currentPrice.change)).toFixed(2)}` : '--', icon: TrendingUp },
          { label: '交易量', value: '2.4M', icon: Activity },
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
                <p className="text-xl font-mono font-bold text-white">{stat.value}</p>
              </div>
              <div className="p-2 bg-white/5 rounded-sm">
                <stat.icon size={20} className="text-[#D4AF37]" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;