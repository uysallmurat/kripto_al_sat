"""
Fiyat tahmin modellerini içeren modül
Bu modül Prophet, ARIMA, LSTM gibi modelleri kullanır
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Makine öğrenmesi kütüphaneleri
try:
    from prophet import Prophet
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    PROPHET_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Bazı ML kütüphaneleri yüklenemedi: {e}")
    PROPHET_AVAILABLE = False

class PricePredictor:
    """
    Fiyat tahmin modellerini yöneten sınıf
    """
    
    def __init__(self):
        """PricePredictor sınıfını başlatır"""
        self.logger = logging.getLogger(__name__)
        self.scaler = MinMaxScaler()
        self.models = {}
        self.predictions = {}
        
    def prepare_data_for_prophet(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prophet modeli için veriyi hazırlar
        
        Args:
            df (pd.DataFrame): OHLCV verileri
            
        Returns:
            pd.DataFrame: Prophet formatında veri
        """
        try:
            # Prophet için gerekli sütunlar: ds (tarih) ve y (değer)
            prophet_df = df.reset_index()
            prophet_df = prophet_df.rename(columns={'timestamp': 'ds', 'close': 'y'})
            prophet_df = prophet_df[['ds', 'y']]
            
            return prophet_df
        except Exception as e:
            self.logger.error(f"Prophet veri hazırlama hatası: {e}")
            return pd.DataFrame()
    
    def train_prophet_model(self, df: pd.DataFrame, periods: int = 24) -> Dict:
        """
        Prophet modelini eğitir ve tahmin yapar
        
        Args:
            df (pd.DataFrame): Eğitim verisi
            periods (int): Tahmin edilecek periyot sayısı
            
        Returns:
            Dict: Model sonuçları
        """
        if not PROPHET_AVAILABLE:
            return {'error': 'Prophet kütüphanesi yüklenemedi'}
            
        try:
            # Veriyi hazırla
            prophet_df = self.prepare_data_for_prophet(df)
            
            if prophet_df.empty:
                return {'error': 'Veri hazırlama başarısız'}
            
            # Prophet modelini oluştur ve eğit
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                seasonality_mode='multiplicative'
            )
            
            model.fit(prophet_df)
            
            # Gelecek tarihleri oluştur
            future = model.make_future_dataframe(periods=periods, freq='H')
            forecast = model.predict(future)
            
            # Sonuçları hazırla
            result = {
                'model': model,
                'forecast': forecast,
                'predictions': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods),
                'model_type': 'Prophet'
            }
            
            self.models['prophet'] = model
            self.predictions['prophet'] = result
            
            self.logger.info(f"Prophet modeli eğitildi ve {periods} periyot tahmin yapıldı")
            return result
            
        except Exception as e:
            self.logger.error(f"Prophet model hatası: {e}")
            return {'error': str(e)}
    
    def prepare_data_for_lstm(self, df: pd.DataFrame, lookback: int = 60) -> Tuple[np.ndarray, np.ndarray]:
        """
        LSTM modeli için veriyi hazırlar
        
        Args:
            df (pd.DataFrame): OHLCV verileri
            lookback (int): Geriye bakılacak periyot sayısı
            
        Returns:
            Tuple: (X, y) eğitim verileri
        """
        try:
            # Sadece close fiyatlarını al
            data = df['close'].values.reshape(-1, 1)
            
            # Veriyi normalize et
            scaled_data = self.scaler.fit_transform(data)
            
            X, y = [], []
            for i in range(lookback, len(scaled_data)):
                X.append(scaled_data[i-lookback:i, 0])
                y.append(scaled_data[i, 0])
            
            X, y = np.array(X), np.array(y)
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"LSTM veri hazırlama hatası: {e}")
            return np.array([]), np.array([])
    
    def train_lstm_model(self, df: pd.DataFrame, lookback: int = 60, epochs: int = 50) -> Dict:
        """
        LSTM modelini eğitir
        
        Args:
            df (pd.DataFrame): Eğitim verisi
            lookback (int): Geriye bakılacak periyot sayısı
            epochs (int): Eğitim epoch sayısı
            
        Returns:
            Dict: Model sonuçları
        """
        try:
            # Veriyi hazırla
            X, y = self.prepare_data_for_lstm(df, lookback)
            
            if len(X) == 0:
                return {'error': 'LSTM veri hazırlama başarısız'}
            
            # Eğitim ve test verilerini ayır
            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            # LSTM modelini oluştur
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # Modeli eğit
            history = model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=32,
                validation_data=(X_test, y_test),
                verbose=0
            )
            
            # Test tahminleri
            test_predictions = model.predict(X_test)
            test_predictions = self.scaler.inverse_transform(test_predictions)
            y_test_actual = self.scaler.inverse_transform(y_test.reshape(-1, 1))
            
            # Gelecek tahminleri için son verileri kullan
            last_sequence = X[-1:]
            future_predictions = []
            
            for _ in range(24):  # 24 saatlik tahmin
                next_pred = model.predict(last_sequence)
                future_predictions.append(next_pred[0, 0])
                
                # Sequence'i güncelle
                last_sequence = np.roll(last_sequence, -1)
                last_sequence[0, -1, 0] = next_pred[0, 0]
            
            # Tahminleri denormalize et
            future_predictions = np.array(future_predictions).reshape(-1, 1)
            future_predictions = self.scaler.inverse_transform(future_predictions)
            
            result = {
                'model': model,
                'history': history,
                'test_predictions': test_predictions.flatten(),
                'test_actual': y_test_actual.flatten(),
                'future_predictions': future_predictions.flatten(),
                'model_type': 'LSTM'
            }
            
            self.models['lstm'] = model
            self.predictions['lstm'] = result
            
            self.logger.info(f"LSTM modeli eğitildi")
            return result
            
        except Exception as e:
            self.logger.error(f"LSTM model hatası: {e}")
            return {'error': str(e)}
    
    def train_arima_model(self, df: pd.DataFrame, order: Tuple = (1, 1, 1)) -> Dict:
        """
        ARIMA modelini eğitir
        
        Args:
            df (pd.DataFrame): Eğitim verisi
            order (Tuple): ARIMA parametreleri (p, d, q)
            
        Returns:
            Dict: Model sonuçları
        """
        try:
            # Close fiyatlarını al
            data = df['close'].values
            
            # Modeli eğit
            model = ARIMA(data, order=order)
            fitted_model = model.fit()
            
            # Gelecek tahminleri
            forecast = fitted_model.forecast(steps=24)
            
            result = {
                'model': fitted_model,
                'forecast': forecast,
                'aic': fitted_model.aic,
                'bic': fitted_model.bic,
                'model_type': 'ARIMA'
            }
            
            self.models['arima'] = fitted_model
            self.predictions['arima'] = result
            
            self.logger.info(f"ARIMA modeli eğitildi")
            return result
            
        except Exception as e:
            self.logger.error(f"ARIMA model hatası: {e}")
            return {'error': str(e)}
    
    def calculate_prediction_accuracy(self, actual: np.ndarray, predicted: np.ndarray) -> Dict:
        """
        Tahmin doğruluğunu hesaplar
        
        Args:
            actual (np.ndarray): Gerçek değerler
            predicted (np.ndarray): Tahmin edilen değerler
            
        Returns:
            Dict: Doğruluk metrikleri
        """
        try:
            mae = mean_absolute_error(actual, predicted)
            mse = mean_squared_error(actual, predicted)
            rmse = np.sqrt(mse)
            
            # MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((actual - predicted) / actual)) * 100
            
            return {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'mape': mape
            }
        except Exception as e:
            self.logger.error(f"Doğruluk hesaplama hatası: {e}")
            return {}
    
    def get_ensemble_prediction(self, df: pd.DataFrame) -> Dict:
        """
        Tüm modelleri kullanarak ensemble tahmin yapar
        
        Args:
            df (pd.DataFrame): Eğitim verisi
            
        Returns:
            Dict: Ensemble tahmin sonuçları
        """
        try:
            results = {}
            
            # Prophet modeli
            if PROPHET_AVAILABLE:
                prophet_result = self.train_prophet_model(df)
                if 'error' not in prophet_result:
                    results['prophet'] = prophet_result
            
            # LSTM modeli
            lstm_result = self.train_lstm_model(df)
            if 'error' not in lstm_result:
                results['lstm'] = lstm_result
            
            # ARIMA modeli
            arima_result = self.train_arima_model(df)
            if 'error' not in arima_result:
                results['arima'] = arima_result
            
            # Ensemble tahmin (ağırlıklı ortalama)
            ensemble_predictions = []
            weights = []
            
            for model_name, result in results.items():
                if model_name == 'prophet':
                    pred = result['predictions']['yhat'].values
                    weights.append(0.4)  # Prophet'e daha fazla ağırlık
                elif model_name == 'lstm':
                    pred = result['future_predictions']
                    weights.append(0.35)
                elif model_name == 'arima':
                    pred = result['forecast']
                    weights.append(0.25)
                
                ensemble_predictions.append(pred[:24])  # İlk 24 tahmin
            
            if ensemble_predictions:
                # Ağırlıklı ortalama hesapla
                weights = np.array(weights) / sum(weights)
                ensemble_final = np.average(ensemble_predictions, axis=0, weights=weights)
                
                return {
                    'ensemble_prediction': ensemble_final,
                    'individual_models': results,
                    'weights': weights.tolist()
                }
            
            return {'error': 'Hiçbir model başarıyla eğitilemedi'}
            
        except Exception as e:
            self.logger.error(f"Ensemble tahmin hatası: {e}")
            return {'error': str(e)}

# Test fonksiyonu
if __name__ == "__main__":
    # Test için örnek veri oluştur
    dates = pd.date_range('2024-01-01', periods=500, freq='H')
    np.random.seed(42)
    
    # Gerçekçi fiyat verisi oluştur
    base_price = 100
    price_changes = np.random.randn(500) * 0.02  # %2 volatilite
    prices = [base_price]
    
    for change in price_changes[1:]:
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    test_data = pd.DataFrame({
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, 500)
    }, index=dates)
    
    # Fiyat tahmin modellerini test et
    predictor = PricePredictor()
    
    print("Fiyat tahmin modelleri test ediliyor...")
    
    # Prophet testi
    if PROPHET_AVAILABLE:
        prophet_result = predictor.train_prophet_model(test_data)
        print(f"Prophet sonucu: {len(prophet_result.get('predictions', []))} tahmin")
    
    # LSTM testi
    lstm_result = predictor.train_lstm_model(test_data)
    print(f"LSTM sonucu: {len(lstm_result.get('future_predictions', []))} tahmin")
    
    # ARIMA testi
    arima_result = predictor.train_arima_model(test_data)
    print(f"ARIMA sonucu: {len(arima_result.get('forecast', []))} tahmin")
    
    print("Test tamamlandı!") 