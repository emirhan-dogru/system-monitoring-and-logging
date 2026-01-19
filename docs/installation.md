# Kurulum Kılavuzu

## Gereksinimler

### Yazılım Gereksinimleri

- **Python**: 3.10 veya üzeri
- **pip**: Python paket yöneticisi
- **İşletim Sistemi**: 
  - Linux (Ubuntu 22.04 önerilir)
  - Windows 10/11

### Linux için Ek Gereksinimler

- systemd (servis yönetimi için)
- journalctl (log erişimi için)

### Windows için Ek Gereksinimler

- Windows Services erişimi
- PowerShell (yedek metot olarak)

## Kurulum Adımları

### 1. Repository'yi Klonlayın

```bash
git clone https://github.com/emirhan-dogru/system-monitoring-and-logging.git
cd monitoring-logging
```

### 2. Virtual Environment Oluşturun (Önerilir)

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Kurulumu Doğrulayın

```bash
python src/main.py --self-check
```

Başarılı çıktı:
```
==================================================
🔍 Self-Check / Auto Test
==================================================

✅ Service Monitor: X servis bulundu
✅ Log Collector: X log okundu
✅ Log Parser: OK
✅ Alert Manager: OK

✅ Tüm kontroller başarılı!
```

## Yapılandırma

### Environment Variables

| Değişken | Açıklama | Varsayılan |
|----------|----------|------------|
| `MONITOR_HOST` | Sunucu adresi | 0.0.0.0 |
| `MONITOR_PORT` | Sunucu portu | 5000 |
| `MONITOR_DEBUG` | Debug modu | false |
| `MONITOR_ERROR_THRESHOLD` | Hata eşiği | 10 |
| `MONITOR_WARNING_THRESHOLD` | Uyarı eşiği | 20 |

### Örnek Yapılandırma

**Linux:**
```bash
export MONITOR_PORT=8080
export MONITOR_DEBUG=true
python src/main.py
```

**Windows PowerShell:**
```powershell
$env:MONITOR_PORT = "8080"
$env:MONITOR_DEBUG = "true"
python src/main.py
```

## Hızlı Başlangıç

```bash
# Sunucuyu başlat
python src/main.py

# Tarayıcıda aç
# http://localhost:5000
```

## Sorun Giderme

### "ModuleNotFoundError" Hatası

```bash
pip install -r requirements.txt
```

### "Permission denied" (Linux)

Log erişimi için root yetkisi gerekebilir:
```bash
sudo python src/main.py
```

### Windows Servis Erişim Hatası

PowerShell'i Administrator olarak çalıştırın.
