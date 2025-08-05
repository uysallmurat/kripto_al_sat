"""
Veri İşleme Modülü
Bu modül kripto verilerini temizler ve işler
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Kripto veri işleme sınıfı
    Veri temizleme, normalleştirme ve hazırlama işlemleri yapar
    """
    
    def __init__(self):
        """DataProcessor sınıfını başlatır"""
        self.processed_data = None
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Veriyi temizler (boş değerler, duplikatlar vb.)
        
        Args:
            df (pd.DataFrame): Ham veri
            
        Returns:
            pd.DataFrame: Temizlenmiş veri
        """
        try:
            logger.info("Veri temizleme başlatılıyor...")
            
            # Kopya oluştur
            cleaned_df = df.copy()
            
            # Boş değerleri doldur
            cleaned_df = cleaned_df.fillna(method='ffill')
            cleaned_df = cleaned_df.fillna(method='bfill')
            
            # Duplikatları kaldır
            cleaned_df = cleaned_df.drop_duplicates()
            
            # Sıfır veya negatif fiyatları kaldır
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in cleaned_df.columns:
                    cleaned_df = cleaned_df[cleaned_df[col] > 0]
            
            logger.info(f"Veri temizlendi. Satır sayısı: {len(cleaned_df)}")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Veri temizleme hatası: {e}")
            return df
    
    def normalize_data(self, df: pd.DataFrame, method: str = 'minmax') -> pd.DataFrame:
        """
        Veriyi normalleştirir
        
        Args:
            df (pd.DataFrame): Temizlenmiş veri
            method (str): Normalleştirme yöntemi ('minmax', 'zscore')
            
        Returns:
            pd.DataFrame: Normalleştirilmiş veri
        """
        try:
            logger.info(f"Veri normalleştirme başlatılıyor ({method})...")
            
            normalized_df = df.copy()
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            if method == 'minmax':
                from sklearn.preprocessing import MinMaxScaler
                scaler = MinMaxScaler()
                normalized_df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
                
            elif method == 'zscore':
                from sklearn.preprocessing import StandardScaler
                scaler = StandardScaler()
                normalized_df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
            
            logger.info("Veri normalleştirme tamamlandı")
            return normalized_df
            
        except Exception as e:
            logger.error(f"Normalleştirme hatası: {e}")
            return df
    
    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Yeni özellikler ekler
        
        Args:
            df (pd.DataFrame): Mevcut veri
            
        Returns:
            pd.DataFrame: Yeni özellikler eklenmiş veri
        """
        try:
            logger.info("Yeni özellikler ekleniyor...")
            
            enhanced_df = df.copy()
            
            # Fiyat değişim oranları
            if 'close' in df.columns:
                enhanced_df['price_change_pct'] = df['close'].pct_change()
                enhanced_df['price_change_pct_5'] = df['close'].pct_change(5)
                enhanced_df['price_change_pct_10'] = df['close'].pct_change(10)
            
            # Volatilite
            if 'high' in df.columns and 'low' in df.columns:
                enhanced_df['volatility'] = (df['high'] - df['low']) / df['close'] * 100
            
            # Hacim özellikleri
            if 'volume' in df.columns:
                enhanced_df['volume_ma_5'] = df['volume'].rolling(5).mean()
                enhanced_df['volume_ratio'] = df['volume'] / enhanced_df['volume_ma_5']
            
            # Zaman bazlı özellikler
            if df.index.dtype == 'datetime64[ns]':
                enhanced_df['hour'] = df.index.hour
                enhanced_df['day_of_week'] = df.index.dayofweek
                enhanced_df['month'] = df.index.month
            
            logger.info("Yeni özellikler eklendi")
            return enhanced_df
            
        except Exception as e:
            logger.error(f"Özellik ekleme hatası: {e}")
            return df
    
    def process_data(self, df: pd.DataFrame, 
                    clean: bool = True, 
                    normalize: bool = False, 
                    add_features: bool = True) -> pd.DataFrame:
        """
        Tam veri işleme pipeline'ı
        
        Args:
            df (pd.DataFrame): Ham veri
            clean (bool): Veri temizleme yapılsın mı
            normalize (bool): Normalleştirme yapılsın mı
            add_features (bool): Yeni özellikler eklensin mi
            
        Returns:
            pd.DataFrame: İşlenmiş veri
        """
        try:
            logger.info("Veri işleme pipeline başlatılıyor...")
            
            processed_df = df.copy()
            
            # Veri temizleme
            if clean:
                processed_df = self.clean_data(processed_df)
            
            # Yeni özellikler ekleme
            if add_features:
                processed_df = self.add_features(processed_df)
            
            # Normalleştirme (en son yapılır)
            if normalize:
                processed_df = self.normalize_data(processed_df)
            
            self.processed_data = processed_df
            logger.info("Veri işleme tamamlandı")
            
            return processed_df
            
        except Exception as e:
            logger.error(f"Veri işleme hatası: {e}")
            return df
    
    def get_training_data(self, df: pd.DataFrame, 
                         target_column: str = 'close',
                         sequence_length: int = 60) -> tuple:
        """
        Makine öğrenmesi için eğitim verisi hazırlar
        
        Args:
            df (pd.DataFrame): İşlenmiş veri
            target_column (str): Hedef sütun
            sequence_length (int): Sekans uzunluğu
            
        Returns:
            tuple: (X, y) eğitim verisi
        """
        try:
            logger.info("Eğitim verisi hazırlanıyor...")
            
            # Numerik sütunları seç
            numeric_df = df.select_dtypes(include=[np.number])
            
            # Hedef değişkeni ayır
            if target_column not in numeric_df.columns:
                raise ValueError(f"Hedef sütun '{target_column}' bulunamadı")
            
            # Sekanslar oluştur
            X, y = [], []
            
            for i in range(sequence_length, len(numeric_df)):
                X.append(numeric_df.iloc[i-sequence_length:i].values)
                y.append(numeric_df[target_column].iloc[i])
            
            X = np.array(X)
            y = np.array(y)
            
            logger.info(f"Eğitim verisi hazırlandı. X shape: {X.shape}, y shape: {y.shape}")
            
            return X, y
            
        except Exception as e:
            logger.error(f"Eğitim verisi hazırlama hatası: {e}")
            return None, None