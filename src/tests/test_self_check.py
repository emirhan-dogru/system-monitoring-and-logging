"""
Self-Check Tests
Auto Test Ability / Self-Check mekanizması testleri.
"""

import pytest
import sys
import os
import platform

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSelfCheck:
    """Self-Check / Auto Test yeteneği testleri"""
    
    def test_core_modules_importable(self):
        """Core modüllerin import edilebilirliği"""
        from core.service_monitor import ServiceMonitor
        from core.log_collector import LogCollector
        from core.log_parser import LogParser
        from core.alert_manager import AlertManager
        
        assert ServiceMonitor is not None
        assert LogCollector is not None
        assert LogParser is not None
        assert AlertManager is not None
    
    def test_service_monitor_initialization(self):
        """ServiceMonitor başlatma testi"""
        from core.service_monitor import ServiceMonitor
        
        monitor = ServiceMonitor()
        
        assert monitor.platform in ["linux", "windows", "darwin"]
        assert monitor.adapter is not None
    
    def test_log_collector_initialization(self):
        """LogCollector başlatma testi"""
        from core.log_collector import LogCollector
        
        collector = LogCollector()
        
        assert collector.platform in ["linux", "windows", "darwin"]
        assert collector.adapter is not None
    
    def test_log_parser_initialization(self):
        """LogParser başlatma testi"""
        from core.log_parser import LogParser
        
        parser = LogParser()
        
        assert parser is not None
    
    def test_alert_manager_initialization(self):
        """AlertManager başlatma testi"""
        from core.alert_manager import AlertManager
        
        manager = AlertManager()
        
        assert manager.error_threshold > 0
        assert manager.warning_threshold > 0
        assert manager.alerts == []
    
    def test_alert_creation(self):
        """Uyarı oluşturma testi"""
        from core.alert_manager import AlertManager, AlertType, AlertSeverity
        
        manager = AlertManager()
        alert = manager.create_alert(
            type=AlertType.SERVICE_DOWN,
            severity=AlertSeverity.HIGH,
            title="Test Alert",
            message="This is a test alert"
        )
        
        assert alert.id is not None
        assert alert.title == "Test Alert"
        assert alert.severity == AlertSeverity.HIGH
        assert len(manager.alerts) == 1
    
    def test_platform_adapter_selection(self):
        """Platform adaptör seçimi testi"""
        from core.service_monitor import ServiceMonitor
        
        monitor = ServiceMonitor()
        
        if platform.system().lower() == "linux":
            from adapters.linux_adapter import LinuxAdapter
            assert isinstance(monitor.adapter, LinuxAdapter)
        elif platform.system().lower() == "windows":
            from adapters.windows_adapter import WindowsAdapter
            assert isinstance(monitor.adapter, WindowsAdapter)
    
    def test_service_summary_structure(self):
        """Servis özeti yapısı testi"""
        from core.service_monitor import ServiceMonitor
        
        monitor = ServiceMonitor()
        summary = monitor.get_service_summary()
        
        required_keys = ["total", "running", "stopped", "failed", "platform"]
        for key in required_keys:
            assert key in summary, f"Missing key: {key}"
    
    def test_log_statistics_structure(self):
        """Log istatistik yapısı testi"""
        from core.log_collector import LogCollector
        
        collector = LogCollector()
        stats = collector.get_log_statistics()
        
        required_keys = ["total", "by_level", "platform"]
        for key in required_keys:
            assert key in stats, f"Missing key: {key}"
    
    def test_alert_summary_structure(self):
        """Uyarı özeti yapısı testi"""
        from core.alert_manager import AlertManager
        
        manager = AlertManager()
        summary = manager.get_alert_summary()
        
        required_keys = ["total", "active", "critical", "high", "medium", "low"]
        for key in required_keys:
            assert key in summary, f"Missing key: {key}"
    
    def test_config_module(self):
        """Yapılandırma modülü testi"""
        from config import config
        
        assert config.host is not None
        assert config.port > 0
        assert config.error_threshold > 0
    
    def test_full_self_check(self):
        """Tam self-check testi"""
        # Bu test tüm sistemin çalışır durumda olduğunu doğrular
        checks_passed = 0
        total_checks = 0
        
        # Check 1: ServiceMonitor
        total_checks += 1
        try:
            from core.service_monitor import ServiceMonitor
            monitor = ServiceMonitor()
            monitor.get_service_summary()
            checks_passed += 1
        except Exception:
            pass
        
        # Check 2: LogCollector
        total_checks += 1
        try:
            from core.log_collector import LogCollector
            collector = LogCollector()
            collector.get_log_statistics()
            checks_passed += 1
        except Exception:
            pass
        
        # Check 3: LogParser
        total_checks += 1
        try:
            from core.log_parser import LogParser
            parser = LogParser()
            parser.get_statistics([])
            checks_passed += 1
        except Exception:
            pass
        
        # Check 4: AlertManager
        total_checks += 1
        try:
            from core.alert_manager import AlertManager
            manager = AlertManager()
            manager.get_alert_summary()
            checks_passed += 1
        except Exception:
            pass
        
        # Tüm kontrollerin geçmesi gerekiyor
        assert checks_passed == total_checks, \
            f"Self-check failed: {checks_passed}/{total_checks} passed"


# Test çalıştırma
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
