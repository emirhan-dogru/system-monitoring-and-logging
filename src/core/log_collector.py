"""
Log Collector Module
Cross-platform log toplama modülü.
"""

import platform
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log seviyesi enum'u"""
    EMERGENCY = 0
    ALERT = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = 4
    NOTICE = 5
    INFO = 6
    DEBUG = 7


@dataclass
class LogEntry:
    """Log girdisi veri sınıfı"""
    timestamp: datetime
    level: LogLevel
    message: str
    source: str = ""
    service: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.name,
            "level_value": self.level.value,
            "message": self.message,
            "source": self.source,
            "service": self.service
        }


class LogCollector:
    """
    Cross-platform log toplama sınıfı.
    Linux'ta journalctl, Windows'ta Event Log okur.
    """

    def __init__(self):
        """LogCollector başlatıcı."""
        self.platform = platform.system().lower()
        self.adapter = self._get_adapter()

    def _get_adapter(self):
        """Platform'a göre uygun adaptörü döndür"""
        import sys
        import os
        # Adapters modülünü import edebilmek için path ekle
        src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        if self.platform == "linux":
            from adapters.linux_adapter import LinuxAdapter
            return LinuxAdapter()
        else:
            from adapters.windows_adapter import WindowsAdapter
            return WindowsAdapter()

    def get_logs(self, 
                 limit: int = 100,
                 level: Optional[LogLevel] = None,
                 service: Optional[str] = None,
                 since: Optional[datetime] = None,
                 until: Optional[datetime] = None) -> List[LogEntry]:
        """
        Log girdilerini al.
        
        Args:
            limit: Maksimum log sayısı
            level: Minimum log seviyesi filtresi
            service: Servis adı filtresi
            since: Başlangıç tarihi
            until: Bitiş tarihi
            
        Returns:
            LogEntry listesi
        """
        return self.adapter.get_logs(
            limit=limit,
            level=level,
            service=service,
            since=since,
            until=until
        )

    def get_error_logs(self, limit: int = 50) -> List[LogEntry]:
        """Sadece ERROR seviyesi logları al"""
        return self.get_logs(limit=limit, level=LogLevel.ERROR)

    def get_warning_logs(self, limit: int = 50) -> List[LogEntry]:
        """WARNING ve üstü logları al"""
        return self.get_logs(limit=limit, level=LogLevel.WARNING)

    def get_service_logs(self, service_name: str, limit: int = 100) -> List[LogEntry]:
        """Belirli bir servisin loglarını al"""
        return self.get_logs(limit=limit, service=service_name)

    def get_recent_logs(self, minutes: int = 60, limit: int = 100) -> List[LogEntry]:
        """Son N dakikadaki logları al"""
        from datetime import timedelta
        since = datetime.now() - timedelta(minutes=minutes)
        return self.get_logs(limit=limit, since=since)

    def get_log_statistics(self, logs: List[LogEntry] = None) -> Dict:
        """
        Log istatistiklerini hesapla.
        
        Args:
            logs: Analiz edilecek loglar (None ise son 100 log)
            
        Returns:
            İstatistik sözlüğü
        """
        if logs is None:
            logs = self.get_logs(limit=100)
        
        stats = {
            "total": len(logs),
            "by_level": {},
            "platform": self.platform
        }
        
        for level in LogLevel:
            count = len([log for log in logs if log.level == level])
            if count > 0:
                stats["by_level"][level.name] = count
        
        return stats


# Test için
if __name__ == "__main__":
    collector = LogCollector()
    print(f"Platform: {collector.platform}")
    stats = collector.get_log_statistics()
    print(f"Log Statistics: {stats}")
