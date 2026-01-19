# Gereksinimler ve Analiz

## 1. Proje Hedefi

Sistem servislerinin (systemd/Windows Services) durumunu izleyen ve loglarını raporlayan cross-platform bir araç geliştirmek.

## 2. Fonksiyonel Gereksinimler

### 2.1 Servis İzleme (FR-01)

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR-01.1 | Tüm servisleri listeleme | Yüksek |
| FR-01.2 | Servis durumu (aktif/pasif) gösterme | Yüksek |
| FR-01.3 | Servis detaylarını görüntüleme | Orta |
| FR-01.4 | Kritik servisleri tanımlama | Yüksek |

### 2.2 Log Yönetimi (FR-02)

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR-02.1 | Log toplama (journalctl/Event Log) | Yüksek |
| FR-02.2 | Log filtreleme (ERROR, WARNING) | Yüksek |
| FR-02.3 | Tarih aralığına göre filtreleme | Orta |
| FR-02.4 | Regex ile arama | Düşük |

### 2.3 Uyarı Sistemi (FR-03)

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR-03.1 | Kritik servis durduğunda uyarı | Yüksek |
| FR-03.2 | Hata sayısı eşik aşımında uyarı | Orta |
| FR-03.3 | Uyarı geçmişi tutma | Düşük |

### 2.4 Kullanıcı Arayüzü (FR-04)

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR-04.1 | Web tabanlı dashboard | Yüksek |
| FR-04.2 | Real-time güncelleme | Yüksek |
| FR-04.3 | Modern ve responsive tasarım | Yüksek |
| FR-04.4 | Dark mode tema | Orta |

## 3. Fonksiyonel Olmayan Gereksinimler

### 3.1 Performans (NFR-01)

- Sayfa yüklenme süresi < 2 saniye
- Servis listesi güncelleme < 1 saniye
- 1000+ log satırı işleme kapasitesi

### 3.2 Güvenilirlik (NFR-02)

- Platform bağımsız çalışma (Linux + Windows)
- Hata toleransı (servis erişilemezse graceful degradation)

### 3.3 Otomasyon (NFR-03)

- **Auto Control Ability**: Sistem durumunu otomatik kontrol edebilme
- **Auto Test Ability**: Self-check mekanizması

### 3.4 Tasarım (NFR-04)

- Modern UI standartları
- Vibrant colors, responsive tasarım
- Kullanıcı dostu arayüz

## 4. Teknik Gereksinimler

### 4.1 Yazılım

| Bileşen | Teknoloji | Versiyon |
|---------|-----------|----------|
| Programlama Dili | Python | 3.10+ |
| Web Framework | Flask | 2.3+ |
| Real-time | Flask-SocketIO | 5.3+ |
| System Info | psutil | 5.9+ |

### 4.2 İşletim Sistemi

- Ubuntu 22.04 veya üzeri
- Windows 10/11

## 5. Use Case Diyagramı

```
┌─────────────────────────────────────────────────────────┐
│                    System Operator                       │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   View      │ │   Filter    │ │   Receive   │
    │  Services   │ │    Logs     │ │   Alerts    │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Check      │ │   Search    │ │  Configure  │
    │  Status     │ │   by Date   │ │  Critical   │
    └─────────────┘ └─────────────┘ └─────────────┘
```

## 6. Kabul Kriterleri

- [ ] Servislerin aktif/pasif durumu anlık gösterilmeli
- [ ] journalctl çıktıları ERROR, WARNING filtrelenebilmeli
- [ ] Kritik servisler durduğunda uyarı verilmeli
- [ ] Web dashboard modern ve responsive olmalı
- [ ] Auto Test (Self-Check) mekanizması çalışmalı
- [ ] Hem Linux hem Windows'ta çalışmalı
