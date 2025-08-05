"""
Teknik analiz sinyal üretimi modülü
Bu modül teknik göstergelere dayalı alım/satım sinyalleri üretir
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional

class SignalGenerator:
    """
    Teknik analiz sinyallerini üreten sınıf
    """
    
    def __init__(self):
        """SignalGenerator sınıfını başlatır"""
        self.logger = logging.getLogger(__name__)
        
    def generate_signals(self, df: pd.DataFrame) -> Dict:
        """
        Teknik analiz sinyallerini üretir
        
        Args:
            df (pd.DataFrame): Teknik göstergeler eklenmiş DataFrame
            
        Returns:
            Dict: Üretilen sinyaller
        """
        try:
            signals = {}
            
            # RSI sinyalleri
            signals['rsi'] = self._generate_rsi_signals(df)
            
            # MACD sinyalleri
            signals['macd'] = self._generate_macd_signals(df)
            
            # Bollinger Bands sinyalleri
            signals['bollinger'] = self._generate_bollinger_signals(df)
            
            # Hareketli ortalama sinyalleri
            signals['moving_averages'] = self._generate_ma_signals(df)
            
            # Genel sinyal özeti
            signals['summary'] = self._create_signal_summary(signals)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Sinyal üretim hatası: {e}")
            return {}
    
    def _generate_rsi_signals(self, df: pd.DataFrame) -> Dict:
        """RSI sinyallerini üretir"""
        try:
            latest = df.iloc[-1]
            rsi = latest['rsi']
            
            if rsi < 30:
                return {
                    'signal': 'BUY',
                    'strength': 'STRONG',
                    'confidence': 0.8,
                    'reason': 'RSI aşırı satım bölgesinde (30 altı)'
                }
            elif rsi > 70:
                return {
                    'signal': 'SELL',
                    'strength': 'STRONG',
                    'confidence': 0.8,
                    'reason': 'RSI aşırı alım bölgesinde (70 üstü)'
                }
            else:
                return {
                    'signal': 'HOLD',
                    'strength': 'WEAK',
                    'confidence': 0.3,
                    'reason': 'RSI nötr bölgede'
                }
                
        except Exception as e:
            self.logger.error(f"RSI sinyal hatası: {e}")
            return {'signal': 'HOLD', 'strength': 'WEAK', 'confidence': 0.0}
    
    def _generate_macd_signals(self, df: pd.DataFrame) -> Dict:
        """MACD sinyallerini üretir"""
        try:
            latest = df.iloc[-1]
            macd = latest['macd']
            macd_signal = latest['macd_signal']
            
            if macd > macd_signal:
                return {
                    'signal': 'BUY',
                    'strength': 'MEDIUM',
                    'confidence': 0.6,
                    'reason': 'MACD sinyal çizgisinin üstünde'
                }
            else:
                return {
                    'signal': 'SELL',
                    'strength': 'MEDIUM',
                    'confidence': 0.6,
                    'reason': 'MACD sinyal çizgisinin altında'
                }
                
        except Exception as e:
            self.logger.error(f"MACD sinyal hatası: {e}")
            return {'signal': 'HOLD', 'strength': 'WEAK', 'confidence': 0.0}
    
    def _generate_bollinger_signals(self, df: pd.DataFrame) -> Dict:
        """Bollinger Bands sinyallerini üretir"""
        try:
            latest = df.iloc[-1]
            close = latest['close']
            bb_upper = latest['bb_upper']
            bb_lower = latest['bb_lower']
            
            if close < bb_lower:
                return {
                    'signal': 'BUY',
                    'strength': 'MEDIUM',
                    'confidence': 0.7,
                    'reason': 'Fiyat Bollinger alt bandının altında'
                }
            elif close > bb_upper:
                return {
                    'signal': 'SELL',
                    'strength': 'MEDIUM',
                    'confidence': 0.7,
                    'reason': 'Fiyat Bollinger üst bandının üstünde'
                }
            else:
                return {
                    'signal': 'HOLD',
                    'strength': 'WEAK',
                    'confidence': 0.4,
                    'reason': 'Fiyat Bollinger bantları arasında'
                }
                
        except Exception as e:
            self.logger.error(f"Bollinger sinyal hatası: {e}")
            return {'signal': 'HOLD', 'strength': 'WEAK', 'confidence': 0.0}
    
    def _generate_ma_signals(self, df: pd.DataFrame) -> Dict:
        """Hareketli ortalama sinyallerini üretir"""
        try:
            latest = df.iloc[-1]
            close = latest['close']
            ema_12 = latest['ema_12']
            ema_26 = latest['ema_26']
            sma_50 = latest['sma_50']
            
            # EMA crossover
            if ema_12 > ema_26:
                return {
                    'signal': 'BUY',
                    'strength': 'MEDIUM',
                    'confidence': 0.6,
                    'reason': 'EMA 12, EMA 26\'nın üstünde'
                }
            else:
                return {
                    'signal': 'SELL',
                    'strength': 'MEDIUM',
                    'confidence': 0.6,
                    'reason': 'EMA 12, EMA 26\'nın altında'
                }
                
        except Exception as e:
            self.logger.error(f"MA sinyal hatası: {e}")
            return {'signal': 'HOLD', 'strength': 'WEAK', 'confidence': 0.0}
    
    def _create_signal_summary(self, signals: Dict) -> Dict:
        """Sinyal özeti oluşturur"""
        try:
            buy_count = sum(1 for s in signals.values() if isinstance(s, dict) and s.get('signal') == 'BUY')
            sell_count = sum(1 for s in signals.values() if isinstance(s, dict) and s.get('signal') == 'SELL')
            
            if buy_count > sell_count:
                overall_signal = 'BUY'
                confidence = min(0.9, buy_count / len(signals) * 0.8)
            elif sell_count > buy_count:
                overall_signal = 'SELL'
                confidence = min(0.9, sell_count / len(signals) * 0.8)
            else:
                overall_signal = 'HOLD'
                confidence = 0.5
            
            return {
                'overall_signal': overall_signal,
                'confidence': confidence,
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'total_signals': len(signals) - 1  # summary hariç
            }
            
        except Exception as e:
            self.logger.error(f"Sinyal özeti hatası: {e}")
            return {'overall_signal': 'HOLD', 'confidence': 0.0} 