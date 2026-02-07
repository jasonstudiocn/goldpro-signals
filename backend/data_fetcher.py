import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict, List
from datetime import datetime, timezone, timedelta
import json
import re
import random

logger = logging.getLogger(__name__)

class GoldDataFetcher:
    """获取黄金实时价格数据 - 多源聚合"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.timeout = 10
        
    def fetch_from_kitco(self) -> Optional[float]:
        """从Kitco获取金价"""
        try:
            response = requests.get("https://www.kitco.com/", headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 尝试多种可能的选择器
            selectors = [
                {'class': 'gold-price'},
                {'id': 'sp-ask'},
                {'class': 'price-value'}
            ]
            
            for selector in selectors:
                element = soup.find('span', selector) or soup.find('div', selector)
                if element:
                    price_text = element.get_text().strip()
                    price = float(re.sub(r'[^\d.]', '', price_text))
                    if 2000 < price < 3500:  # 合理范围检查
                        return price
            
            return None
        except Exception as e:
            logger.warning(f"Kitco爬取失败: {e}")
            return None
    
    def fetch_from_goldapi(self) -> Optional[float]:
        """从Gold-API获取金价（可能需要API密钥）"""
        try:
            response = requests.get("https://www.goldapi.io/api/XAU/USD", headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return float(data.get('price', 0))
            return None
        except Exception as e:
            logger.warning(f"Gold-API爬取失败: {e}")
            return None
    
    def fetch_from_xe(self) -> Optional[float]:
        """从XE.com获取金价"""
        try:
            response = requests.get("https://www.xe.com/currency/xau-gold/", headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # XE通常显示1 XAU = X USD
            element = soup.find('p', {'class': 'result__BigRate-sc-1bsijpp-1'})
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
            
            element = soup.find('span', {'id': 'p'}) or soup.find('div', {'class': 'price'})
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
            
            element = soup.find('span', {'class': 'fxs_quote_val'})
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
            element = soup.find('div', {'id': 'gp-gold-price-usd'})
            if not element:
                element = soup.find('span', {'class': 'price'})
            
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
                {'attrs': {'data-test': 'instrument-price-last'}},
                {'class': 'text-2xl'},
                {'class': 'instrument-price_last__KQzyA'}
            ]
            
            for selector in selectors:
                element = soup.find('div', selector) or soup.find('span', selector)
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
    
    def fetch_from_bullionvault(self) -> Optional[float]:
        """从BullionVault获取金价"""
        try:
            response = requests.get(
                "https://www.bullionvault.com/gold-price-chart.do",
                headers=self.headers,
                timeout=self.timeout
            )
            soup = BeautifulSoup(response.content, 'html.parser')
            
            element = soup.find('span', {'class': 'price'}) or soup.find('div', {'class': 'spotPrice'})
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
            ('Investing.com', self.fetch_from_investing_com),
            ('BullionVault', self.fetch_from_bullionvault),
            ('Kitco', self.fetch_from_kitco),
            ('XE.com', self.fetch_from_xe),
            ('TradingEconomics', self.fetch_from_tradingeconomics),
            ('FXStreet', self.fetch_from_fxstreet),
            ('Gold-API', self.fetch_from_goldapi),
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
        base_price = 2650.0
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
    
    def fetch_historical_data(self, days: int = 30) -> list:
        """获取历史价格数据（模拟）"""
        data = []
        base_price = 2650.0
        current_time = datetime.now(timezone.utc)
        
        for i in range(days):
            timestamp = current_time - timedelta(days=days-i)
            variation = random.uniform(-20, 20)
            price = base_price + variation
            
            # 生成OHLC数据
            open_price = price + random.uniform(-5, 5)
            high = max(open_price, price) + random.uniform(0, 5)
            low = min(open_price, price) - random.uniform(0, 5)
            close = price
            
            data.append({
                'timestamp': timestamp.isoformat(),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': random.randint(10000, 50000)
            })
        
        return data
    
    def fetch_historical_data(self, days: int = 30) -> list:
        """获取历史价格数据（模拟）"""
        import random
        from datetime import timedelta
        
        data = []
        base_price = 2650.0
        current_time = datetime.now(timezone.utc)
        
        for i in range(days):
            timestamp = current_time - timedelta(days=days-i)
            variation = random.uniform(-20, 20)
            price = base_price + variation
            
            # 生成OHLC数据
            open_price = price + random.uniform(-5, 5)
            high = max(open_price, price) + random.uniform(0, 5)
            low = min(open_price, price) - random.uniform(0, 5)
            close = price
            
            data.append({
                'timestamp': timestamp.isoformat(),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': random.randint(10000, 50000)
            })
        
        return data