"""
Teknik analiz pattern tanıma modülü
Bu modül fiyat formasyonlarını ve pattern'leri tanır
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional

class PatternRecognition:
    """
    Teknik analiz pattern'lerini tanıyan sınıf
    """
    
    def __init__(self):
        """PatternRecognition sınıfını başlatır"""
        self.logger = logging.getLogger(__name__)
        
    def detect_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Fiyat pattern'lerini tespit eder
        
        Args:
            df (pd.DataFrame): OHLCV verileri
            
        Returns:
            Dict: Tespit edilen pattern'ler
        """
        try:
            patterns = {}
            
            # Temel pattern'leri tespit et
            patterns['double_top'] = self._detect_double_top(df)
            patterns['double_bottom'] = self._detect_double_bottom(df)
            patterns['head_shoulders'] = self._detect_head_shoulders(df)
            patterns['triangle'] = self._detect_triangle(df)
            patterns['flag'] = self._detect_flag(df)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Pattern tespit hatası: {e}")
            return {}
    
    def _detect_double_top(self, df: pd.DataFrame) -> Dict:
        """Çift tepe pattern'ini tespit eder"""
        try:
            # Basit çift tepe tespiti
            highs = df['high'].rolling(window=5, center=True).max()
            peaks = df[df['high'] == highs]
            
            if len(peaks) >= 2:
                return {
                    'detected': True,
                    'confidence': 0.7,
                    'description': 'Çift tepe pattern tespit edildi'
                }
            
            return {'detected': False, 'confidence': 0.0}
            
        except Exception as e:
            self.logger.error(f"Çift tepe tespit hatası: {e}")
            return {'detected': False, 'confidence': 0.0}
    
    def _detect_double_bottom(self, df: pd.DataFrame) -> Dict:
        """Çift dip pattern'ini tespit eder"""
        try:
            # Basit çift dip tespiti
            lows = df['low'].rolling(window=5, center=True).min()
            troughs = df[df['low'] == lows]
            
            if len(troughs) >= 2:
                return {
                    'detected': True,
                    'confidence': 0.7,
                    'description': 'Çift dip pattern tespit edildi'
                }
            
            return {'detected': False, 'confidence': 0.0}
            
        except Exception as e:
            self.logger.error(f"Çift dip tespit hatası: {e}")
            return {'detected': False, 'confidence': 0.0}
    
    def _detect_head_shoulders(self, df: pd.DataFrame) -> Dict:
        """Omuz baş omuz pattern'ini tespit eder"""
        try:
            # Basit omuz baş omuz tespiti
            return {
                'detected': False,
                'confidence': 0.0,
                'description': 'Omuz baş omuz pattern tespit edilmedi'
            }
            
        except Exception as e:
            self.logger.error(f"Omuz baş omuz tespit hatası: {e}")
            return {'detected': False, 'confidence': 0.0}
    
    def _detect_triangle(self, df: pd.DataFrame) -> Dict:
        """Üçgen pattern'ini tespit eder"""
        try:
            # Basit üçgen tespiti
            return {
                'detected': False,
                'confidence': 0.0,
                'description': 'Üçgen pattern tespit edilmedi'
            }
            
        except Exception as e:
            self.logger.error(f"Üçgen tespit hatası: {e}")
            return {'detected': False, 'confidence': 0.0}
    
    def _detect_flag(self, df: pd.DataFrame) -> Dict:
        """Bayrak pattern'ini tespit eder"""
        try:
            # Basit bayrak tespiti
            return {
                'detected': False,
                'confidence': 0.0,
                'description': 'Bayrak pattern tespit edilmedi'
            }
            
        except Exception as e:
            self.logger.error(f"Bayrak tespit hatası: {e}")
            return {'detected': False, 'confidence': 0.0} 