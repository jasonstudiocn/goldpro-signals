import sqlite3
import pandas as pd
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Generator
import threading

logger = logging.getLogger(__name__)

class HistoricalDataDatabase:
    """SQLite数据库存储历史K线数据"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None):
        if self._initialized:
            return

        if db_path is None:
            base_dir = Path(__file__).parent.parent
            db_path = base_dir / 'data' / 'gold_history.db'
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()
        self._initialized = True

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_kline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT UNIQUE NOT NULL,
                datetime TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS m1_kline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT UNIQUE NOT NULL,
                datetime TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS m5_kline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT UNIQUE NOT NULL,
                datetime TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS m15_kline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT UNIQUE NOT NULL,
                datetime TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS m30_kline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT UNIQUE NOT NULL,
                datetime TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS h12_kline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT UNIQUE NOT NULL,
                datetime TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_daily_kline_timestamp ON daily_kline(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_m1_kline_timestamp ON m1_kline(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_m15_kline_timestamp ON m15_kline(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_m30_kline_timestamp ON m30_kline(timestamp)
        ''')

        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")

    def import_daily_data(self, csv_path: str) -> Dict:
        """从CSV文件导入日线数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            df = pd.read_csv(csv_path, sep='\t')
            df.columns = df.columns.str.strip().str.replace('<', '').str.replace('>', '')
            df['DATE'] = pd.to_datetime(df['DATE'], format='%Y.%m.%d')

            imported = 0
            skipped = 0

            for _, row in df.iterrows():
                timestamp = row['DATE'].strftime('%Y-%m-%d')
                datetime_str = row['DATE'].strftime('%Y-%m-%d %H:%M:%S')

                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO daily_kline
                        (timestamp, datetime, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        timestamp,
                        datetime_str,
                        float(row['OPEN']),
                        float(row['HIGH']),
                        float(row['LOW']),
                        float(row['CLOSE']),
                        int(row['VOL']) if row['VOL'] else int(row.get('TICKVOL', 0))
                    ))

                    if cursor.rowcount > 0:
                        imported += 1
                    else:
                        skipped += 1

                except Exception as e:
                    logger.warning(f"插入数据失败 {timestamp}: {e}")
                    skipped += 1

            conn.commit()
            logger.info(f"日线数据导入完成: 新增 {imported}, 跳过 {skipped}")

            return {'imported': imported, 'skipped': skipped}

        finally:
            conn.close()

    def import_m15_data(self, csv_path: str, limit: int = None):
        """从CSV文件导入15分钟线数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            df = pd.read_csv(csv_path, sep='\t')
            df.columns = df.columns.str.strip().str.replace('<', '').str.replace('>', '')

            df['datetime'] = pd.to_datetime(
                df['DATE'].astype(str) + ' ' + df['TIME'].astype(str),
                format='mixed',
                dayfirst=False
            )

            if limit:
                df = df.tail(limit)

            imported = 0
            skipped = 0

            for _, row in df.iterrows():
                timestamp = row['datetime'].strftime('%Y-%m-%d %H:%M:%S')

                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO m15_kline
                        (timestamp, datetime, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        timestamp,
                        timestamp,
                        float(row['OPEN']),
                        float(row['HIGH']),
                        float(row['LOW']),
                        float(row['CLOSE']),
                        int(row.get('VOL', 0)) or int(row.get('TICKVOL', 0))
                    ))

                    if cursor.rowcount > 0:
                        imported += 1
                    else:
                        skipped += 1

                except Exception as e:
                    logger.warning(f"插入M15数据失败 {timestamp}: {e}")
                    skipped += 1

            conn.commit()
            logger.info(f"M15数据导入完成: 新增 {imported}, 跳过 {skipped}")

            return {'imported': imported, 'skipped': skipped}

        finally:
            conn.close()

    def import_m1_data(self, csv_path: str, limit: int = None):
        """从CSV文件导入1分钟线数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            df = pd.read_csv(csv_path, sep='\t')
            df.columns = df.columns.str.strip().str.replace('<', '').str.replace('>', '')

            df['datetime'] = pd.to_datetime(
                df['DATE'].astype(str) + ' ' + df['TIME'].astype(str),
                format='mixed',
                dayfirst=False
            )

            if limit:
                df = df.tail(limit)

            imported = 0
            skipped = 0

            for _, row in df.iterrows():
                timestamp = row['datetime'].strftime('%Y-%m-%d %H:%M:%S')

                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO m1_kline
                        (timestamp, datetime, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        timestamp,
                        timestamp,
                        float(row['OPEN']),
                        float(row['HIGH']),
                        float(row['LOW']),
                        float(row['CLOSE']),
                        int(row.get('VOL', 0)) or int(row.get('TICKVOL', 0))
                    ))

                    if cursor.rowcount > 0:
                        imported += 1
                    else:
                        skipped += 1

                except Exception as e:
                    logger.warning(f"插入M1数据失败 {timestamp}: {e}")
                    skipped += 1

            conn.commit()
            logger.info(f"M1数据导入完成: 新增 {imported}, 跳过 {skipped}")

            return {'imported': imported, 'skipped': skipped}

        finally:
            conn.close()

    def import_m30_data(self, csv_path: str):
        """从CSV文件导入30分钟线数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            df = pd.read_csv(csv_path, sep='\t')
            df.columns = df.columns.str.strip().str.replace('<', '').str.replace('>', '')

            df['datetime'] = pd.to_datetime(
                df['DATE'].astype(str) + ' ' + df['TIME'].astype(str),
                format='mixed',
                dayfirst=False
            )

            imported = 0
            skipped = 0

            for _, row in df.iterrows():
                timestamp = row['datetime'].strftime('%Y-%m-%d %H:%M:%S')

                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO m30_kline
                        (timestamp, datetime, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        timestamp,
                        timestamp,
                        float(row['OPEN']),
                        float(row['HIGH']),
                        float(row['LOW']),
                        float(row['CLOSE']),
                        int(row.get('VOL', 0)) or int(row.get('TICKVOL', 0))
                    ))

                    if cursor.rowcount > 0:
                        imported += 1
                    else:
                        skipped += 1

                except Exception as e:
                    logger.warning(f"插入M30数据失败 {timestamp}: {e}")
                    skipped += 1

            conn.commit()
            logger.info(f"M30数据导入完成: 新增 {imported}, 跳过 {skipped}")

            return {'imported': imported, 'skipped': skipped}

        finally:
            conn.close()

    def aggregate_m5_from_m1(self):
        """从1分钟数据聚合5分钟数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM m5_kline')

            cursor.execute('SELECT timestamp, datetime, open, high, low, close, volume FROM m1_kline ORDER BY datetime')
            rows = cursor.fetchall()

            if not rows:
                return {'aggregated': 0}

            aggregated = {}
            for row in rows:
                dt = row[1]
                hour = dt[11:13]
                minute = int(dt[14:16])
                period_min = (minute // 5) * 5
                period_key = f"{dt[:11]}{hour}:{period_min:02d}:00"

                if period_key not in aggregated:
                    aggregated[period_key] = {
                        'timestamp': period_key,
                        'datetime': period_key,
                        'open': row[2],
                        'high': row[3],
                        'low': row[4],
                        'close': row[5],
                        'volume': row[6]
                    }
                else:
                    agg = aggregated[period_key]
                    agg['high'] = max(agg['high'], row[3])
                    agg['low'] = min(agg['low'], row[4])
                    agg['close'] = row[5]
                    agg['volume'] += row[6]

            for period_key, data in aggregated.items():
                cursor.execute('''
                    INSERT INTO m5_kline (timestamp, datetime, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['timestamp'],
                    data['datetime'],
                    data['open'],
                    data['high'],
                    data['low'],
                    data['close'],
                    data['volume']
                ))

            conn.commit()
            count = len(aggregated)
            logger.info(f"M5数据聚合完成: {count} 条")

            return {'aggregated': count}

        except Exception as e:
            logger.error(f"M5聚合失败: {e}")
            return {'error': str(e)}

        finally:
            conn.close()

    def aggregate_weekly_from_daily(self):
        """从日线数据聚合周线数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM weekly_kline')

            cursor.execute('''
                INSERT INTO weekly_kline (timestamp, datetime, open, high, low, close, volume)
                SELECT
                    MIN(timestamp),
                    MIN(datetime),
                    MIN(open) as open,
                    MAX(high) as high,
                    MIN(low) as low,
                    MAX(close) as close,
                    SUM(volume) as volume
                FROM daily_kline
                GROUP BY strftime('%Y', datetime) || '-' || (CAST(strftime('%W', datetime) AS INTEGER))
                ORDER BY datetime
            ''')

            conn.commit()
            count = cursor.rowcount
            logger.info(f"周线数据聚合完成: {count} 条")

            return {'aggregated': count}

        except Exception as e:
            logger.error(f"周线聚合失败: {e}")
            return {'error': str(e)}

        finally:
            conn.close()

    def aggregate_monthly_from_daily(self):
        """从日线数据聚合月线数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM monthly_kline')

            cursor.execute('''
                INSERT INTO monthly_kline (timestamp, datetime, open, high, low, close, volume)
                SELECT
                    MIN(timestamp),
                    MIN(datetime),
                    MIN(open) as open,
                    MAX(high) as high,
                    MIN(low) as low,
                    MAX(close) as close,
                    SUM(volume) as volume
                FROM daily_kline
                GROUP BY strftime('%Y', datetime) || '-' || strftime('%m', datetime)
                ORDER BY datetime
            ''')

            conn.commit()
            count = cursor.rowcount
            logger.info(f"月线数据聚合完成: {count} 条")

            return {'aggregated': count}

        except Exception as e:
            logger.error(f"月线聚合失败: {e}")
            return {'error': str(e)}

        finally:
            conn.close()

    def get_daily_data(self, start_date: str = None, end_date: str = None, limit: int = None) -> List[Dict]:
        """获取日线数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = 'SELECT timestamp, datetime, open, high, low, close, volume FROM daily_kline'
            params = []

            if start_date and end_date:
                query += ' WHERE timestamp BETWEEN ? AND ?'
                params.extend([start_date, end_date])
            elif start_date:
                query += ' WHERE timestamp >= ?'
                params.append(start_date)
            elif end_date:
                query += ' WHERE timestamp <= ?'
                params.append(end_date)

            query += ' ORDER BY timestamp ASC'

            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                {
                    'timestamp': row[0],
                    'datetime': row[1],
                    'open': row[2],
                    'high': row[3],
                    'low': row[4],
                    'close': row[5],
                    'volume': row[6]
                }
                for row in rows
            ]

        finally:
            conn.close()

    def get_kline_data_for_chart(self, period: str = 'daily', limit: int = 1000, reverse: bool = True) -> List[Dict]:
        """获取K线数据（专为KLineChart格式化）"""
        period_map = {
            'M1': ('m1_kline', 60),
            'M5': ('m5_kline', 300),
            'M15': ('m15_kline', 900),
            'M30': ('m30_kline', 1800),
            'D1': ('daily_kline', 86400),
            'W1': ('weekly_kline', 604800),
            'MN': ('monthly_kline', 2592000),
        }

        table = 'daily_kline'
        if period in period_map:
            table = period_map[period][0]

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = f'SELECT timestamp, datetime, open, high, low, close, volume FROM {table}'
            query += ' ORDER BY timestamp ASC'

            if limit and period in ['M1', 'M5']:
                query += f' LIMIT {limit}'

            cursor.execute(query)
            rows = cursor.fetchall()

            data = [
                {
                    'timestamp': int(datetime.fromisoformat(row[0]).timestamp() * 1000) if isinstance(row[0], str) else int(row[0]),
                    'datetime': row[1] if row[1] else row[0],
                    'open': row[2],
                    'high': row[3],
                    'low': row[4],
                    'close': row[5],
                    'volume': row[6] if len(row) > 6 else 0
                }
                for row in rows
            ]

            if reverse:
                data = list(reversed(data))

            return data

        except Exception as e:
            logger.error(f"获取{period}数据失败: {e}")
            return []

        finally:
            conn.close()

    def get_kline_data(self, period: str = 'daily', limit: int = 1000) -> List[Dict]:
        """获取任意周期的K线数据"""
        if period in ['M1', 'M5', 'M15', 'M30', 'D1']:
            return self.get_kline_data_for_chart(period, limit)
        elif period == 'W1':
            return self.get_weekly_data(limit)
        elif period == 'MN':
            return self.get_monthly_data(limit)
        else:
            return self.get_kline_data_for_chart('daily', limit)

    def get_weekly_data(self, limit: int = 200) -> List[Dict]:
        """获取周线数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT timestamp, datetime, open, high, low, close, volume FROM (
                    SELECT
                        timestamp,
                        datetime,
                        open,
                        high,
                        low,
                        close,
                        volume,
                        ROW_NUMBER() OVER (ORDER BY timestamp DESC) as rn
                    FROM (
                        SELECT
                            MIN(timestamp) as timestamp,
                            MIN(datetime) as datetime,
                            MIN(open) as open,
                            MAX(high) as high,
                            MIN(low) as low,
                            MAX(close) as close,
                            SUM(volume) as volume
                        FROM daily_kline
                        GROUP BY
                            strftime('%Y', datetime) || '-' ||
                            CAST((CAST(strftime('%j', datetime) AS INTEGER) / 7) AS INTEGER)
                        ORDER BY timestamp DESC
                    )
                ) WHERE rn <= ?
            ''', (limit,))

            rows = cursor.fetchall()

            return [
                {
                    'timestamp': int(datetime.fromisoformat(row[0]).timestamp() * 1000),
                    'datetime': row[1],
                    'open': row[2],
                    'high': row[3],
                    'low': row[4],
                    'close': row[5],
                    'volume': row[6]
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"获取周线数据失败: {e}")
            return []

        finally:
            conn.close()

    def get_monthly_data(self, limit: int = 120) -> List[Dict]:
        """获取月线数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f'''
                SELECT timestamp, datetime, open, high, low, close, volume FROM (
                    SELECT
                        MIN(timestamp) as timestamp,
                        MIN(datetime) as datetime,
                        MIN(open) as open,
                        MAX(high) as high,
                        MIN(low) as low,
                        MAX(close) as close,
                        SUM(volume) as volume
                    FROM daily_kline
                    GROUP BY strftime('%Y', datetime) || '-' || strftime('%m', datetime)
                    ORDER BY timestamp DESC
                    LIMIT {limit}
                ) ORDER BY timestamp ASC
            ''')

            rows = cursor.fetchall()

            return [
                {
                    'timestamp': int(datetime.fromisoformat(row[0]).timestamp() * 1000),
                    'datetime': row[1],
                    'open': row[2],
                    'high': row[3],
                    'low': row[4],
                    'close': row[5],
                    'volume': row[6]
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"获取月线数据失败: {e}")
            return []

        finally:
            conn.close()

    def get_latest_price(self) -> Optional[Dict]:
        """获取最新价格"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT timestamp, open, high, low, close, volume
                FROM daily_kline
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            row = cursor.fetchone()

            if row:
                return {
                    'timestamp': row[0],
                    'open': row[1],
                    'high': row[2],
                    'low': row[3],
                    'close': row[4],
                    'volume': row[5]
                }
            return None

        finally:
            conn.close()

    def get_data_count(self, table: str = 'daily_kline') -> int:
        """获取数据条数"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def clear_data(self, table: str = 'daily_kline') -> bool:
        """清空指定表数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f'DELETE FROM {table}')
            conn.commit()
            logger.info(f"已清空{table}数据")
            return True
        except Exception as e:
            logger.error(f"清空数据失败: {e}")
            return False
        finally:
            conn.close()


historical_db = HistoricalDataDatabase()


def get_historical_db() -> HistoricalDataDatabase:
    """获取数据库单例"""
    return historical_db
