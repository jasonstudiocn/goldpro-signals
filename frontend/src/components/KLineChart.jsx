import React, { useEffect, useRef, useState, useCallback } from 'react';
import { init, dispose } from 'klinecharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TechnicalIndicatorBox = ({ name, value, signal }) => {
  const getSignalColor = () => {
    switch (signal) {
      case 'BUY': return 'text-green-400 border-green-400 bg-green-400/10';
      case 'SELL': return 'text-red-400 border-red-400 bg-red-400/10';
      default: return 'text-gray-400 border-gray-400 bg-gray-400/10';
    }
  };

  return (
    <div className={`flex flex-col items-center px-3 py-2 rounded border ${getSignalColor()} min-w-[80px]`}>
      <span className="text-xs font-medium">{name}</span>
      <span className="text-sm font-mono font-bold">{value !== undefined && value !== null ? (typeof value === 'number' ? value.toFixed(2) : value) : '--'}</span>
      <span className="text-xs mt-1">{signal || '观望'}</span>
    </div>
  );
};

const KLineChart = ({ period = 'D1', height = 500 }) => {
  const chartContainerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [indicators, setIndicators] = useState({});
  const [selectedBar, setSelectedBar] = useState(null);

  const calculateIndicators = useCallback(async (data, barIndex = null) => {
    if (!data || data.length === 0) return;

    try {
      const endIndex = barIndex !== null ? barIndex + 1 : data.length;
      const startIndex = Math.max(0, endIndex - 200);
      const subset = data.slice(startIndex, endIndex);

      const formattedData = subset.map(d => ({
        timestamp: d.timestamp,
        open: Number(d.open),
        high: Number(d.high),
        low: Number(d.low),
        close: Number(d.close),
        volume: Number(d.volume) || 0
      }));

      const response = await fetch(`${API}/analysis/technical`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: formattedData })
      });

      if (response.ok) {
        const result = await response.json();
        setIndicators(result);
      }
    } catch (err) {
      console.error('Failed to calculate indicators:', err);
    }
  }, []);

  useEffect(() => {
    if (!chartContainerRef.current) return undefined;

    const chart = init(chartContainerRef.current, {
      layout: {
        background: { type: 'solid', color: '#1F1F22' },
        text: '#999',
      },
      grid: {
        show: true,
        horizontal: { show: true, color: '#333333' },
        vertical: { show: true, color: '#333333' },
      },
      candle: {
        upColor: '#10B981',
        downColor: '#EF4444',
        upWickColor: '#10B981',
        downWickColor: '#EF4444',
      },
      xAxis: {
        position: 'bottom',
        height: 30,
        zoomAnchor: 'last_bar',
      },
    });

    let loadedData = [];

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API}/kline/${period}?limit=2000&reverse=true`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();
        const data = Array.isArray(result.data) ? result.data : [];

        if (data.length === 0) {
          setError('暂无数据');
          setLoading(false);
          return;
        }

        loadedData = [...data].reverse();

        chart.applyNewData(loadedData);

        await calculateIndicators(data, data.length - 1);
        setLoading(false);

      } catch (err) {
        console.error('Chart error:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    chart.subscribeAction('onCandleBarClick', async (params) => {
      if (params.kLineData) {
        const clickedData = params.kLineData;
        const clickedIndex = loadedData.findIndex(
          d => d.timestamp === clickedData.timestamp
        );

        if (clickedIndex >= 0) {
          setSelectedBar({
            timestamp: clickedData.timestamp,
            open: clickedData.open,
            high: clickedData.high,
            low: clickedData.low,
            close: clickedData.close
          });
          await calculateIndicators(loadedData, clickedIndex);
        }
      }
    });

    loadData();

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.resize(chartContainerRef.current.clientWidth, height);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      dispose(chart);
    };
  }, [period, height, calculateIndicators]);

  const getSignal = (indicator) => {
    if (!indicator) return null;
    return indicator.signal || 'HOLD';
  };

  return (
    <div className="w-full">
      {Object.keys(indicators).length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3 p-3 bg-[#252525] rounded">
          <TechnicalIndicatorBox
            name="RSI(14)"
            value={indicators.rsi?.value}
            signal={getSignal(indicators.rsi)}
          />
          <TechnicalIndicatorBox
            name="MACD"
            value={indicators.macd?.macd}
            signal={getSignal(indicators.macd)}
          />
          <TechnicalIndicatorBox
            name="MA20"
            value={indicators.sma_20}
            signal={indicators.sma_20 > indicators.close ? 'SELL' : indicators.sma_20 < indicators.close ? 'BUY' : 'HOLD'}
          />
          <TechnicalIndicatorBox
            name="MA50"
            value={indicators.sma_50}
            signal={indicators.sma_50 > indicators.close ? 'SELL' : indicators.sma_50 < indicators.close ? 'BUY' : 'HOLD'}
          />
          <TechnicalIndicatorBox
            name="BOLL"
            value={indicators.bollinger?.current_price}
            signal={getSignal(indicators.bollinger)}
          />
          <TechnicalIndicatorBox
            name="ATR"
            value={indicators.atr?.value}
            signal={null}
          />
          <TechnicalIndicatorBox
            name="STOCH"
            value={indicators.stochastic?.value}
            signal={getSignal(indicators.stochastic)}
          />
          <TechnicalIndicatorBox
            name="CCI"
            value={indicators.cci?.value}
            signal={getSignal(indicators.cci)}
          />
        </div>
      )}

      {selectedBar && (
        <div className="mb-2 p-2 bg-[#1F1F22] rounded text-xs text-gray-400">
          选中: {new Date(selectedBar.timestamp).toLocaleString()} | O:{selectedBar.open} H:{selectedBar.high} L:{selectedBar.low} C:{selectedBar.close}
        </div>
      )}

      <div className="relative w-full" style={{ height }}>
        <div
          ref={chartContainerRef}
          className="w-full"
          style={{ height }}
        />
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-[#1F1F22]/90">
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin" />
              <span className="text-[#D4AF37] text-sm">加载中...</span>
            </div>
          </div>
        )}
        {error && !loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-[#1F1F22]/90">
            <div className="text-center">
              <p className="text-red-400 text-sm mb-1">加载失败</p>
              <p className="text-gray-500 text-xs">{error}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default KLineChart;
