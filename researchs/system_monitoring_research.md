# Sistem Servisleri Monitoring Araştırması

## 1. Giriş

Bu döküman, Linux ve Windows işletim sistemlerinde servis izleme ve log yönetimi konularında yapılan araştırmaları içermektedir.

## 2. Linux Sistemlerde Servis Yönetimi

### 2.1 systemd

systemd, modern Linux dağıtımlarında standart init sistemi olarak kullanılmaktadır.

**Temel Komutlar:**
- `systemctl list-units --type=service` - Tüm servisleri listele
- `systemctl status <service>` - Servis durumu
- `systemctl is-active <service>` - Aktif mi kontrol et
- `systemctl is-failed <service>` - Hatalı mı kontrol et

### 2.2 journalctl

journalctl, systemd'nin log yönetim aracıdır.

**Temel Komutlar:**
- `journalctl -p err` - Sadece ERROR logları
- `journalctl -p warning` - WARNING ve üstü
- `journalctl --since "1 hour ago"` - Son 1 saat
- `journalctl -u <service>` - Belirli servisin logları

### 2.3 Python ile Entegrasyon

```python
import subprocess

def get_service_status(service_name):
    result = subprocess.run(
        ['systemctl', 'is-active', service_name],
        capture_output=True, text=True
    )
    return result.stdout.strip()
```

## 3. Windows Sistemlerde Servis Yönetimi

### 3.1 Windows Services

Windows servislerini yönetmek için:
- `sc query` - Servisleri listele
- `sc query <service>` - Servis durumu
- `Get-Service` (PowerShell) - Servisleri listele

### 3.2 Windows Event Log

Windows Event Log yapısı:
- Application Log
- System Log
- Security Log

### 3.3 Python ile Entegrasyon

```python
import psutil

def get_windows_services():
    services = []
    for service in psutil.win_service_iter():
        services.append({
            'name': service.name(),
            'status': service.status(),
            'display_name': service.display_name()
        })
    return services
```

## 4. Cross-Platform Yaklaşım

Hem Linux hem Windows'ta çalışacak bir uygulama için:

1. **Platform Detection**: `platform.system()` ile işletim sistemi belirleme
2. **Adapter Pattern**: Her platform için ayrı adaptör sınıfı
3. **Common Interface**: Ortak bir arayüz tanımlama

```python
import platform

class ServiceMonitor:
    def __init__(self):
        if platform.system() == 'Linux':
            self.adapter = LinuxAdapter()
        else:
            self.adapter = WindowsAdapter()
```

## 5. Log Filtreleme Stratejileri

### 5.1 Severity Levels

| Level | Açıklama |
|-------|----------|
| EMERG | Sistem kullanılamaz |
| ALERT | Hemen aksiyon gerekli |
| CRIT | Kritik durum |
| ERR | Hata |
| WARNING | Uyarı |
| NOTICE | Normal ama önemli |
| INFO | Bilgilendirme |
| DEBUG | Debug mesajları |

### 5.2 Filtreleme Yöntemleri

1. **Regex ile filtreleme**
2. **Tarih aralığı ile filtreleme**
3. **Servis bazlı filtreleme**
4. **Severity bazlı filtreleme**

## 6. Sonuç

Bu araştırma sonucunda, cross-platform bir monitoring uygulaması için:
- Python'un `psutil` kütüphanesi Windows'ta etkili
- Linux'ta `subprocess` ile systemctl/journalctl kullanımı
- Adapter pattern ile platform bağımsız tasarım
- Flask ile web dashboard geliştirme

yaklaşımlarının uygun olduğu belirlenmiştir.

## 7. Kaynaklar

- [systemd Documentation](https://systemd.io/)
- [journalctl Man Page](https://www.freedesktop.org/software/systemd/man/journalctl.html)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [Python subprocess Module](https://docs.python.org/3/library/subprocess.html)
