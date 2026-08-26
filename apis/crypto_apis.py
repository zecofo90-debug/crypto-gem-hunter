import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class CoinGeckoAPI:
    """واجهة CoinGecko API للحصول على بيانات العملات الرقمية"""
    
    def __init__(self):
        self.base_url = Config.COINGECKO_API_URL
        self.session = requests.Session()
    
    def get_all_coins(self, per_page: int = 250, order: str = 'market_cap_desc') -> List[Dict]:
        """الحصول على قائمة جميع العملات الرقمية"""
        try:
            coins = []
            for page in range(1, 5):  # جلب 4 صفحات (1000 عملة)
                url = f"{self.base_url}/coins/markets"
                params = {
                    'vs_currency': 'usd',
                    'order': order,
                    'per_page': per_page,
                    'page': page,
                    'sparkline': False,
                    'locale': 'ar'
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                coins.extend(response.json())
            
            logger.info(f"تم جلب {len(coins)} عملة من CoinGecko")
            return coins
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على البيانات من CoinGecko: {str(e)}")
            return []
    
    def get_coin_details(self, coin_id: str) -> Optional[Dict]:
        """الحصول على تفاصيل عملة معينة"""
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': 'ar',
                'tickers': True,
                'market_data': True,
                'community_data': True,
                'developer_data': True
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على تفاصيل العملة {coin_id}: {str(e)}")
            return None
    
    def get_coin_history(self, coin_id: str, days: int = 30) -> Optional[Dict]:
        """الحصول على السعر التاريخي للعملة"""
        try:
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على السجل التاريخي للعملة {coin_id}: {str(e)}")
            return None
    
    def search_coin(self, query: str) -> Optional[List[Dict]]:
        """البحث عن عملة"""
        try:
            url = f"{self.base_url}/search"
            params = {'query': query}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('coins', [])
        
        except Exception as e:
            logger.error(f"خطأ في البحث عن العملة {query}: {str(e)}")
            return None
    
    def get_trending_coins(self) -> Optional[List[Dict]]:
        """الحصول على العملات الرائجة"""
        try:
            url = f"{self.base_url}/search/trending"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get('coins', [])
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على العملات الرائجة: {str(e)}")
            return None
    
    def get_new_coins(self) -> Optional[List[Dict]]:
        """الحصول على العملات الجديدة المدرجة حديثاً"""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'id_desc',  # أحدث العملات
                'per_page': 250,
                'page': 1,
                'sparkline': False
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            coins = response.json()
            
            # تصفية العملات التي أضيفت مؤخراً (آخر 30 يوم)
            new_coins = []
            for coin in coins:
                if coin.get('id') and coin.get('market_cap_rank'):
                    new_coins.append(coin)
            
            return new_coins[:50]  # إرجاع أول 50 عملة جديدة
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على العملات الجديدة: {str(e)}")
            return None


class BinanceAPI:
    """واجهة Binance API"""
    
    def __init__(self):
        self.base_url = Config.BINANCE_API_URL
        self.session = requests.Session()
    
    def get_trading_pairs(self) -> List[Dict]:
        """الحصول على أزواج التداول"""
        try:
            url = f"{self.base_url}/api/v3/exchangeInfo"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get('symbols', [])
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على أزواج التداول من Binance: {str(e)}")
            return []
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """الحصول على بيانات السعر الحالي"""
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            params = {'symbol': symbol}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على بيانات السعر {symbol}: {str(e)}")
            return None
    
    def get_klines(self, symbol: str, interval: str = '1d', limit: int = 100) -> List[List]:
        """الحصول على بيانات الشموع (Klines)"""
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على بيانات الشموع {symbol}: {str(e)}")
            return []
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """الحصول على أحدث الصفقات"""
        try:
            url = f"{self.base_url}/api/v3/trades"
            params = {'symbol': symbol, 'limit': limit}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على الصفقات الأخيرة {symbol}: {str(e)}")
            return []


class CoinMarketCapAPI:
    """واجهة CoinMarketCap API"""
    
    def __init__(self):
        self.base_url = Config.COINMARKETCAP_API_URL
        self.api_key = Config.COINMARKETCAP_API_KEY
        self.session = requests.Session()
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
    
    def get_latest_listings(self, start: int = 1, limit: int = 5000) -> Optional[List[Dict]]:
        """الحصول على آخر التصنيفات"""
        try:
            url = f"{self.base_url}/cryptocurrency/listings/latest"
            params = {
                'start': start,
                'limit': limit,
                'convert': 'USD'
            }
            
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('data', [])
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على التصنيفات من CoinMarketCap: {str(e)}")
            return None
    
    def get_metadata(self, id: str) -> Optional[Dict]:
        """الحصول على البيانات الوصفية للعملة"""
        try:
            url = f"{self.base_url}/cryptocurrency/info"
            params = {'id': id}
            
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('data', {}).get(id)
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على البيانات الوصفية {id}: {str(e)}")
            return None
