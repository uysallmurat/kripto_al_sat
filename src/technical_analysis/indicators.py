"""
Teknik analiz göstergelerini hesaplayan modül
Bu modül RSI, MACD, EMA, Bollinger Bands gibi göstergeleri hesaplar
"""

import pandas as pd
import numpy as np
import ta
import logging
from typing import Dict, List, Optional

class TechnicalIndicators:
    """
    Teknik analiz göstergelerini hesaplayan sınıf
    """
    
    def __init__(self):
        """TechnicalIndicators sınıfını başlatır"""
        self.logger = logging.getLogger(__name__)
        
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tüm teknik göstergeleri hesaplar
        
        Args:
            df (pd.DataFrame): OHLCV verileri içeren DataFrame
            
        Returns:
            pd.DataFrame: Teknik göstergeler eklenmiş DataFrame
        """
        try:
            # Veri kopyası oluştur
            result_df = df.copy()
            
            # Temel göstergeler
            result_df = self._add_moving_averages(result_df)
            result_df = self._add_rsi(result_df)
            result_df = self._add_macd(result_df)
            result_df = self._add_bollinger_bands(result_df)
            result_df = self._add_stochastic(result_df)
            result_df = self._add_williams_r(result_df)
            result_df = self._add_atr(result_df)
            result_df = self._add_volume_indicators(result_df)
            
            # NaN değerleri temizle
            result_df = result_df.dropna()
            
            self.logger.info(f"Tüm teknik göstergeler hesaplandı. Toplam {len(result_df)} veri noktası")
            return result_df
            
        except Exception as e:
            self.logger.error(f"Gösterge hesaplama hatası: {e}")
            return df
    
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Hareketli ortalamaları ekler"""
        try:
            # SMA (Simple Moving Average)
            df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
            df['sma_200'] = ta.trend.sma_indicator(df['close'], window=200)
            
            # EMA (Exponential Moving Average)
            df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
            df['ema_50'] = ta.trend.ema_indicator(df['close'], window=50)
            
            # WMA (Weighted Moving Average)
            df['wma_20'] = ta.trend.wma_indicator(df['close'], window=20)
            
            return df
        except Exception as e:
            self.logger.error(f"Hareketli ortalama hesaplama hatası: {e}")
            return df
    
    def _add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """RSI (Relative Strength Index) ekler"""
        try:
            df['rsi'] = ta.momentum.rsi(df['close'], window=period)
            
            # RSI seviyeleri
            df['rsi_overbought'] = 70
            df['rsi_oversold'] = 30
            
            return df
        except Exception as e:
            self.logger.error(f"RSI hesaplama hatası: {e}")
            return df
    
    def _add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """MACD (Moving Average Convergence Divergence) ekler"""
        try:
            macd = ta.trend.MACD(df['close'], window_fast=12, window_slow=26, window_sign=9)
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_hist'] = macd.macd_diff()
            
            return df
        except Exception as e:
            self.logger.error(f"MACD hesaplama hatası: {e}")
            return df
    
    def _add_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> pd.DataFrame:
        """Bollinger Bands ekler"""
        try:
            bb = ta.volatility.BollingerBands(df['close'], window=period, window_dev=std_dev)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            
            # Bollinger Band genişliği
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # Bollinger Band pozisyonu
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            return df
        except Exception as e:
            self.logger.error(f"Bollinger Bands hesaplama hatası: {e}")
            return df
    
    def _add_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Stochastic Oscillator ekler"""
        try:
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            return df
        except Exception as e:
            self.logger.error(f"Stochastic hesaplama hatası: {e}")
            return df
    
    def _add_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Williams %R ekler"""
        try:
            df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'], lbp=period)
            return df
        except Exception as e:
            self.logger.error(f"Williams %R hesaplama hatası: {e}")
            return df
    
    def _add_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """ATR (Average True Range) ekler"""
        try:
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=period)
            return df
        except Exception as e:
            self.logger.error(f"ATR hesaplama hatası: {e}")
            return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Hacim göstergelerini ekler"""
        try:
            # OBV (On Balance Volume)
            df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
            
            # Volume SMA
            df['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20)
            
            # Volume Ratio
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            return df
        except Exception as e:
            self.logger.error(f"Hacim göstergesi hesaplama hatası: {e}")
            return df
    
    def get_indicator_summary(self, df: pd.DataFrame) -> Dict:
        """
        Teknik göstergelerin özetini döndürür
        
        Args:
            df (pd.DataFrame): Teknik göstergeler eklenmiş DataFrame
            
        Returns:
            Dict: Gösterge özetleri
        """
        try:
            latest = df.iloc[-1]
            
            summary = {
                'price': {
                    'current': latest['close'],
                    'change_24h': (latest['close'] - df.iloc[-24]['close']) / df.iloc[-24]['close'] * 100 if len(df) > 24 else 0
                },
                'rsi': {
                    'value': latest['rsi'],
                    'status': 'Aşırı Alım' if latest['rsi'] > 70 else 'Aşırı Satım' if latest['rsi'] < 30 else 'Nötr'
                },
                'macd': {
                    'value': latest['macd'],
                    'signal': latest['macd_signal'],
                    'trend': 'Yükseliş' if latest['macd'] > latest['macd_signal'] else 'Düşüş'
                },
                'bollinger_bands': {
                    'position': latest['bb_position'],
                    'status': 'Üst Band' if latest['close'] > latest['bb_upper'] else 'Alt Band' if latest['close'] < latest['bb_lower'] else 'Orta'
                },
                'moving_averages': {
                    'ema_12': latest['ema_12'],
                    'ema_26': latest['ema_26'],
                    'sma_50': latest['sma_50'],
                    'sma_200': latest['sma_200']
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Gösterge özeti hatası: {e}")
            return {}
    
    def get_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """
        Destek ve direnç seviyelerini hesaplar
        
        Args:
            df (pd.DataFrame): OHLCV verileri
            window (int): Hesaplama penceresi
            
        Returns:
            Dict: Destek ve direnç seviyeleri
        """
        try:
            recent_data = df.tail(window)
            
            # Direnç seviyeleri (yüksek noktalar)
            resistance_levels = recent_data['high'].nlargest(3).tolist()
            
            # Destek seviyeleri (düşük noktalar)
            support_levels = recent_data['low'].nsmallest(3).tolist()
            
            current_price = df['close'].iloc[-1]
            
            return {
                'current_price': current_price,
                'resistance_levels': sorted(resistance_levels, reverse=True),
                'support_levels': sorted(support_levels),
                'nearest_resistance': min([r for r in resistance_levels if r > current_price], default=None),
                'nearest_support': max([s for s in support_levels if s < current_price], default=None)
            }
            
        except Exception as e:
            self.logger.error(f"Destek/Direnç hesaplama hatası: {e}")
            return {}

# Test fonksiyonu
if __name__ == "__main__":
    # Test için örnek veri oluştur
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    np.random.seed(42)
    
    test_data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    # Teknik göstergeleri hesapla
    indicators = TechnicalIndicators()
    result = indicators.calculate_all_indicators(test_data)
    
    print("Teknik göstergeler hesaplandı!")
    print(f"Toplam sütun sayısı: {len(result.columns)}")
    print(f"Veri noktası sayısı: {len(result)}")
    print("\nSon 5 satır:")
    print(result.tail()) 