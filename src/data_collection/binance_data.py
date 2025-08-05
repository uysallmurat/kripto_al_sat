"""
Binance API'den kripto para verilerini çeken modül
Bu modül, Binance borsasından geçmiş fiyat verilerini alır
"""

import pandas as pd
import numpy as np
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Çevre değişkenlerini yükle
load_dotenv()

class BinanceDataCollector:
    """
    Binance API'den kripto para verilerini toplayan sınıf
    """
    
    def __init__(self, api_key=None, secret_key=None):
        """
        BinanceDataCollector sınıfını başlatır
        
        Args:
            api_key (str): Binance API anahtarı
            secret_key (str): Binance gizli anahtarı
        """
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.secret_key = secret_key or os.getenv('BINANCE_SECRET_KEY')
        
        # API anahtarları yoksa sadece public veriler için client oluştur
        if self.api_key and self.secret_key:
            self.client = Client(self.api_key, self.secret_key)
        else:
            self.client = Client()
            
        # Loglama ayarları
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def get_historical_data(self, symbol, interval, start_date=None, end_date=None, limit=1000):
        """
        Belirtilen kripto para için geçmiş verileri çeker
        
        Args:
            symbol (str): Kripto para çifti (örn: 'BTCUSDT')
            interval (str): Zaman aralığı ('1h', '4h', '1d', vb.)
            start_date (str): Başlangıç tarihi (YYYY-MM-DD)
            end_date (str): Bitiş tarihi (YYYY-MM-DD)
            limit (int): Maksimum veri sayısı
            
        Returns:
            pandas.DataFrame: OHLCV verileri
        """
        try:
            self.logger.info(f"{symbol} için {interval} aralığında veri çekiliyor...")
            
            # Tarih formatını ayarla
            if start_date:
                start_str = start_date
            else:
                # Varsayılan olarak 30 gün öncesi
                start_str = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
            if end_date:
                end_str = end_date
            else:
                end_str = datetime.now().strftime('%Y-%m-%d')
            
            # Binance API'den veri çek
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str,
                end_str=end_str,
                limit=limit
            )
            
            # Verileri DataFrame'e dönüştür
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Veri tiplerini düzenle
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            # Gereksiz sütunları kaldır
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df.set_index('timestamp', inplace=True)
            
            self.logger.info(f"{len(df)} adet veri başarıyla çekildi")
            return df
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API hatası: {e}")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Beklenmeyen hata: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol):
        """
        Belirtilen kripto paranın güncel fiyatını alır
        
        Args:
            symbol (str): Kripto para çifti (örn: 'BTCUSDT')
            
        Returns:
            float: Güncel fiyat
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            self.logger.error(f"Fiyat alma hatası: {e}")
            return None
    
    def get_24h_stats(self, symbol):
        """
        Son 24 saatlik istatistikleri alır
        
        Args:
            symbol (str): Kripto para çifti (örn: 'BTCUSDT')
            
        Returns:
            dict: 24 saatlik istatistikler
        """
        try:
            stats = self.client.get_ticker(symbol=symbol)
            return {
                'price_change': float(stats['priceChange']),
                'price_change_percent': float(stats['priceChangePercent']),
                'high_24h': float(stats['highPrice']),
                'low_24h': float(stats['lowPrice']),
                'volume': float(stats['volume']),
                'quote_volume': float(stats['quoteVolume'])
            }
        except Exception as e:
            self.logger.error(f"24h istatistik hatası: {e}")
            return {}
    
    def get_top_gainers_losers(self, limit=10):
        """
        En çok yükselen ve düşen kripto paraları listeler
        
        Args:
            limit (int): Liste uzunluğu
            
        Returns:
            tuple: (gainers, losers) listeleri
        """
        try:
            # Tüm ticker'ları al
            tickers = self.client.get_ticker()
            
            # USDT çiftlerini filtrele
            usdt_pairs = [t for t in tickers if t['symbol'].endswith('USDT')]
            
            # Yüzde değişime göre sırala
            gainers = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)[:limit]
            losers = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']))[:limit]
            
            return gainers, losers
            
        except Exception as e:
            self.logger.error(f"Top gainers/losers hatası: {e}")
            return [], []
    
    def save_data_to_csv(self, df, symbol, interval, filename=None):
        """
        Verileri CSV dosyasına kaydeder
        
        Args:
            df (pandas.DataFrame): Kaydedilecek veri
            symbol (str): Kripto para çifti
            interval (str): Zaman aralığı
            filename (str): Dosya adı (opsiyonel)
        """
        if filename is None:
            filename = f"{symbol}_{interval}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        filepath = os.path.join('data', 'historical', filename)
        
        try:
            df.to_csv(filepath)
            self.logger.info(f"Veriler {filepath} dosyasına kaydedildi")
        except Exception as e:
            self.logger.error(f"Dosya kaydetme hatası: {e}")

# Test fonksiyonu
if __name__ == "__main__":
    # Test için örnek kullanım
    collector = BinanceDataCollector()
    
    # BTC/USDT verilerini çek
    btc_data = collector.get_historical_data('BTCUSDT', '1h', limit=100)
    print(f"Çekilen veri sayısı: {len(btc_data)}")
    print(btc_data.head())
    
    # Güncel fiyatı al
    current_price = collector.get_current_price('BTCUSDT')
    print(f"Güncel BTC fiyatı: ${current_price}") 