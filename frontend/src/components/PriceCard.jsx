import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';

const PriceCard = ({ price, change, changePercent, loading }) => {
  const isPositive = change >= 0;

  if (loading) {
    return (
      <div className="glass-card rounded-sm p-6" data-testid="price-card-loading">
        <div className="h-8 w-32 loading-skeleton rounded mb-4"></div>
        <div className="h-12 w-48 loading-skeleton rounded"></div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-sm p-6 relative overflow-hidden"
      data-testid="price-card"
    >
      {/* 背景装饰 */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-[#D4AF37] opacity-5 rounded-full blur-3xl"></div>

      <div className="relative z-10">
        <p className="text-sm text-gray-400 mb-2">黄金实时价格</p>
        <div className="flex items-end gap-4">
          <span className="price-display text-white" data-testid="current-price">
            ${price?.toFixed(2) || '---'}
          </span>
          <div className="mb-2">
            <div
              className={`flex items-center gap-1 text-sm font-mono ${
                isPositive ? 'text-[#10B981]' : 'text-[#EF4444]'
              }`}
              data-testid="price-change"
            >
              {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
              <span>{isPositive ? '+' : ''}{change?.toFixed(2)}</span>
              <span>({isPositive ? '+' : ''}{changePercent?.toFixed(2)}%)</span>
            </div>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">USD/盎司</p>
      </div>
    </motion.div>
  );
};

export default PriceCard;