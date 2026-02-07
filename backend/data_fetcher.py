import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict, List
from datetime import datetime, timezone, timedelta
import json
import re
import random
import numpy as np

logger = logging.getLogger(__name__)

class GoldDataFetcher:
    """获取黄金实时价格数据 - 多源聚合（增强版）"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.timeout = 10
        self._current_price_cache = None
        self._historical_data_cache = None
        
    def fetch_from_kitco(self) -> Optional[float]:
        """从Kitco获取金价"""
        try:
            response = requests.get("https://www.kitco.com/", headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 尝试多种可能的选择器
            selectors = [
                ('span', {'class_': 'gold-price'}),
                ('span', {'id_': 'sp-ask'}),
                ('span', {'class_': 'price-value'})
            ]
            
            for tag, attrs in selectors:
                element = soup.find(tag, attrs)
                if element:
                    price_text = element.get_text().strip()
                    price = float(re.sub(r'[^\d.]', '', price_text))
                    if 2000 < price < 3500:  # 合理范围检查
                        return price
            
            return None
        except Exception as e:
            logger.warning(f"Kitco爬取失败: {e}")
            return None
    
    def fetch_from_freegoldapi(self) -> Optional[float]:
        """从freegoldapi.com获取金价（免费API）"""
        try:
            response = requests.get(
                "https://freegoldapi.com/api/v0/goldprice/5000",
                headers=self.headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    price = float(data['price'])
                    if 4000 < price < 6000:
                        return price
            return None
        except Exception as e:
            logger.warning(f"freegoldapi爬取失败: {e}")
            return None
    
    def fetch_from_xe(self) -> Optional[float]:
        """从XE.com获取金价"""
        try:
            response = requests.get("https://www.xe.com/currency/xau-gold/", headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # XE通常显示1 XAU = X USD
            element = soup.find('p', class_='result__BigRate-sc-1bsijpp-1')
            if element:
                price_text = element.get_text().strip()
                price = float(re.sub(r'[^\d.]', '', price_text))
                if 2000 < price < 3500:
                    return price
            
            return None
        except Exception as e:
            logger.warning(f"XE.com爬取失败: {e}")
            return None
    
    def fetch_from_tradingeconomics(self) -> Optional[float]:
        """从TradingEconomics获取金价"""
        try:
            response = requests.get("https://tradingeconomics.com/commodity/gold", headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            element = soup.find('span', id='p') or soup.find('div', class_='price')
            if element:
                price_text = element.get_text().strip()
                price = float(re.sub(r'[^\d.]', '', price_text))
                if 2000 < price < 3500:
                    return price
            
            return None
        except Exception as e:
            logger.warning(f"TradingEconomics爬取失败: {e}")
            return None
    
    def fetch_from_fxstreet(self) -> Optional[float]:
        """从FXStreet获取金价"""
        try:
            response = requests.get("https://www.fxstreet.com/rates-charts/gold-price", headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            element = soup.find('span', class_='fxs_quote_val')
            if element:
                price_text = element.get_text().strip()
                price = float(re.sub(r'[^\d.]', '', price_text))
                if 2000 < price < 3500:
                    return price
            
            return None
        except Exception as e:
            logger.warning(f"FXStreet爬取失败: {e}")
            return None
    
    def fetch_from_goldprice_org_api(self) -> Optional[float]:
        """从goldprice.org API获取金价（最可靠的数据源）"""
        try:
            response = requests.get(
                "https://data-asg.goldprice.org/dbXRates/USD",
                headers=self.headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and len(data['items']) > 0:
                    xau_price = data['items'][0].get('xauPrice')
                    if xau_price and 2000 < xau_price < 10000:
                        return float(xau_price)
            return None
        except Exception as e:
            logger.warning(f"GoldPrice.org API爬取失败: {e}")
            return None
    
    def fetch_from_goldprice_org(self) -> Optional[float]:
        """从goldprice.org获取金价"""
        try:
            response = requests.get(
                "https://www.goldprice.org/",
                headers=self.headers,
                timeout=self.timeout
            )
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找金价元素
            element = soup.find('div', id='gp-gold-price-usd')
            if not element:
                element = soup.find('span', class_='price')
            
            if element:
                price_text = element.get_text().strip()
                # 移除货币符号和逗号
                price_text = re.sub(r'[^\d.]', '', price_text)
                price = float(price_text)
                if 2000 < price < 3500:
                    return price
            
            return None
        except Exception as e:
            logger.warning(f"GoldPrice.org爬取失败: {e}")
            return None
    
    def fetch_from_investing_com(self) -> Optional[float]:
        """从investing.com获取金价"""
        try:
            response = requests.get(
                "https://www.investing.com/commodities/gold",
                headers=self.headers,
                timeout=self.timeout
            )
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 尝试多种可能的选择器
            selectors = [
                ('div', {'data-test': 'instrument-price-last'}),
                ('div', {'class_': 'text-2xl'}),
                ('div', {'class_': 'instrument-price_last__KQzyA'})
            ]
            
            for tag, attrs in selectors:
                element = soup.find(tag, attrs)
                if element:
                    price_text = element.get_text().strip()
                    price_text = re.sub(r'[^\d.]', '', price_text)
                    price = float(price_text)
                    if 2000 < price < 3500:
                        return price
            
            return None
        except Exception as e:
            logger.warning(f"Investing.com爬取失败: {e}")
            return None
    
    def fetch_from_metalsapi(self) -> Optional[float]:
        """从Metals-API获取金价"""
        try:
            response = requests.get(
                "https://www.metals-api.com/api/latest?base=XAU&access_key=demo",
                headers=self.headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and 'USD' in data['rates']:
                    price_per_oz = data['rates']['USD']
                    if 2000 < price_per_oz < 10000:
                        return float(price_per_oz)
            return None
        except Exception as e:
            logger.warning(f"Metals-API爬取失败: {e}")
            return None

    def fetch_from_goldprices_org_scraper(self) -> Optional[float]:
        """从goldprices.org获取金价（备用爬虫）"""
        try:
            response = requests.get(
                "https://www.goldprices.org/",
                headers=self.headers,
                timeout=self.timeout
            )
            soup = BeautifulSoup(response.content, 'html.parser')

            # 尝试多种选择器
            selectors = [
                ('span', {'class_': 'gold-price'}),
                ('div', {'class_': 'price-value'}),
                ('p', {'class_': 'current-price'})
            ]

            for tag, attrs in selectors:
                element = soup.find(tag, attrs)
                if element:
                    price_text = element.get_text().strip()
                    price = float(re.sub(r'[^\d.]', '', price_text))
                    if 2000 < price < 10000:
                        return price

            return None
        except Exception as e:
            logger.warning(f"GoldPrices.org爬取失败: {e}")
            return None

    def fetch_from_bullionvault(self) -> Optional[float]:
        """从BullionVault获取金价"""
        try:
            response = requests.get(
                "https://www.bullionvault.com/gold-price-chart.do",
                headers=self.headers,
                timeout=self.timeout
            )
            soup = BeautifulSoup(response.content, 'html.parser')
            
            element = soup.find('span', class_='price') or soup.find('div', class_='spotPrice')
            if element:
                price_text = element.get_text().strip()
                price_text = re.sub(r'[^\d.]', '', price_text)
                price = float(price_text)
                if 2000 < price < 3500:
                    return price
            
            return None
        except Exception as e:
            logger.warning(f"BullionVault爬取失败: {e}")
            return None
    
    def fetch_real_time_price(self) -> Optional[Dict]:
        """从多个来源获取实时黄金价格并聚合"""
        sources = [
            ('GoldPrice.org API', self.fetch_from_goldprice_org_api),  # 最可靠的源放第一位
            ('GoldPrice.org', self.fetch_from_goldprice_org),
            ('GoldPrices.org', self.fetch_from_goldprices_org_scraper),
            ('Investing.com', self.fetch_from_investing_com),
            ('BullionVault', self.fetch_from_bullionvault),
            ('Kitco', self.fetch_from_kitco),
            ('XE.com', self.fetch_from_xe),
            ('TradingEconomics', self.fetch_from_tradingeconomics),
            ('FXStreet', self.fetch_from_fxstreet),
            ('Gold-API', self.fetch_from_freegoldapi),
            ('Metals-API', self.fetch_from_metalsapi),
        ]
        
        prices = []
        successful_sources = []
        
        # 尝试从所有来源获取价格
        for source_name, fetch_func in sources:
            try:
                price = fetch_func()
                if price and 2000 < price < 10000:  # 扩大合理范围以适应未来价格
                    prices.append(price)
                    successful_sources.append(source_name)
                    logger.info(f"成功从 {source_name} 获取金价: ${price}")
                    # 如果已经成功获取到API数据，可以提前结束
                    if source_name == 'GoldPrice.org API':
                        break
            except Exception as e:
                logger.warning(f"从 {source_name} 获取失败: {e}")
                continue
        
        # 如果没有成功获取任何价格，返回模拟数据
        if not prices:
            logger.warning("所有数据源均失败，使用模拟数据")
            base_price = 2650.0
            variation = random.uniform(-10, 10)
            current_price = base_price + variation
            
            return {
                'price': round(current_price, 2),
                'change': round(variation, 2),
                'change_percent': round((variation / base_price) * 100, 3),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'currency': 'USD',
                'unit': 'ounce',
                'sources': ['模拟数据'],
                'source_count': 0
            }
        
        # 计算平均价格（简单平均，忽略权重）
        avg_price = sum(prices) / len(prices)
        
        # 从GoldPrice.org API获取实时变化数据
        try:
            response = requests.get(
                "https://data-asg.goldprice.org/dbXRates/USD",
                headers=self.headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and len(data['items']) > 0:
                    item = data['items'][0]
                    change = item.get('chgXau', 0)
                    change_percent = item.get('pcXau', 0)
                    
                    return {
                        'price': round(avg_price, 2),
                        'change': round(float(change), 2),
                        'change_percent': round(float(change_percent), 3),
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'currency': 'USD',
                        'unit': 'ounce',
                        'sources': successful_sources,
                        'source_count': len(successful_sources),
                        'price_range': {
                            'min': round(min(prices), 2),
                            'max': round(max(prices), 2)
                        } if len(prices) > 1 else None
                    }
        except:
            pass
        
        # 如果无法获取实时变化，计算估算值
        base_price = 5000.0  # 当前金价约5000美元
        change = avg_price - base_price
        change_percent = (change / base_price) * 100
        
        return {
            'price': round(avg_price, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 3),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'currency': 'USD',
            'unit': 'ounce',
            'sources': successful_sources,
            'source_count': len(successful_sources),
            'price_range': {
                'min': round(min(prices), 2),
                'max': round(max(prices), 2)
            } if len(prices) > 1 else None
        }
    
    def fetch_historical_data(self, days: int = 90) -> list:
        """获取历史价格数据 - 基于真实趋势的增强模拟"""
        
        # 获取当前真实价格作为基准
        current_price = self._current_price_cache
        if current_price is None:
            current_price_data = self.fetch_real_time_price()
            if current_price_data:
                current_price = current_price_data['price']
                self._current_price_cache = current_price
            else:
                current_price = 5000.0  # 当前金价约5000美元
        
        # 历史价格趋势（从 freegoldapi 获取年度数据作为参考）
        historical_prices = self._fetch_historical_prices(days)
        
        if historical_prices:
            # 使用真实历史数据
            data = []
            for i, price in enumerate(historical_prices):
                if isinstance(price, dict) and 'close' in price:
                    data.append({
                        'timestamp': price.get('timestamp', datetime.now(timezone.utc).isoformat()),
                        'open': price.get('open', price['close']),
                        'high': price.get('high', price['close'] * 1.005),
                        'low': price.get('low', price['close'] * 0.995),
                        'close': price['close'],
                        'volume': price.get('volume', random.randint(30000, 50000))
                    })
            return data
        
        # 生成基于真实价格趋势的模拟数据
        data = []
        current_time = datetime.now(timezone.utc)
        
        # 黄金价格历史趋势（约2024年中从2600涨到2026年初的5000+）
        # 使用非线性增长模型
        for i in range(days):
            timestamp = current_time - timedelta(days=days-i)
            
            # 计算历史价格（向过去追溯）
            days_ago = days - i
            if days_ago < 180:
                # 近半年：快速上涨期
                price = current_price * (1 - 0.15 * (days_ago / 180))
            elif days_ago < 365:
                # 近一年：上涨期
                price = current_price * 0.85 * (1 - 0.10 * ((days_ago - 180) / 185))
            else:
                # 更早：温和期
                price = current_price * 0.75 * (1 - 0.05 * ((days_ago - 365) / (days - 365)))
            
            # 添加每日波动
            daily_volatility = price * 0.015  # 约1.5%日波动
            close_price = price + random.gauss(0, daily_volatility)
            
            # 生成OHLC
            open_price = close_price + random.gauss(0, daily_volatility * 0.5)
            high_price = max(open_price, close_price) + random.uniform(0, daily_volatility * 0.3)
            low_price = min(open_price, close_price) - random.uniform(0, daily_volatility * 0.3)
            
            data.append({
                'timestamp': timestamp.isoformat(),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': int(random.gauss(40000, 10000))
            })
        
        return data
    
    def _fetch_historical_prices(self, days: int = 90) -> Optional[List[Dict]]:
        """从真实CSV历史数据获取每日价格"""
        try:
            import pandas as pd
            from pathlib import Path
            
            historical_path = "/Users/mac/AI/gold-trading-system/data/history/GOLD"
            daily_file = Path(historical_path) / 'GOLD_Daily_200701280000_202601300000.csv'
            
            if daily_file.exists():
                df = pd.read_csv(daily_file, sep='\t')
                df.columns = df.columns.str.strip().str.replace('<', '').str.replace('>', '')
                df['DATE'] = pd.to_datetime(df['DATE'], format='%Y.%m.%d')
                df = df.sort_values('DATE', ascending=True)
                
                # 取最近的days条数据
                if len(df) > days:
                    df = df.tail(days)
                
                historical_data = []
                for _, row in df.iterrows():
                    historical_data.append({
                        'timestamp': row['DATE'].replace(tzinfo=timezone.utc).isoformat(),
                        'open': float(row['OPEN']),
                        'high': float(row['HIGH']),
                        'low': float(row['LOW']),
                        'close': float(row['CLOSE']),
                        'volume': int(row['VOL']) if row['VOL'] else int(row.get('TICKVOL', 0))
                    })
                
                logger.info(f"从CSV加载真实历史数据: {len(historical_data)} 条")
                return historical_data
            
        except Exception as e:
            logger.warning(f"从CSV加载历史数据失败: {e}")
        
        return None