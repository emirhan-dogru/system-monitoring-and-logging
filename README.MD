# Monitoring & Logging Panel

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Cross-platform sistem servisleri izleme ve log yönetim paneli.

## 🎯 Özellikler

- ✅ **Servis İzleme**: Aktif/pasif durumlarını anlık gösterme
- ✅ **Log Toplama**: journalctl (Linux) / Event Log (Windows) okuma
- ✅ **Log Filtreleme**: ERROR, WARNING, INFO filtreleri
- ✅ **Kritik Uyarılar**: Servis durduğunda bildirim
- ✅ **Modern UI**: Dark mode, responsive tasarım
- ✅ **Cross-platform**: Linux ve Windows desteği

## 📸 Screenshots

*Dashboard ekran görüntüsü*

## 🚀 Kurulum

### Gereksinimler

- Python 3.10+
- pip

### Adımlar

```bash
# Repository'yi klonla
git clone https://github.com/emirhan-dogru/system-monitoring-and-logging.git

# Virtual environment oluştur (opsiyonel)
python -m venv venv
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı başlat
python src/main.py
```

Tarayıcıda `http://localhost:5000` adresini açın.

## 📁 Proje Yapısı

```
monitoring-logging/
├── researchs/           # Araştırma dökümanları
├── specs/               # Gereksinim ve analiz
├── src/
│   ├── core/            # Ana modüller
│   ├── adapters/        # Platform adaptörleri
│   ├── web/             # Flask web uygulaması
│   └── tests/           # Unit testler
├── docs/                # Dokümantasyon
├── project_info.json    # Proje meta verileri
└── README.md
```

## 🧪 Test

```bash
# Tüm testleri çalıştır
python -m pytest src/tests/ -v

# Self-check
python src/main.py --self-check
```

## 📖 Kullanım

### Web Dashboard

1. `python src/main.py` ile başlatın
2. `http://localhost:5000` adresini açın
3. Sol panelden servisleri izleyin
4. Sağ panelden logları filtreleyin

### CLI Kullanımı

```bash
# Servis listesi
python src/main.py --list-services

# Log filtreleme
python src/main.py --logs --level ERROR

# Kritik servisleri izle
python src/main.py --watch-critical
```

## 📚 Dokümantasyon

- [Kurulum Kılavuzu](docs/installation.md)
- [Kullanım Kılavuzu](docs/usage.md)
- [API Dokümantasyonu](docs/api.md)

## 🛠️ Teknolojiler

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **System**: psutil, subprocess

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👤 Yazar

**Emirhan Doğru**

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
