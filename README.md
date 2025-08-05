# 🚀 Kripto AL/SAT Tahmin Sistemi

**Yapay Zeka Destekli Kripto Para Analiz ve Alım/Satım Sinyali Platformu**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Teknolojiler](#-teknolojiler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Proje Yapısı](#-proje-yapısı)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

## ✨ Özellikler

### 🤖 AI Destekli Analiz
- **Prophet Modeli** - Facebook'un zaman serisi tahmin modeli
- **ARIMA Modeli** - Klasik istatistiksel tahmin
- **LSTM Modeli** - Derin öğrenme tabanlı tahmin
- **Ensemble Tahmin** - Çoklu model birleştirme

### 📊 Teknik Analiz
- **RSI (Relative Strength Index)** - Aşırı alım/satım göstergesi
- **MACD** - Momentum ve trend göstergesi
- **Bollinger Bands** - Volatilite ve fiyat kanalları
- **EMA/SMA** - Hareketli ortalamalar
- **Stochastic Oscillator** - Momentum göstergesi
- **Williams %R** - Aşırı alım/satım göstergesi
- **ATR** - Ortalama Gerçek Aralık

### 📈 Görselleştirme
- **İnteraktif Grafikler** - Plotly.js ile candlestick grafikleri
- **Teknik Gösterge Grafikleri** - Alt grafikler
- **Alım/Satım Sinyalleri** - Renkli işaretler
- **Responsive Tasarım** - Mobil uyumlu arayüz

### 🔔 Sinyal Sistemi
- **Otomatik Sinyal Üretimi** - AI + teknik analiz birleşimi
- **Güven Skorları** - 0-100 arası güvenilirlik
- **Risk Yönetimi** - Stop-loss önerileri
- **Gerçek Zamanlı Güncelleme** - Periyodik analiz

## 🛠️ Teknolojiler

### Backend
- **Python 3.8+** - Ana programlama dili
- **Flask** - Web framework
- **Pandas** - Veri işleme
- **NumPy** - Matematiksel işlemler
- **Scikit-learn** - Makine öğrenmesi
- **Prophet** - Zaman serisi tahmini
- **TensorFlow** - Derin öğrenme
- **TA-Lib** - Teknik analiz göstergeleri

### Frontend
- **HTML5/CSS3** - Web arayüzü
- **JavaScript (ES6+)** - İnteraktif özellikler
- **Bootstrap 5** - Responsive tasarım
- **Plotly.js** - İnteraktif grafikler
- **Font Awesome** - İkonlar

### Veri Kaynakları
- **Binance API** - Kripto para verileri
- **CCXT** - Çoklu borsa desteği

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- Git

### Adım 1: Repository'yi Klonlayın
```bash
git clone https://github.com/kullaniciadi/kripto-al-sat.git
cd kripto-al-sat
```

### Adım 2: Sanal Ortam Oluşturun
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: Uygulamayı Başlatın
```bash
python app.py
```

Uygulama `http://localhost:5000` adresinde çalışacaktır.

## 📖 Kullanım

### Web Arayüzü
1. Tarayıcınızda `http://localhost:5000` adresine gidin
2. Kripto para çifti seçin (örn: BTCUSDT)
3. Zaman aralığı seçin (1H, 4H, 1D)
4. "Analiz Et" butonuna tıklayın
5. Sonuçları grafiklerde ve tablolarda görün

### API Kullanımı
```python
import requests

# Analiz yap
response = requests.post('http://localhost:5000/analyze', json={
    'symbol': 'BTCUSDT',
    'interval': '1h'
})

data = response.json()
print(data['summary']['current_price'])
```

## 📚 API Dokümantasyonu

### POST /analyze
Kripto para analizi yapar.

**Request Body:**
```json
{
    "symbol": "BTCUSDT",
    "interval": "1h"
}
```

**Response:**
```json
{
    "symbol": "BTCUSDT",
    "interval": "1h",
    "data": [...],
    "predictions": {...},
    "signals": [...],
    "summary": {
        "current_price": 45000.0,
        "price_change_24h": 2.5,
        "technical_summary": {...},
        "support_resistance": {...},
        "latest_signal": {...}
    }
}
```

### GET /health
Uygulama sağlık kontrolü.

### GET /api/symbols
Mevcut kripto para çiftlerini listeler.

## 📁 Proje Yapısı

```
kripto-al-sat/
├── app.py                      # Ana Flask uygulaması
├── requirements.txt            # Python bağımlılıkları
├── README.md                   # Proje dokümantasyonu
├── .gitignore                  # Git ignore dosyası
├── src/                        # Kaynak kodlar
│   ├── data_collection/        # Veri toplama modülleri
│   │   ├── binance_data.py     # Binance API entegrasyonu
│   │   └── data_processor.py   # Veri işleme
│   ├── technical_analysis/     # Teknik analiz modülleri
│   │   ├── indicators.py       # Teknik göstergeler
│   │   ├── patterns.py         # Pattern tanıma
│   │   └── signals.py          # Sinyal üretimi
│   ├── ml_models/              # Makine öğrenmesi modülleri
│   │   ├── price_predictor.py  # Fiyat tahmin modelleri
│   │   ├── model_trainer.py    # Model eğitimi
│   │   └── ensemble_model.py   # Ensemble modeller
│   ├── signal_generation/      # Sinyal üretimi modülleri
│   │   ├── signal_generator.py # Ana sinyal üretici
│   │   ├── risk_manager.py     # Risk yönetimi
│   │   └── confidence_calculator.py # Güven hesaplama
│   └── visualization/          # Görselleştirme modülleri
├── templates/                  # HTML şablonları
│   └── index.html              # Ana sayfa
├── static/                     # Statik dosyalar
│   ├── css/                    # CSS dosyaları
│   └── js/                     # JavaScript dosyaları
├── data/                       # Veri dosyaları
│   ├── historical/             # Geçmiş veriler
│   └── models/                 # Eğitilmiş modeller
└── tests/                      # Test dosyaları
```

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

### Katkıda Bulunabilecek Alanlar
- Yeni teknik göstergeler ekleme
- AI modellerini geliştirme
- Web arayüzünü iyileştirme
- Test coverage artırma
- Dokümantasyon geliştirme

## ⚠️ Uyarılar

- Bu proje eğitim amaçlıdır
- Finansal tavsiye niteliği taşımaz
- Yatırım kararlarınızda dikkatli olun
- Risk yönetimi kurallarına uyun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

- **Proje Sahibi:** [Adınız]
- **Email:** [email@example.com]
- **GitHub:** [github.com/kullaniciadi]

## 🙏 Teşekkürler

- [Binance](https://binance.com) - API desteği için
- [Facebook Prophet](https://facebook.github.io/prophet/) - Zaman serisi tahmini için
- [Plotly](https://plotly.com) - İnteraktif grafikler için
- [Bootstrap](https://getbootstrap.com) - UI framework için

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! 