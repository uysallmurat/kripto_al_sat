"""
Alım/satım sinyalleri üreten modül
Bu modül teknik analiz ve AI tahminlerini birleştirerek sinyaller üretir
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

class SignalType(Enum):
    """Sinyal türleri"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class SignalStrength(Enum):
    """Sinyal gücü"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4

class SignalGenerator:
    """
    Alım/satım sinyalleri üreten ana sınıf
    """
    
    def __init__(self):
        """SignalGenerator sınıfını başlatır"""
        self.logger = logging.getLogger(__name__)
        self.signals = []
        
    def generate_signals(self, df: pd.DataFrame, predictions: Dict = None) -> List[Dict]:
        """
        Teknik analiz ve AI tahminlerine dayalı sinyaller üretir
        
        Args:
            df (pd.DataFrame): Teknik göstergeler eklenmiş DataFrame
            predictions (Dict): AI tahmin sonuçları
            
        Returns:
            List[Dict]: Üretilen sinyaller listesi
        """
        try:
            signals = []
            
            # Teknik analiz sinyalleri
            technical_signals = self._generate_technical_signals(df)
            signals.extend(technical_signals)
            
            # AI tahmin sinyalleri
            if predictions:
                ai_signals = self._generate_ai_signals(df, predictions)
                signals.extend(ai_signals)
            
            # Sinyalleri birleştir ve güven skorunu hesapla
            final_signals = self._combine_signals(signals)
            
            # Son sinyali kaydet
            if final_signals:
                self.signals = final_signals
                self.logger.info(f"{len(final_signals)} sinyal üretildi")
            
            return final_signals
            
        except Exception as e:
            self.logger.error(f"Sinyal üretme hatası: {e}")
            return []
    
    def _generate_technical_signals(self, df: pd.DataFrame) -> List[Dict]:
        """Teknik analiz tabanlı sinyaller üretir"""
        signals = []
        
        try:
            if len(df) < 50:  # Yeterli veri yoksa sinyal üretme
                return signals
            
            latest = df.iloc[-1]
            previous = df.iloc[-2]
            
            # RSI sinyalleri
            rsi_signal = self._analyze_rsi(latest, previous)
            if rsi_signal:
                signals.append(rsi_signal)
            
            # MACD sinyalleri
            macd_signal = self._analyze_macd(latest, previous)
            if macd_signal:
                signals.append(macd_signal)
            
            # Bollinger Bands sinyalleri
            bb_signal = self._analyze_bollinger_bands(latest, previous)
            if bb_signal:
                signals.append(bb_signal)
            
            # Moving Average sinyalleri
            ma_signal = self._analyze_moving_averages(latest, previous)
            if ma_signal:
                signals.append(ma_signal)
            
            # Stochastic sinyalleri
            stoch_signal = self._analyze_stochastic(latest, previous)
            if stoch_signal:
                signals.append(stoch_signal)
            
            # Volume sinyalleri
            volume_signal = self._analyze_volume(latest, df.tail(20))
            if volume_signal:
                signals.append(volume_signal)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Teknik sinyal üretme hatası: {e}")
            return []
    
    def _analyze_rsi(self, latest: pd.Series, previous: pd.Series) -> Optional[Dict]:
        """RSI analizi yapar"""
        try:
            current_rsi = latest['rsi']
            previous_rsi = previous['rsi']
            
            signal = None
            
            # Aşırı satım bölgesinden çıkış
            if previous_rsi < 30 and current_rsi > 30:
                signal = {
                    'type': SignalType.BUY,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'RSI',
                    'value': current_rsi,
                    'reason': 'Aşırı satım bölgesinden çıkış',
                    'confidence': 75
                }
            
            # Aşırı alım bölgesinden çıkış
            elif previous_rsi > 70 and current_rsi < 70:
                signal = {
                    'type': SignalType.SELL,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'RSI',
                    'value': current_rsi,
                    'reason': 'Aşırı alım bölgesinden çıkış',
                    'confidence': 75
                }
            
            # RSI yükseliş trendi
            elif current_rsi > previous_rsi and current_rsi > 50:
                signal = {
                    'type': SignalType.BUY,
                    'strength': SignalStrength.MODERATE,
                    'indicator': 'RSI',
                    'value': current_rsi,
                    'reason': 'RSI yükseliş trendi',
                    'confidence': 60
                }
            
            # RSI düşüş trendi
            elif current_rsi < previous_rsi and current_rsi < 50:
                signal = {
                    'type': SignalType.SELL,
                    'strength': SignalStrength.MODERATE,
                    'indicator': 'RSI',
                    'value': current_rsi,
                    'reason': 'RSI düşüş trendi',
                    'confidence': 60
                }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"RSI analiz hatası: {e}")
            return None
    
    def _analyze_macd(self, latest: pd.Series, previous: pd.Series) -> Optional[Dict]:
        """MACD analizi yapar"""
        try:
            current_macd = latest['macd']
            current_signal = latest['macd_signal']
            previous_macd = previous['macd']
            previous_signal = previous['macd_signal']
            
            signal = None
            
            # MACD sinyal çizgisini yukarı kesiyor
            if previous_macd < previous_signal and current_macd > current_signal:
                signal = {
                    'type': SignalType.BUY,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'MACD',
                    'value': current_macd,
                    'reason': 'MACD sinyal çizgisini yukarı kesti',
                    'confidence': 80
                }
            
            # MACD sinyal çizgisini aşağı kesiyor
            elif previous_macd > previous_signal and current_macd < current_signal:
                signal = {
                    'type': SignalType.SELL,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'MACD',
                    'value': current_macd,
                    'reason': 'MACD sinyal çizgisini aşağı kesti',
                    'confidence': 80
                }
            
            # MACD histogramı pozitif ve artıyor
            elif latest['macd_hist'] > 0 and latest['macd_hist'] > previous['macd_hist']:
                signal = {
                    'type': SignalType.BUY,
                    'strength': SignalStrength.MODERATE,
                    'indicator': 'MACD',
                    'value': current_macd,
                    'reason': 'MACD histogramı pozitif ve artıyor',
                    'confidence': 65
                }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"MACD analiz hatası: {e}")
            return None
    
    def _analyze_bollinger_bands(self, latest: pd.Series, previous: pd.Series) -> Optional[Dict]:
        """Bollinger Bands analizi yapar"""
        try:
            current_price = latest['close']
            current_upper = latest['bb_upper']
            current_lower = latest['bb_lower']
            current_position = latest['bb_position']
            
            signal = None
            
            # Fiyat alt banda dokunuyor
            if current_price <= current_lower * 1.01:
                signal = {
                    'type': SignalType.BUY,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'Bollinger Bands',
                    'value': current_position,
                    'reason': 'Fiyat alt Bollinger Bandına dokundu',
                    'confidence': 70
                }
            
            # Fiyat üst banda dokunuyor
            elif current_price >= current_upper * 0.99:
                signal = {
                    'type': SignalType.SELL,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'Bollinger Bands',
                    'value': current_position,
                    'reason': 'Fiyat üst Bollinger Bandına dokundu',
                    'confidence': 70
                }
            
            # Band genişliği daralıyor (sıkışma)
            elif latest['bb_width'] < previous['bb_width'] * 0.9:
                signal = {
                    'type': SignalType.HOLD,
                    'strength': SignalStrength.WEAK,
                    'indicator': 'Bollinger Bands',
                    'value': latest['bb_width'],
                    'reason': 'Bollinger Bands sıkışması - breakout bekleniyor',
                    'confidence': 50
                }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Bollinger Bands analiz hatası: {e}")
            return None
    
    def _analyze_moving_averages(self, latest: pd.Series, previous: pd.Series) -> Optional[Dict]:
        """Hareketli ortalama analizi yapar"""
        try:
            current_price = latest['close']
            ema_12 = latest['ema_12']
            ema_26 = latest['ema_26']
            sma_50 = latest['sma_50']
            sma_200 = latest['sma_200']
            
            signal = None
            
            # Altın kesişim (Golden Cross)
            if previous['ema_12'] <= previous['ema_26'] and ema_12 > ema_26:
                signal = {
                    'type': SignalType.STRONG_BUY,
                    'strength': SignalStrength.VERY_STRONG,
                    'indicator': 'Moving Averages',
                    'value': ema_12,
                    'reason': 'Altın kesişim (EMA 12 > EMA 26)',
                    'confidence': 85
                }
            
            # Ölüm kesişimi (Death Cross)
            elif previous['ema_12'] >= previous['ema_26'] and ema_12 < ema_26:
                signal = {
                    'type': SignalType.STRONG_SELL,
                    'strength': SignalStrength.VERY_STRONG,
                    'indicator': 'Moving Averages',
                    'value': ema_12,
                    'reason': 'Ölüm kesişimi (EMA 12 < EMA 26)',
                    'confidence': 85
                }
            
            # Fiyat 50 SMA'nın üstünde
            elif current_price > sma_50 and previous['close'] <= previous['sma_50']:
                signal = {
                    'type': SignalType.BUY,
                    'strength': SignalStrength.MODERATE,
                    'indicator': 'Moving Averages',
                    'value': sma_50,
                    'reason': 'Fiyat 50 SMA\'nın üstüne çıktı',
                    'confidence': 65
                }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Hareketli ortalama analiz hatası: {e}")
            return None
    
    def _analyze_stochastic(self, latest: pd.Series, previous: pd.Series) -> Optional[Dict]:
        """Stochastic analizi yapar"""
        try:
            current_k = latest['stoch_k']
            current_d = latest['stoch_d']
            previous_k = previous['stoch_k']
            previous_d = previous['stoch_d']
            
            signal = None
            
            # Aşırı satım bölgesinden çıkış
            if previous_k < 20 and current_k > 20:
                signal = {
                    'type': SignalType.BUY,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'Stochastic',
                    'value': current_k,
                    'reason': 'Stochastic aşırı satım bölgesinden çıkış',
                    'confidence': 70
                }
            
            # Aşırı alım bölgesinden çıkış
            elif previous_k > 80 and current_k < 80:
                signal = {
                    'type': SignalType.SELL,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'Stochastic',
                    'value': current_k,
                    'reason': 'Stochastic aşırı alım bölgesinden çıkış',
                    'confidence': 70
                }
            
            # K ve D çizgileri kesişimi
            elif previous_k < previous_d and current_k > current_d:
                signal = {
                    'type': SignalType.BUY,
                    'strength': SignalStrength.MODERATE,
                    'indicator': 'Stochastic',
                    'value': current_k,
                    'reason': 'Stochastic K ve D çizgileri yukarı kesişim',
                    'confidence': 60
                }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Stochastic analiz hatası: {e}")
            return None
    
    def _analyze_volume(self, latest: pd.Series, recent_data: pd.DataFrame) -> Optional[Dict]:
        """Hacim analizi yapar"""
        try:
            current_volume = latest['volume']
            avg_volume = recent_data['volume'].mean()
            volume_ratio = latest['volume_ratio']
            
            signal = None
            
            # Yüksek hacimle fiyat artışı
            if volume_ratio > 2.0 and latest['close'] > latest['open']:
                signal = {
                    'type': SignalType.BUY,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'Volume',
                    'value': volume_ratio,
                    'reason': 'Yüksek hacimle fiyat artışı',
                    'confidence': 75
                }
            
            # Yüksek hacimle fiyat düşüşü
            elif volume_ratio > 2.0 and latest['close'] < latest['open']:
                signal = {
                    'type': SignalType.SELL,
                    'strength': SignalStrength.STRONG,
                    'indicator': 'Volume',
                    'value': volume_ratio,
                    'reason': 'Yüksek hacimle fiyat düşüşü',
                    'confidence': 75
                }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Hacim analiz hatası: {e}")
            return None
    
    def _generate_ai_signals(self, df: pd.DataFrame, predictions: Dict) -> List[Dict]:
        """AI tahminlerine dayalı sinyaller üretir"""
        signals = []
        
        try:
            if 'ensemble_prediction' in predictions:
                ensemble_pred = predictions['ensemble_prediction']
                current_price = df['close'].iloc[-1]
                
                # Gelecek 24 saatlik tahmin
                next_24h_pred = ensemble_pred[0] if len(ensemble_pred) > 0 else current_price
                
                # Fiyat değişim yüzdesi
                price_change_pct = ((next_24h_pred - current_price) / current_price) * 100
                
                if price_change_pct > 5:  # %5'ten fazla artış bekleniyor
                    signals.append({
                        'type': SignalType.STRONG_BUY,
                        'strength': SignalStrength.VERY_STRONG,
                        'indicator': 'AI Prediction',
                        'value': price_change_pct,
                        'reason': f'AI {price_change_pct:.1f}% artış tahmin ediyor',
                        'confidence': 80
                    })
                elif price_change_pct > 2:  # %2-5 arası artış
                    signals.append({
                        'type': SignalType.BUY,
                        'strength': SignalStrength.STRONG,
                        'indicator': 'AI Prediction',
                        'value': price_change_pct,
                        'reason': f'AI {price_change_pct:.1f}% artış tahmin ediyor',
                        'confidence': 70
                    })
                elif price_change_pct < -5:  # %5'ten fazla düşüş
                    signals.append({
                        'type': SignalType.STRONG_SELL,
                        'strength': SignalStrength.VERY_STRONG,
                        'indicator': 'AI Prediction',
                        'value': price_change_pct,
                        'reason': f'AI {abs(price_change_pct):.1f}% düşüş tahmin ediyor',
                        'confidence': 80
                    })
                elif price_change_pct < -2:  # %2-5 arası düşüş
                    signals.append({
                        'type': SignalType.SELL,
                        'strength': SignalStrength.STRONG,
                        'indicator': 'AI Prediction',
                        'value': price_change_pct,
                        'reason': f'AI {abs(price_change_pct):.1f}% düşüş tahmin ediyor',
                        'confidence': 70
                    })
            
            return signals
            
        except Exception as e:
            self.logger.error(f"AI sinyal üretme hatası: {e}")
            return []
    
    def _combine_signals(self, signals: List[Dict]) -> List[Dict]:
        """Sinyalleri birleştirir ve güven skorunu hesaplar"""
        try:
            if not signals:
                return []
            
            # Sinyalleri türlerine göre grupla
            buy_signals = [s for s in signals if s['type'] in [SignalType.BUY, SignalType.STRONG_BUY]]
            sell_signals = [s for s in signals if s['type'] in [SignalType.SELL, SignalType.STRONG_SELL]]
            hold_signals = [s for s in signals if s['type'] == SignalType.HOLD]
            
            final_signals = []
            
            # Alım sinyalleri
            if buy_signals:
                avg_confidence = np.mean([s['confidence'] for s in buy_signals])
                strength_count = sum(1 for s in buy_signals if s['strength'] in [SignalStrength.STRONG, SignalStrength.VERY_STRONG])
                
                signal_type = SignalType.STRONG_BUY if strength_count >= 2 else SignalType.BUY
                
                final_signals.append({
                    'type': signal_type,
                    'confidence': min(avg_confidence + 10, 95),  # Bonus güven puanı
                    'signals_count': len(buy_signals),
                    'indicators': [s['indicator'] for s in buy_signals],
                    'reasons': [s['reason'] for s in buy_signals],
                    'timestamp': datetime.now()
                })
            
            # Satım sinyalleri
            if sell_signals:
                avg_confidence = np.mean([s['confidence'] for s in sell_signals])
                strength_count = sum(1 for s in sell_signals if s['strength'] in [SignalStrength.STRONG, SignalStrength.VERY_STRONG])
                
                signal_type = SignalType.STRONG_SELL if strength_count >= 2 else SignalType.SELL
                
                final_signals.append({
                    'type': signal_type,
                    'confidence': min(avg_confidence + 10, 95),
                    'signals_count': len(sell_signals),
                    'indicators': [s['indicator'] for s in sell_signals],
                    'reasons': [s['reason'] for s in sell_signals],
                    'timestamp': datetime.now()
                })
            
            # Bekleme sinyalleri
            if hold_signals and not buy_signals and not sell_signals:
                final_signals.append({
                    'type': SignalType.HOLD,
                    'confidence': 50,
                    'signals_count': len(hold_signals),
                    'indicators': [s['indicator'] for s in hold_signals],
                    'reasons': [s['reason'] for s in hold_signals],
                    'timestamp': datetime.now()
                })
            
            return final_signals
            
        except Exception as e:
            self.logger.error(f"Sinyal birleştirme hatası: {e}")
            return []
    
    def get_latest_signal(self) -> Optional[Dict]:
        """En son üretilen sinyali döndürür"""
        return self.signals[-1] if self.signals else None
    
    def get_signal_history(self, limit: int = 10) -> List[Dict]:
        """Sinyal geçmişini döndürür"""
        return self.signals[-limit:] if self.signals else []

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
        'volume': np.random.randint(1000, 10000, 100),
        'rsi': np.random.uniform(20, 80, 100),
        'macd': np.random.randn(100),
        'macd_signal': np.random.randn(100),
        'macd_histogram': np.random.randn(100),
        'bb_upper': np.random.randn(100).cumsum() + 105,
        'bb_lower': np.random.randn(100).cumsum() + 95,
        'bb_position': np.random.uniform(0, 1, 100),
        'bb_width': np.random.uniform(0.1, 0.3, 100),
        'ema_12': np.random.randn(100).cumsum() + 100,
        'ema_26': np.random.randn(100).cumsum() + 100,
        'sma_50': np.random.randn(100).cumsum() + 100,
        'sma_200': np.random.randn(100).cumsum() + 100,
        'stoch_k': np.random.uniform(0, 100, 100),
        'stoch_d': np.random.uniform(0, 100, 100),
        'volume_ratio': np.random.uniform(0.5, 3.0, 100)
    }, index=dates)
    
    # Sinyal üreticiyi test et
    generator = SignalGenerator()
    signals = generator.generate_signals(test_data)
    
    print(f"Üretilen sinyal sayısı: {len(signals)}")
    for signal in signals:
        print(f"Sinyal: {signal['type'].value}, Güven: {signal['confidence']:.1f}%")
        print(f"Göstergeler: {', '.join(signal['indicators'])}")
        print("---") 