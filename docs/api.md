# API Dokümantasyonu

## Genel Bilgiler

- **Base URL**: `http://localhost:5000`
- **Format**: JSON
- **Kimlik Doğrulama**: Yok (yerel kullanım için)

## Endpoints

---

### GET /api/status

Sistem durumunu döndürür.

**Yanıt:**
```json
{
  "status": "ok",
  "platform": "windows",
  "version": "1.0.0"
}
```

---

### GET /api/services

Servis listesini döndürür.

**Query Parametreleri:**
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| status | string | Filtre: running, stopped, failed, critical |

**Örnek İstek:**
```bash
GET /api/services?status=running
```

**Yanıt:**
```json
{
  "services": [
    {
      "name": "Spooler",
      "display_name": "Print Spooler",
      "status": "running",
      "is_critical": false,
      "description": "...",
      "pid": 1234
    }
  ],
  "count": 120
}
```

---

### GET /api/services/summary

Servis özeti istatistiklerini döndürür.

**Yanıt:**
```json
{
  "total": 245,
  "running": 120,
  "stopped": 125,
  "failed": 0,
  "critical_total": 6,
  "critical_down": 0,
  "platform": "windows"
}
```

---

### GET /api/services/{service_name}

Belirli bir servisin detaylarını döndürür.

**Örnek İstek:**
```bash
GET /api/services/Spooler
```

**Yanıt:**
```json
{
  "name": "Spooler",
  "display_name": "Print Spooler",
  "status": "running",
  "is_critical": false,
  "description": "",
  "pid": 1234
}
```

**Hata:**
```json
{
  "error": "Service not found"
}
```

---

### GET /api/logs

Log listesini döndürür.

**Query Parametreleri:**
| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| limit | int | 100 | Maksimum log sayısı |
| level | string | - | Filtre: error, warning, info |
| service | string | - | Servis adı filtresi |
| search | string | - | Mesaj içinde arama |

**Örnek İstek:**
```bash
GET /api/logs?level=error&limit=50&search=failed
```

**Yanıt:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:45+03:00",
      "level": "ERROR",
      "level_value": 3,
      "message": "Connection failed",
      "source": "System",
      "service": "nginx"
    }
  ],
  "count": 25,
  "statistics": {
    "total": 25,
    "by_level": {"ERROR": 25},
    "error_count": 25,
    "warning_count": 0,
    "error_rate": 100.0,
    "warning_rate": 0.0
  }
}
```

---

### GET /api/logs/statistics

Log istatistiklerini döndürür.

**Yanıt:**
```json
{
  "total": 100,
  "by_level": {
    "ERROR": 5,
    "WARNING": 15,
    "INFO": 80
  },
  "by_service": {
    "nginx": 20,
    "mysql": 30
  },
  "error_count": 5,
  "warning_count": 15,
  "error_rate": 5.0,
  "warning_rate": 15.0
}
```

---

### GET /api/alerts

Uyarı listesini döndürür.

**Query Parametreleri:**
| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| active | bool | true | Sadece aktif uyarılar |

**Yanıt:**
```json
{
  "alerts": [
    {
      "id": "ALT-000001",
      "type": "critical_service_down",
      "severity": "critical",
      "title": "Kritik Servis Durdu: nginx",
      "message": "Kritik servis 'nginx' durmuş durumda.",
      "source": "nginx",
      "timestamp": "2024-01-15T10:30:45+03:00",
      "acknowledged": false,
      "resolved": false
    }
  ],
  "count": 1,
  "summary": {
    "total": 1,
    "active": 1,
    "critical": 1,
    "high": 0,
    "medium": 0,
    "low": 0,
    "unacknowledged": 1
  }
}
```

---

### POST /api/alerts/{alert_id}/acknowledge

Uyarıyı onaylar.

**Yanıt (Başarılı):**
```json
{
  "success": true
}
```

**Yanıt (Hata):**
```json
{
  "error": "Alert not found"
}
```

---

### POST /api/alerts/{alert_id}/resolve

Uyarıyı çözülmüş olarak işaretler.

**Yanıt (Başarılı):**
```json
{
  "success": true
}
```

---

### GET /api/dashboard

Dashboard özeti döndürür.

**Yanıt:**
```json
{
  "services": {
    "total": 245,
    "running": 120,
    "stopped": 125,
    "failed": 0
  },
  "logs": {
    "total": 100,
    "by_level": {"ERROR": 5, "WARNING": 15},
    "error_count": 5,
    "warning_count": 15
  },
  "alerts": {
    "total": 1,
    "active": 1,
    "critical": 1
  },
  "platform": "windows"
}
```

---

## Hata Kodları

| Kod | Açıklama |
|-----|----------|
| 200 | Başarılı |
| 404 | Kaynak bulunamadı |
| 500 | Sunucu hatası |

## WebSocket

Real-time güncellemeler için WebSocket desteği mevcuttur.

**Bağlantı:**
```javascript
const socket = io('http://localhost:5000');

socket.on('connected', (data) => {
  console.log('Connected:', data);
});

socket.emit('request_update');

socket.on('dashboard_update', (data) => {
  console.log('Update:', data);
});
```
