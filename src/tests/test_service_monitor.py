"""
Service Monitor Tests
Servis izleme modülü unit testleri.
"""

import pytest
import platform
import sys
import os

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.service_monitor import ServiceMonitor, ServiceInfo, ServiceStatus


class TestServiceStatus:
    """ServiceStatus enum testleri"""
    
    def test_status_values(self):
        """Durum değerlerini test et"""
        assert ServiceStatus.RUNNING.value == "running"
        assert ServiceStatus.STOPPED.value == "stopped"
        assert ServiceStatus.FAILED.value == "failed"
        assert ServiceStatus.UNKNOWN.value == "unknown"


class TestServiceInfo:
    """ServiceInfo dataclass testleri"""
    
    def test_service_info_creation(self):
        """ServiceInfo oluşturma testi"""
        service = ServiceInfo(
            name="test_service",
            display_name="Test Service",
            status=ServiceStatus.RUNNING
        )
        
        assert service.name == "test_service"
        assert service.display_name == "Test Service"
        assert service.status == ServiceStatus.RUNNING
        assert service.is_critical == False
    
    def test_service_info_to_dict(self):
        """ServiceInfo dict dönüşümü testi"""
        service = ServiceInfo(
            name="test",
            display_name="Test",
            status=ServiceStatus.RUNNING,
            is_critical=True,
            pid=1234
        )
        
        result = service.to_dict()
        
        assert result["name"] == "test"
        assert result["status"] == "running"
        assert result["is_critical"] == True
        assert result["pid"] == 1234


class TestServiceMonitor:
    """ServiceMonitor sınıfı testleri"""
    
    @pytest.fixture
    def monitor(self):
        """Test için ServiceMonitor instance"""
        return ServiceMonitor()
    
    def test_platform_detection(self, monitor):
        """Platform algılama testi"""
        expected_platform = platform.system().lower()
        assert monitor.platform == expected_platform
    
    def test_get_all_services(self, monitor):
        """Tüm servisleri listeleme testi"""
        services = monitor.get_all_services()
        
        # En az birkaç servis olmalı
        assert isinstance(services, list)
        # Windows veya Linux'ta servis olmalı
        # (Bazı ortamlarda boş olabilir)
    
    def test_get_service_summary(self, monitor):
        """Servis özeti testi"""
        summary = monitor.get_service_summary()
        
        assert "total" in summary
        assert "running" in summary
        assert "stopped" in summary
        assert "failed" in summary
        assert "platform" in summary
        
        assert isinstance(summary["total"], int)
        assert isinstance(summary["running"], int)
    
    def test_add_critical_service(self, monitor):
        """Kritik servis ekleme testi"""
        test_service = "test_critical_service"
        
        monitor.add_critical_service(test_service)
        
        assert test_service in monitor.critical_services
    
    def test_remove_critical_service(self, monitor):
        """Kritik servis çıkarma testi"""
        test_service = "test_to_remove"
        
        monitor.add_critical_service(test_service)
        monitor.remove_critical_service(test_service)
        
        assert test_service not in monitor.critical_services


# Test çalıştırma
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
