import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PriceCard from '../components/PriceCard';
import SignalCard from '../components/SignalCard';
import KLineChart from '../components/KLineChart';
import { RefreshCw, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [currentPrice, setCurrentPrice] = useState(null);
  const [currentSignal, setCurrentSignal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [chartPeriod, setChartPeriod] = useState('D1');

  const fetchDashboardData = async (showToast = false) => {
    try {
      setRefreshing(true);

      const priceRes = await axios.get(`${API}/price/current`);
      setCurrentPrice(priceRes.data);

      const signalRes = await axios.get(`${API}/signals/current`);
      setCurrentSignal(signalRes.data);

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
    const interval = setInterval(() => fetchDashboardData(), 30000);
    return () => clearInterval(interval);
  }, []);

  const periodLabels = {
    M1: '1分钟',
    M5: '5分钟',
    M15: '15分钟',
    M30: '30分钟',
    D1: '日线',
    W1: '周线',
    MN: '月线'
  };

  const periodLimits = {
    M1: 1000,
    M5: 1000,
    M15: 1000,
    M30: 1000,
    D1: 2000,
    W1: 500,
    MN: 200
  };

  useEffect(() => {
    if (currentPrice && currentPrice.price) {
      const chartDiv = document.querySelector('[data-testid="price-chart"]');
      if (chartDiv) {
        const priceLabel = chartDiv.querySelector('.price-label');
        if (priceLabel) {
          priceLabel.textContent = `$${currentPrice.price.toFixed(2)}`;
        }
      }
    }
  }, [currentPrice]);

  return (
    <div className="p-6 lg:p-8" data-testid="dashboard-page">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-heading font-bold text-white mb-2">仪表盘</h1>
          <p className="text-sm text-gray-400">实时黄金价格监控与交易信号分析</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-white/5 rounded-sm p-1">
            <button
              onClick={() => setChartPeriod('M1')}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                chartPeriod === 'M1'
                  ? 'bg-[#D4AF37] text-black'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              M1
            </button>
            <button
              onClick={() => setChartPeriod('M5')}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                chartPeriod === 'M5'
                  ? 'bg-[#D4AF37] text-black'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              M5
            </button>
            <button
              onClick={() => setChartPeriod('M15')}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                chartPeriod === 'M15'
                  ? 'bg-[#D4AF37] text-black'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              M15
            </button>
            <button
              onClick={() => setChartPeriod('M30')}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                chartPeriod === 'M30'
                  ? 'bg-[#D4AF37] text-black'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              M30
            </button>
            <button
              onClick={() => setChartPeriod('D1')}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                chartPeriod === 'D1'
                  ? 'bg-[#D4AF37] text-black'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              D1
            </button>
            <button
              onClick={() => setChartPeriod('W1')}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                chartPeriod === 'W1'
                  ? 'bg-[#D4AF37] text-black'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              W
            </button>
            <button
              onClick={() => setChartPeriod('MN')}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                chartPeriod === 'MN'
                  ? 'bg-[#D4AF37] text-black'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              MN
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
            <BarChart3 size={20} className="text-[#D4AF37]" />
            <h2 className="text-lg font-heading font-bold text-white">
              黄金K线图 ({periodLabels[chartPeriod]})
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
          <div className="h-[500px] loading-skeleton rounded"></div>
        ) : (
          <KLineChart period={chartPeriod} height={500} />
        )}
      </motion.div>

      {/* 快速统计 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            label: '最新价格',
            value: currentPrice ? `$${currentPrice.price.toFixed(2)}` : '--',
            icon: BarChart3,
            color: 'text-[#D4AF37]'
          },
          {
            label: '今日涨跌',
            value: currentPrice ? `${currentPrice.change >= 0 ? '+' : ''}${currentPrice.change.toFixed(2)} (${currentPrice.change >= 0 ? '+' : ''}${currentPrice.change_percent.toFixed(3)}%)` : '--',
            icon: currentPrice?.change >= 0 ? TrendingUp : TrendingDown,
            color: currentPrice?.change >= 0 ? 'text-green-400' : 'text-red-400'
          },
          {
            label: '数据来源',
            value: currentPrice?.sources?.length > 0 ? `${currentPrice.source_count}个` : '--',
            icon: BarChart3,
            color: 'text-blue-400'
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
