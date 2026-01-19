"""
Alert Manager Module
Uyarı sistemi modülü.
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import time


class AlertSeverity(Enum):
    """Uyarı önem derecesi"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Uyarı tipi"""
    SERVICE_DOWN = "service_down"
    SERVICE_FAILED = "service_failed"
    HIGH_ERROR_RATE = "high_error_rate"
    HIGH_WARNING_RATE = "high_warning_rate"
    CRITICAL_SERVICE_DOWN = "critical_service_down"
    CUSTOM = "custom"


@dataclass
class Alert:
    """Uyarı veri sınıfı"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "resolved": self.resolved
        }


class AlertManager:
    """
    Uyarı yönetim sınıfı.
    Kritik durumları tespit eder ve uyarı oluşturur.
    """

    def __init__(self, error_threshold: int = 10, warning_threshold: int = 20):
        """
        AlertManager başlatıcı.
        
        Args:
            error_threshold: Hata eşiği (bu kadar error log'da uyarı)
            warning_threshold: Uyarı eşiği
        """
        self.error_threshold = error_threshold
        self.warning_threshold = warning_threshold
        self.alerts: List[Alert] = []
        self._alert_counter = 0
        self._lock = threading.Lock()
        self._callbacks: List[Callable[[Alert], None]] = []

    def _generate_id(self) -> str:
        """Benzersiz uyarı ID'si oluştur"""
        with self._lock:
            self._alert_counter += 1
            return f"ALT-{self._alert_counter:06d}"

    def add_callback(self, callback: Callable[[Alert], None]):
        """Yeni uyarı callback'i ekle"""
        self._callbacks.append(callback)

    def _notify_callbacks(self, alert: Alert):
        """Callback'leri bilgilendir"""
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Callback error: {e}")

    def create_alert(self, 
                     type: AlertType,
                     severity: AlertSeverity,
                     title: str,
                     message: str,
                     source: str = "system") -> Alert:
        """
        Yeni uyarı oluştur.
        
        Returns:
            Oluşturulan Alert nesnesi
        """
        alert = Alert(
            id=self._generate_id(),
            type=type,
            severity=severity,
            title=title,
            message=message,
            source=source
        )
        
        with self._lock:
            self.alerts.append(alert)
        
        self._notify_callbacks(alert)
        return alert

    def check_service_status(self, service_name: str, is_running: bool, is_critical: bool = False):
        """
        Servis durumunu kontrol et ve gerekirse uyarı oluştur.
        
        Args:
            service_name: Servis adı
            is_running: Servis çalışıyor mu
            is_critical: Kritik servis mi
        """
        if not is_running:
            if is_critical:
                self.create_alert(
                    type=AlertType.CRITICAL_SERVICE_DOWN,
                    severity=AlertSeverity.CRITICAL,
                    title=f"Kritik Servis Durdu: {service_name}",
                    message=f"Kritik servis '{service_name}' durmuş durumda. Acil müdahale gerekiyor.",
                    source=service_name
                )
            else:
                self.create_alert(
                    type=AlertType.SERVICE_DOWN,
                    severity=AlertSeverity.MEDIUM,
                    title=f"Servis Durdu: {service_name}",
                    message=f"Servis '{service_name}' durmuş durumda.",
                    source=service_name
                )

    def check_error_rate(self, error_count: int, total_count: int, source: str = "logs"):
        """
        Hata oranını kontrol et.
        
        Args:
            error_count: Hata sayısı
            total_count: Toplam log sayısı
            source: Kaynak
        """
        if error_count >= self.error_threshold:
            rate = round(error_count / max(total_count, 1) * 100, 2)
            self.create_alert(
                type=AlertType.HIGH_ERROR_RATE,
                severity=AlertSeverity.HIGH,
                title="Yüksek Hata Oranı",
                message=f"Son loglar içinde {error_count} adet ERROR tespit edildi (%{rate}).",
                source=source
            )

    def check_warning_rate(self, warning_count: int, total_count: int, source: str = "logs"):
        """
        Uyarı oranını kontrol et.
        """
        if warning_count >= self.warning_threshold:
            rate = round(warning_count / max(total_count, 1) * 100, 2)
            self.create_alert(
                type=AlertType.HIGH_WARNING_RATE,
                severity=AlertSeverity.MEDIUM,
                title="Yüksek Uyarı Oranı",
                message=f"Son loglar içinde {warning_count} adet WARNING tespit edildi (%{rate}).",
                source=source
            )

    def get_active_alerts(self) -> List[Alert]:
        """Çözülmemiş uyarıları döndür"""
        return [a for a in self.alerts if not a.resolved]

    def get_unacknowledged_alerts(self) -> List[Alert]:
        """Onaylanmamış uyarıları döndür"""
        return [a for a in self.alerts if not a.acknowledged]

    def get_critical_alerts(self) -> List[Alert]:
        """Kritik uyarıları döndür"""
        return [a for a in self.alerts 
                if a.severity == AlertSeverity.CRITICAL and not a.resolved]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Uyarıyı onayla"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Uyarıyı çözülmüş olarak işaretle"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                return True
        return False

    def get_alert_summary(self) -> Dict:
        """Uyarı özeti döndür"""
        active = self.get_active_alerts()
        return {
            "total": len(self.alerts),
            "active": len(active),
            "critical": len([a for a in active if a.severity == AlertSeverity.CRITICAL]),
            "high": len([a for a in active if a.severity == AlertSeverity.HIGH]),
            "medium": len([a for a in active if a.severity == AlertSeverity.MEDIUM]),
            "low": len([a for a in active if a.severity == AlertSeverity.LOW]),
            "unacknowledged": len(self.get_unacknowledged_alerts())
        }

    def clear_resolved(self):
        """Çözülmüş uyarıları temizle"""
        with self._lock:
            self.alerts = [a for a in self.alerts if not a.resolved]

    def get_alerts_json(self) -> List[Dict]:
        """Tüm uyarıları JSON formatında döndür"""
        return [a.to_dict() for a in self.alerts]


# Test için
if __name__ == "__main__":
    manager = AlertManager()
    
    # Test uyarısı oluştur
    manager.create_alert(
        type=AlertType.SERVICE_DOWN,
        severity=AlertSeverity.HIGH,
        title="Test Alert",
        message="This is a test alert",
        source="test"
    )
    
    print(f"Alert Summary: {manager.get_alert_summary()}")
