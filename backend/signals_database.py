import json
import os
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class SignalsDatabase:
    """信号历史数据库 - 使用JSON文件存储"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = Path(__file__).parent.parent
            db_path = base_dir / 'data' / 'signals'
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.history_file = self.db_path / 'signal_history.json'
        self.stats_file = self.db_path / 'signal_stats.json'

    def save_signal(self, signal_data: Dict) -> bool:
        """保存交易信号到历史记录"""
        try:
            history = self._load_history()

            signal_entry = {
                'id': self._generate_id(),
                'signal': signal_data.get('signal', 'HOLD'),
                'confidence': signal_data.get('confidence', 0),
                'buy_score': signal_data.get('buy_score', 0),
                'sell_score': signal_data.get('sell_score', 0),
                'recommendation': signal_data.get('recommendation', ''),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'price_at_signal': signal_data.get('price_at_signal'),
                'signals_detail': signal_data.get('signals_detail', [])
            }

            history.append(signal_entry)

            # 只保留最近1000条记录
            if len(history) > 1000:
                history = history[-1000:]

            self._save_history(history)

            # 更新统计数据
            self._update_stats(signal_entry)

            logger.info(f"信号已保存: {signal_entry['signal']} @ {signal_entry['confidence']}%")
            return True

        except Exception as e:
            logger.error(f"保存信号失败: {e}")
            return False

    def get_signal_history(self, limit: int = 100, signal_type: str = None) -> List[Dict]:
        """获取信号历史记录"""
        try:
            history = self._load_history()

            if signal_type:
                history = [s for s in history if s['signal'] == signal_type.upper()]

            return history[-limit:]

        except Exception as e:
            logger.error(f"获取信号历史失败: {e}")
            return []

    def get_latest_signal(self) -> Optional[Dict]:
        """获取最新信号"""
        history = self._load_history()
        if history:
            return history[-1]
        return None

    def get_signal_stats(self) -> Dict:
        """获取信号统计信息"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"加载统计数据失败: {e}")

        return self._calculate_stats()

    def get_signal_performance(self, days: int = 30) -> Dict:
        """获取信号表现统计"""
        history = self._load_history()
        cutoff_date = datetime.now(timezone.utc).timestamp() - (days * 24 * 60 * 60)

        recent_signals = [
            s for s in history
            if datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00')).timestamp() > cutoff_date
        ]

        if not recent_signals:
            return {'message': '暂无信号数据'}

        buy_signals = [s for s in recent_signals if s['signal'] == 'BUY']
        sell_signals = [s for s in recent_signals if s['signal'] == 'SELL']
        hold_signals = [s for s in recent_signals if s['signal'] == 'HOLD']

        avg_confidence = {
            'BUY': sum(s['confidence'] for s in buy_signals) / len(buy_signals) if buy_signals else 0,
            'SELL': sum(s['confidence'] for s in sell_signals) / len(sell_signals) if sell_signals else 0,
            'HOLD': sum(s['confidence'] for s in hold_signals) / len(hold_signals) if hold_signals else 0
        }

        return {
            'period_days': days,
            'total_signals': len(recent_signals),
            'buy_count': len(buy_signals),
            'sell_count': len(sell_signals),
            'hold_count': len(hold_signals),
            'avg_confidence': {k: round(v, 2) for k, v in avg_confidence.items()},
            'signal_distribution': {
                'BUY': round(len(buy_signals) / len(recent_signals) * 100, 1) if recent_signals else 0,
                'SELL': round(len(sell_signals) / len(recent_signals) * 100, 1) if recent_signals else 0,
                'HOLD': round(len(hold_signals) / len(recent_signals) * 100, 1) if recent_signals else 0
            }
        }

    def _load_history(self) -> List[Dict]:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("信号历史文件损坏，将重新创建")
                return []
        return []

    def _save_history(self, history: List[Dict]):
        """保存历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _generate_id(self) -> str:
        """生成唯一ID"""
        return f"sig_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    def _update_stats(self, signal_entry: Dict):
        """更新统计数据"""
        stats = self.get_signal_stats()

        signal = signal_entry['signal']
        stats['total_signals'] = stats.get('total_signals', 0) + 1
        stats['by_signal'][signal] = stats.get('by_signal', {}).get(signal, 0) + 1

        total_conf = stats.get('total_confidence', 0) + signal_entry['confidence']
        count = stats.get('signal_count', 0) + 1
        stats['avg_confidence'] = round(total_conf / count, 2) if count > 0 else 0
        stats['signal_count'] = count

        stats['last_updated'] = datetime.now(timezone.utc).isoformat()

        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存统计数据失败: {e}")

    def _calculate_stats(self) -> Dict:
        """计算统计数据"""
        history = self._load_history()

        if not history:
            return {
                'total_signals': 0,
                'signal_count': 0,
                'avg_confidence': 0,
                'by_signal': {'BUY': 0, 'SELL': 0, 'HOLD': 0},
                'last_updated': None
            }

        buy_count = len([s for s in history if s['signal'] == 'BUY'])
        sell_count = len([s for s in history if s['signal'] == 'SELL'])
        hold_count = len([s for s in history if s['signal'] == 'HOLD'])

        avg_conf = sum(s['confidence'] for s in history) / len(history)

        return {
            'total_signals': len(history),
            'signal_count': len(history),
            'avg_confidence': round(avg_conf, 2),
            'by_signal': {
                'BUY': buy_count,
                'SELL': sell_count,
                'HOLD': hold_count
            },
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

    def clear_history(self) -> bool:
        """清空历史记录"""
        try:
            self._save_history([])
            if self.stats_file.exists():
                self.stats_file.unlink()
            logger.info("信号历史已清空")
            return True
        except Exception as e:
            logger.error(f"清空历史失败: {e}")
            return False


signals_db = SignalsDatabase()


def save_signal_to_db(signal_data: Dict) -> bool:
    """便捷函数：保存信号到数据库"""
    return signals_db.save_signal(signal_data)


def get_signal_history(limit: int = 100, signal_type: str = None) -> List[Dict]:
    """便捷函数：获取信号历史"""
    return signals_db.get_signal_history(limit, signal_type)


def get_latest_signal() -> Optional[Dict]:
    """便捷函数：获取最新信号"""
    return signals_db.get_latest_signal()


def get_signal_performance(days: int = 30) -> Dict:
    """便捷函数：获取信号表现"""
    return signals_db.get_signal_performance(days)
