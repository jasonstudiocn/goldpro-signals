import pandas as pd
import logging
from typing import Optional, List, Dict
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

class HistoricalDataLoader:
    """历史数据加载器 - 从CSV文件加载真实黄金价格数据"""
    
    def __init__(self, data_path: str = "/Users/mac/AI/gold-trading-system/data/history/GOLD"):
        self.data_path = Path(data_path)
        self._cache = {}
    
    def get_available_files(self) -> Dict[str, str]:
        """获取可用的数据文件"""
        files = {
            'daily': 'GOLD_Daily_200701280000_202601300000.csv',
            'h12': 'GOLD_H12_200701281200_202601301200.csv',
            'm30': 'GOLD_M30_200701282100_202601302130.csv',
            'm15': 'GOLD_M15_202111081100_202601302145.csv',
            'm1': 'GOLD_M1_202510171713_202601302158.csv'
        }
        return files
    
    def load_daily_data(self, days: int = 365) -> List[Dict]:
        """加载日线数据"""
        cache_key = f'daily_{days}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            file_path = self.data_path / 'GOLD_Daily_200701280000_202601300000.csv'
            if not file_path.exists():
                logger.warning(f"日线数据文件不存在: {file_path}")
                return self._get_fallback_data(days)
            
            df = pd.read_csv(file_path, sep='\t')
            df.columns = df.columns.str.strip().str.replace('<', '').str.replace('>', '')
            
            # 转换日期格式
            df['DATE'] = pd.to_datetime(df['DATE'], format='%Y.%m.%d')
            df = df.sort_values('DATE', ascending=True)
            
            # 取最近的days条数据
            if len(df) > days:
                df = df.tail(days)
            
            # 转换为字典列表
            data = []
            for _, row in df.iterrows():
                data.append({
                    'timestamp': row['DATE'].replace(tzinfo=timezone.utc).isoformat(),
                    'open': float(row['OPEN']),
                    'high': float(row['HIGH']),
                    'low': float(row['LOW']),
                    'close': float(row['CLOSE']),
                    'volume': int(row['VOL']) if row['VOL'] else int(row.get('TICKVOL', 0))
                })
            
            self._cache[cache_key] = data
            logger.info(f"加载日线数据: {len(data)} 条记录")
            return data
            
        except Exception as e:
            logger.error(f"加载日线数据失败: {e}")
            return self._get_fallback_data(days)
    
    def load_m15_data(self, limit: int = 100) -> List[Dict]:
        """加载15分钟线数据"""
        cache_key = f'm15_{limit}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            file_path = self.data_path / 'GOLD_M15_202111081100_202601302145.csv'
            if not file_path.exists():
                logger.warning(f"15分钟线数据文件不存在: {file_path}")
                return []
            
            df = pd.read_csv(file_path, sep='\t')
            df.columns = df.columns.str.strip().str.replace('<', '').str.replace('>', '')
            
            # 转换日期时间格式
            df['datetime'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'], format='%Y.%m.%d %H:%M:%S')
            df = df.sort_values('datetime', ascending=True)
            
            # 取最近的limit条数据
            if len(df) > limit:
                df = df.tail(limit)
            
            data = []
            for _, row in df.iterrows():
                data.append({
                    'timestamp': row['datetime'].replace(tzinfo=timezone.utc).isoformat(),
                    'open': float(row['OPEN']),
                    'high': float(row['HIGH']),
                    'low': float(row['LOW']),
                    'close': float(row['CLOSE']),
                    'volume': int(row.get('VOL', 0)) or int(row.get('TICKVOL', 0))
                })
            
            self._cache[cache_key] = data
            logger.info(f"加载15分钟线数据: {len(data)} 条记录")
            return data
            
        except Exception as e:
            logger.error(f"加载15分钟线数据失败: {e}")
            return []
    
    def load_recent_data(self, days: int = 90) -> List[Dict]:
        """加载最近的日线数据用于技术分析"""
        daily_data = self.load_daily_data(days)
        
        if daily_data:
            return daily_data
        
        # 如果日线数据不可用，尝试使用M15数据合成日线
        m15_data = self.load_m15_data(96 * days)  # 96个15分钟 = 1天
        if m15_data:
            return self._aggregate_m15_to_daily(m15_data)
        
        return []
    
    def _aggregate_m15_to_daily(self, m15_data: List[Dict]) -> List[Dict]:
        """将15分钟数据聚合为日线"""
        if not m15_data:
            return []
        
        daily_bars = {}
        for bar in m15_data:
            dt = bar['timestamp'][:10]  # YYYY-MM-DD
            if dt not in daily_bars:
                daily_bars[dt] = {
                    'open': bar['open'],
                    'high': bar['high'],
                    'low': bar['low'],
                    'close': bar['close'],
                    'volume': bar.get('volume', 0),
                    'timestamp': dt + 'T00:00:00+00:00'
                }
            else:
                daily_bars[dt]['high'] = max(daily_bars[dt]['high'], bar['high'])
                daily_bars[dt]['low'] = min(daily_bars[dt]['low'], bar['low'])
                daily_bars[dt]['close'] = bar['close']
                daily_bars[dt]['volume'] += bar.get('volume', 0)
        
        return list(daily_bars.values())
    
    def _get_fallback_data(self, days: int) -> List[Dict]:
        """获取备用数据"""
        logger.warning("使用备用数据生成")
        return []
    
    def get_price_range(self) -> Dict:
        """获取价格范围信息"""
        daily_data = self.load_daily_data(1)
        if daily_data:
            return {
                'current': daily_data[-1]['close'],
                'timestamp': daily_data[-1]['timestamp']
            }
        return {'current': 5000, 'timestamp': datetime.now(timezone.utc).isoformat()}


def load_historical_data(data_path: str = "/Users/mac/AI/gold-trading-system/data/history/GOLD") -> HistoricalDataLoader:
    """加载历史数据的便捷函数"""
    return HistoricalDataLoader(data_path)
