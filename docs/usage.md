# Kullanım Kılavuzu

## Web Dashboard

### Başlatma

```bash
python src/main.py
```

Tarayıcıda `http://localhost:5000` adresini açın.

### Dashboard Sekmesi

![Dashboard](screenshots/dashboard.png)

- **İstatistik Kartları**: Çalışan, durmuş, hatalı servis sayıları
- **Servis Grafiği**: Donut chart ile servis durumu dağılımı
- **Log Grafiği**: Seviye bazlı log dağılımı
- **Son Uyarılar**: En son oluşan uyarılar

### Servisler Sekmesi

- **Filtreleme**: Duruma göre (çalışan, durmuş, hatalı, kritik)
- **Arama**: Servis adına göre arama
- **Durum Göstergesi**: Yeşil=çalışan, Sarı=durmuş, Kırmızı=hatalı

### Loglar Sekmesi

- **Seviye Filtresi**: ERROR, WARNING, INFO
- **Limit**: Gösterilecek log sayısı (50, 100, 200)
- **Arama**: Log mesajı içinde arama

### Uyarılar Sekmesi

- **Onayla**: Uyarıyı görüldü olarak işaretle
- **Çözüldü**: Uyarıyı çözülmüş olarak işaretle
- **Kritik/Yüksek Sayaçları**: Öncelikli uyarı sayıları

## CLI Kullanımı

### Servis Listesi

```bash
python src/main.py --list-services
```

Çıktı:
```
============================================================
Platform: WINDOWS
Toplam Servis: 245
============================================================

🟢 Çalışan: 120
🟡 Durmuş: 125
🔴 Hatalı: 0

────────────────────────────────────────────────────────────
Servis                                   Durum          
────────────────────────────────────────────────────────────
Spooler                                  🟢 running      
BITS                                     🟢 running      
...
```

### Log Görüntüleme

```bash
# Son 20 log
python src/main.py --logs

# Sadece ERROR logları
python src/main.py --logs --level error

# Son 50 log
python src/main.py --logs --limit 50
```

### Kritik Servis İzleme

```bash
python src/main.py --watch-critical
```

Bu mod sürekli olarak kritik servisleri izler ve durduğunda uyarı verir.

### Self-Check

```bash
python src/main.py --self-check
```

Tüm modüllerin doğru çalıştığını kontrol eder.

## API Kullanımı

### Endpoints

| Endpoint | Metot | Açıklama |
|----------|-------|----------|
| `/api/status` | GET | Sistem durumu |
| `/api/services` | GET | Servis listesi |
| `/api/services/summary` | GET | Servis özeti |
| `/api/logs` | GET | Log listesi |
| `/api/logs/statistics` | GET | Log istatistikleri |
| `/api/alerts` | GET | Uyarı listesi |
| `/api/dashboard` | GET | Dashboard özeti |

### Örnek API Çağrıları

**Servis Listesi:**
```bash
curl http://localhost:5000/api/services
```

**Log Filtreleme:**
```bash
curl "http://localhost:5000/api/logs?level=error&limit=50"
```

**Dashboard Özeti:**
```bash
curl http://localhost:5000/api/dashboard
```

## Kritik Servis Tanımlama

Varsayılan kritik servisler `src/config.py` dosyasında tanımlanmıştır.

Özel kritik servis eklemek için:

```python
from core.service_monitor import ServiceMonitor

monitor = ServiceMonitor()
monitor.add_critical_service("my-service")
```

## Uyarı Eşikleri

Varsayılan eşikler:
- **Error Threshold**: 10 (10 error log'da uyarı)
- **Warning Threshold**: 20 (20 warning log'da uyarı)

Environment variable ile değiştirilebilir:
```bash
export MONITOR_ERROR_THRESHOLD=5
export MONITOR_WARNING_THRESHOLD=15
```
