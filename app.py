"""
Kripto AL/SAT Tahmin Sistemi - Ana Flask Uygulaması
Bu uygulama tüm modülleri birleştirir ve web arayüzü sağlar
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime, timedelta
import json

# Proje modüllerini import et
from src.data_collection.binance_data import BinanceDataCollector
from src.technical_analysis.indicators import TechnicalIndicators
from src.ml_models.price_predictor import PricePredictor
from src.signal_generation.signal_generator import SignalGenerator

# Flask uygulamasını oluştur
app = Flask(__name__)
CORS(app)

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global değişkenler
current_data = None
current_signals = None
current_predictions = None

class CryptoAnalyzer:
    """
    Tüm analiz modüllerini birleştiren ana sınıf
    """
    
    def __init__(self):
        """CryptoAnalyzer sınıfını başlatır"""
        self.data_collector = BinanceDataCollector()
        self.technical_indicators = TechnicalIndicators()
        self.price_predictor = PricePredictor()
        self.signal_generator = SignalGenerator()
        
    def analyze_crypto(self, symbol: str, interval: str = '1h', limit: int = 500) -> dict:
        """
        Belirtilen kripto para için tam analiz yapar
        
        Args:
            symbol (str): Kripto para çifti (örn: 'BTCUSDT')
            interval (str): Zaman aralığı ('1h', '4h', '1d')
            limit (int): Veri sayısı
            
        Returns:
            dict: Analiz sonuçları
        """
        try:
            logger.info(f"{symbol} için analiz başlatılıyor...")
            
            # 1. Veri toplama
            df = self.data_collector.get_historical_data(symbol, interval, limit=limit)
            if df.empty:
                return {'error': 'Veri çekilemedi'}
            
            # 2. Teknik göstergeleri hesapla
            df_with_indicators = self.technical_indicators.calculate_all_indicators(df)
            
            # 3. AI tahminleri
            predictions = self.price_predictor.get_ensemble_prediction(df_with_indicators)
            
            # 4. Sinyal üretimi
            signals = self.signal_generator.generate_signals(df_with_indicators, predictions)
            
            # 5. Sonuçları hazırla
            # DataFrame'i JSON'a çevrilebilir hale getir
            data_dict = df_with_indicators.reset_index().to_dict('records')
            
            # Predictions'ı JSON'a çevrilebilir hale getir
            predictions_json = self._convert_predictions_to_json(predictions)
            
            # Signals'ı JSON'a çevrilebilir hale getir
            signals_json = self._convert_signals_to_json(signals)
            
            result = {
                'symbol': symbol,
                'interval': interval,
                'data': data_dict,
                'predictions': predictions_json,
                'signals': signals_json,
                'summary': self._create_summary(df_with_indicators, signals, predictions),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"{symbol} analizi tamamlandı")
            return result
            
        except Exception as e:
            logger.error(f"Analiz hatası: {e}")
            return {'error': str(e)}
    
    def _create_summary(self, df: pd.DataFrame, signals: list, predictions: dict) -> dict:
        """Analiz özeti oluşturur"""
        try:
            latest = df.iloc[-1]
            
            # Latest signal'ı JSON'a çevir
            latest_signal_json = None
            if signals:
                latest_signal_json = self._convert_signal_to_json(signals[-1])
            
            summary = {
                'current_price': float(latest['close']),
                'price_change_24h': 0,  # Hesaplanacak
                'technical_summary': self.technical_indicators.get_indicator_summary(df),
                'support_resistance': self.technical_indicators.get_support_resistance(df),
                'latest_signal': latest_signal_json,
                'prediction_summary': self._get_prediction_summary(predictions)
            }
            
            # 24 saatlik değişim hesapla
            if len(df) > 24:
                summary['price_change_24h'] = ((latest['close'] - df.iloc[-24]['close']) / df.iloc[-24]['close']) * 100
            
            return summary
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {e}")
            return {}
    
    def _get_prediction_summary(self, predictions: dict) -> dict:
        """Tahmin özeti oluşturur"""
        try:
            if 'error' in predictions:
                return {'error': predictions['error']}
            
            if 'ensemble_prediction' in predictions:
                ensemble_pred = predictions['ensemble_prediction']
                return {
                    'next_24h_prediction': float(ensemble_pred[0]) if len(ensemble_pred) > 0 else 0,
                    'prediction_models': list(predictions.get('individual_models', {}).keys()),
                    'model_weights': predictions.get('weights', [])
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Tahmin özeti hatası: {e}")
            return {}
    
    def _convert_predictions_to_json(self, predictions: dict) -> dict:
        """Predictions'ı JSON'a çevrilebilir hale getirir"""
        try:
            if not predictions:
                return {}
            
            json_predictions = {}
            
            for key, value in predictions.items():
                if isinstance(value, np.ndarray):
                    json_predictions[key] = value.tolist()
                elif isinstance(value, dict):
                    json_predictions[key] = self._convert_predictions_to_json(value)
                elif isinstance(value, list):
                    json_predictions[key] = [
                        item.tolist() if isinstance(item, np.ndarray) else item 
                        for item in value
                    ]
                elif hasattr(value, '__class__') and 'ARIMA' in str(value.__class__):
                    # ARIMA model nesnelerini string'e çevir
                    json_predictions[key] = str(value)
                elif hasattr(value, 'tolist'):
                    # NumPy array benzeri nesneler
                    json_predictions[key] = value.tolist()
                elif hasattr(value, '__dict__'):
                    # Diğer nesneleri string'e çevir
                    json_predictions[key] = str(value)
                else:
                    json_predictions[key] = value
            
            return json_predictions
            
        except Exception as e:
            logger.error(f"Predictions JSON dönüştürme hatası: {e}")
            return {}
    
    def _convert_signals_to_json(self, signals: list) -> list:
        """Signals'ı JSON'a çevrilebilir hale getirir"""
        try:
            if not signals:
                return []
            
            json_signals = []
            
            for signal in signals:
                json_signal = {}
                
                for key, value in signal.items():
                    if hasattr(value, 'value'):  # Enum değerleri
                        json_signal[key] = value.value
                    elif isinstance(value, datetime):
                        json_signal[key] = value.isoformat()
                    elif isinstance(value, list):
                        json_signal[key] = [
                            item.value if hasattr(item, 'value') else item 
                            for item in value
                        ]
                    else:
                        json_signal[key] = value
                
                json_signals.append(json_signal)
            
            return json_signals
            
        except Exception as e:
            logger.error(f"Signals JSON dönüştürme hatası: {e}")
            return []
    
    def _convert_signal_to_json(self, signal: dict) -> dict:
        """Tek bir signal'ı JSON'a çevrilebilir hale getirir"""
        try:
            if not signal:
                return {}
            
            json_signal = {}
            
            for key, value in signal.items():
                if hasattr(value, 'value'):  # Enum değerleri
                    json_signal[key] = value.value
                elif isinstance(value, datetime):
                    json_signal[key] = value.isoformat()
                elif isinstance(value, list):
                    json_signal[key] = [
                        item.value if hasattr(item, 'value') else item 
                        for item in value
                    ]
                else:
                    json_signal[key] = value
            
            return json_signal
            
        except Exception as e:
            logger.error(f"Signal JSON dönüştürme hatası: {e}")
            return {}

# Global analyzer instance
analyzer = CryptoAnalyzer()

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Kripto para analizi yapar"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        interval = data.get('interval', '1h')
        
        # Analiz yap
        result = analyzer.analyze_crypto(symbol, interval)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        # Global değişkenleri güncelle
        global current_data, current_signals, current_predictions
        current_signals = result['signals']
        current_predictions = result['predictions']
        
        # DataFrame'i global değişkende sakla (sadece son 100 veri)
        if 'data' in result and result['data']:
            # JSON'dan DataFrame'e geri çevir
            df_data = pd.DataFrame(result['data'])
            current_data = df_data.tail(100)  # Son 100 veriyi sakla
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analiz endpoint hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/symbols')
def get_symbols():
    """Mevcut kripto para çiftlerini döndürür"""
    try:
        # Popüler kripto paralar
        symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
            'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT', 'LINKUSDT',
            'UNIUSDT', 'LTCUSDT', 'BCHUSDT', 'XLMUSDT', 'VETUSDT'
        ]
        
        return jsonify({'symbols': symbols})
        
    except Exception as e:
        logger.error(f"Symbols endpoint hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-overview')
def market_overview():
    """Piyasa genel görünümü"""
    try:
        collector = BinanceDataCollector()
        gainers, losers = collector.get_top_gainers_losers(5)
        
        return jsonify({
            'top_gainers': gainers,
            'top_losers': losers,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Market overview hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals')
def get_signals():
    """Mevcut sinyalleri döndürür"""
    global current_signals
    return jsonify({'signals': current_signals or []})

@app.route('/api/predictions')
def get_predictions():
    """Mevcut tahminleri döndürür"""
    global current_predictions
    return jsonify({'predictions': current_predictions or {}})

@app.route('/api/data')
def get_data():
    """Mevcut veriyi döndürür"""
    global current_data
    if current_data is not None:
        # DataFrame'i JSON'a çevir
        data_dict = current_data.reset_index().to_dict('records')
        return jsonify({'data': data_dict})
    return jsonify({'data': []})

@app.route('/health')
def health_check():
    """Sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Hata yakalama
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Sayfa bulunamadı'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Sunucu hatası'}), 500

if __name__ == '__main__':
    # Geliştirme sunucusunu başlat
    app.run(debug=True, host='0.0.0.0', port=5000) 