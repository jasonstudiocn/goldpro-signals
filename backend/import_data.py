#!/usr/bin/env python3
"""
历史数据导入脚本
从CSV文件导入黄金价格数据到SQLite数据库
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from historical_db import HistoricalDataDatabase, get_historical_db

DATA_PATH = "/Users/mac/AI/gold-trading-system/data/history/GOLD"

def import_all_data():
    """导入所有数据"""
    db = get_historical_db()

    print("=" * 50)
    print("黄金历史数据导入工具")
    print("=" * 50)

    daily_file = Path(DATA_PATH) / 'GOLD_Daily_200701280000_202601300000.csv'
    m15_file = Path(DATA_PATH) / 'GOLD_M15_202111081100_202601302145.csv'

    print(f"\n[1/2] 导入日线数据...")
    if daily_file.exists():
        result = db.import_daily_data(str(daily_file))
        print(f"    ✓ 日线数据导入完成: 新增 {result['imported']}, 跳过 {result['skipped']}")
        print(f"    ✓ 当前日线数据总量: {db.get_data_count('daily_kline')} 条")
    else:
        print(f"    ✗ 文件不存在: {daily_file}")

    print(f"\n[2/2] 导入15分钟线数据...")
    if m15_file.exists():
        result = db.import_m15_data(str(m15_file), limit=5000)
        print(f"    ✓ M15数据导入完成: 新增 {result['imported']}, 跳过 {result['skipped']}")
        print(f"    ✓ 当前M15数据总量: {db.get_data_count('m15_kline')} 条")
    else:
        print(f"    ✗ 文件不存在: {m15_file}")

    print("\n" + "=" * 50)
    print("导入完成!")
    print("=" * 50)

    latest = db.get_latest_price()
    if latest:
        print(f"\n最新数据: {latest['timestamp']}")
        print(f"最新价格: ${latest['close']:.2f}")

def check_database():
    """检查数据库状态"""
    db = get_historical_db()

    print("=" * 50)
    print("数据库状态检查")
    print("=" * 50)

    daily_count = db.get_data_count('daily_kline')
    m15_count = db.get_data_count('m15_kline')

    print(f"\n日线数据: {daily_count} 条")
    print(f"15分钟线数据: {m15_count} 条")

    latest = db.get_latest_price()
    if latest:
        print(f"\n最新K线:")
        print(f"  时间: {latest['timestamp']}")
        print(f"  开盘: ${latest['open']:.2f}")
        print(f"  最高: ${latest['high']:.2f}")
        print(f"  最低: ${latest['low']:.2f}")
        print(f"  收盘: ${latest['close']:.2f}")
        print(f"  成交量: {latest['volume']}")

def clear_database():
    """清空数据库"""
    db = get_historical_db()

    print("=" * 50)
    print("清空数据库")
    print("=" * 50)

    db.clear_data('daily_kline')
    db.clear_data('m15_kline')
    db.clear_data('m30_kline')
    db.clear_data('h12_kline')

    print("\n✓ 数据库已清空")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='黄金历史数据导入工具')
    parser.add_argument('--check', action='store_true', help='检查数据库状态')
    parser.add_argument('--clear', action='store_true', help='清空数据库')
    parser.add_argument('--import', action='store_true', dest='import_data', default=True, help='导入数据（默认）')

    args = parser.parse_args()

    if args.clear:
        clear_database()
    elif args.check:
        check_database()
    else:
        import_all_data()
