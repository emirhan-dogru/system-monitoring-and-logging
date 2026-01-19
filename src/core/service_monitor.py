"""
Service Monitor Module
Cross-platform sistem servisleri izleme modülü.
"""

import platform
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ServiceStatus(Enum):
    """Servis durumu enum'u"""
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Servis bilgisi veri sınıfı"""
    name: str
    display_name: str
    status: ServiceStatus
    is_critical: bool = False
    description: str = ""
    pid: Optional[int] = None

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": self.status.value,
            "is_critical": self.is_critical,
            "description": self.description,
            "pid": self.pid
        }


class ServiceMonitor:
    """
    Cross-platform servis izleme sınıfı.
    Linux ve Windows sistemlerinde servis durumlarını izler.
    """

    # Kritik olarak işaretlenecek varsayılan servisler
    DEFAULT_CRITICAL_SERVICES = {
        "linux": ["sshd", "nginx", "apache2", "mysql", "postgresql", "docker"],
        "windows": ["Spooler", "BITS", "wuauserv", "Dhcp", "Dnscache", "EventLog"]
    }

    def __init__(self, custom_critical_services: List[str] = None):
        """
        ServiceMonitor başlatıcı.
        
        Args:
            custom_critical_services: Özel kritik servis listesi
        """
        self.platform = platform.system().lower()
        self.adapter = self._get_adapter()
        self.critical_services = custom_critical_services or self._get_default_critical()

    def _get_default_critical(self) -> List[str]:
        """Varsayılan kritik servisleri döndür"""
        if self.platform == "linux":
            return self.DEFAULT_CRITICAL_SERVICES["linux"]
        return self.DEFAULT_CRITICAL_SERVICES["windows"]

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

    def get_all_services(self) -> List[ServiceInfo]:
        """
        Tüm servisleri listele.
        
        Returns:
            ServiceInfo listesi
        """
        services = self.adapter.get_services()
        
        # Kritik servisleri işaretle
        for service in services:
            if service.name in self.critical_services:
                service.is_critical = True
        
        return services

    def get_service_status(self, service_name: str) -> ServiceInfo:
        """
        Belirli bir servisin durumunu al.
        
        Args:
            service_name: Servis adı
            
        Returns:
            ServiceInfo nesnesi
        """
        service = self.adapter.get_service_status(service_name)
        if service and service.name in self.critical_services:
            service.is_critical = True
        return service

    def get_running_services(self) -> List[ServiceInfo]:
        """Çalışan servisleri döndür"""
        return [s for s in self.get_all_services() if s.status == ServiceStatus.RUNNING]

    def get_stopped_services(self) -> List[ServiceInfo]:
        """Durmuş servisleri döndür"""
        return [s for s in self.get_all_services() if s.status == ServiceStatus.STOPPED]

    def get_failed_services(self) -> List[ServiceInfo]:
        """Hatalı servisleri döndür"""
        return [s for s in self.get_all_services() if s.status == ServiceStatus.FAILED]

    def get_critical_services(self) -> List[ServiceInfo]:
        """Kritik servisleri döndür"""
        return [s for s in self.get_all_services() if s.is_critical]

    def get_critical_down_services(self) -> List[ServiceInfo]:
        """Durmuş kritik servisleri döndür"""
        return [s for s in self.get_critical_services() 
                if s.status in [ServiceStatus.STOPPED, ServiceStatus.FAILED]]

    def add_critical_service(self, service_name: str):
        """Kritik servis listesine ekle"""
        if service_name not in self.critical_services:
            self.critical_services.append(service_name)

    def remove_critical_service(self, service_name: str):
        """Kritik servis listesinden çıkar"""
        if service_name in self.critical_services:
            self.critical_services.remove(service_name)

    def get_service_summary(self) -> Dict:
        """
        Servis özeti döndür.
        
        Returns:
            Özet istatistikleri içeren sözlük
        """
        services = self.get_all_services()
        return {
            "total": len(services),
            "running": len([s for s in services if s.status == ServiceStatus.RUNNING]),
            "stopped": len([s for s in services if s.status == ServiceStatus.STOPPED]),
            "failed": len([s for s in services if s.status == ServiceStatus.FAILED]),
            "critical_total": len([s for s in services if s.is_critical]),
            "critical_down": len(self.get_critical_down_services()),
            "platform": self.platform
        }


# Test için
if __name__ == "__main__":
    monitor = ServiceMonitor()
    print(f"Platform: {monitor.platform}")
    print(f"Service Summary: {monitor.get_service_summary()}")
