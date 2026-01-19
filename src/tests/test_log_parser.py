"""
Log Parser Tests
Log ayrıştırma modülü unit testleri.
"""

import pytest
import sys
import os
from datetime import datetime

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.log_collector import LogEntry, LogLevel
from core.log_parser import LogParser


class TestLogLevel:
    """LogLevel enum testleri"""
    
    def test_log_levels_order(self):
        """Log seviyesi sıralaması testi"""
        assert LogLevel.EMERGENCY.value < LogLevel.ERROR.value
        assert LogLevel.ERROR.value < LogLevel.WARNING.value
        assert LogLevel.WARNING.value < LogLevel.INFO.value
        assert LogLevel.INFO.value < LogLevel.DEBUG.value


class TestLogEntry:
    """LogEntry dataclass testleri"""
    
    def test_log_entry_creation(self):
        """LogEntry oluşturma testi"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            message="Test error message",
            service="test_service"
        )
        
        assert entry.level == LogLevel.ERROR
        assert entry.message == "Test error message"
        assert entry.service == "test_service"
    
    def test_log_entry_to_dict(self):
        """LogEntry dict dönüşümü testi"""
        timestamp = datetime.now()
        entry = LogEntry(
            timestamp=timestamp,
            level=LogLevel.WARNING,
            message="Test warning"
        )
        
        result = entry.to_dict()
        
        assert result["level"] == "WARNING"
        assert result["message"] == "Test warning"
        assert "timestamp" in result


class TestLogParser:
    """LogParser sınıfı testleri"""
    
    @pytest.fixture
    def parser(self):
        """Test için LogParser instance"""
        return LogParser()
    
    @pytest.fixture
    def sample_logs(self):
        """Test için örnek loglar"""
        return [
            LogEntry(datetime.now(), LogLevel.ERROR, "Database connection failed", service="db"),
            LogEntry(datetime.now(), LogLevel.WARNING, "High memory usage", service="monitor"),
            LogEntry(datetime.now(), LogLevel.INFO, "Service started successfully", service="app"),
            LogEntry(datetime.now(), LogLevel.ERROR, "Authentication error", service="auth"),
            LogEntry(datetime.now(), LogLevel.DEBUG, "Debug message", service="debug"),
        ]
    
    def test_filter_by_level(self, parser, sample_logs):
        """Seviyeye göre filtreleme testi"""
        result = parser.filter_by_level(sample_logs, LogLevel.ERROR)
        
        # ERROR ve üstü (CRITICAL, ALERT, EMERGENCY, ERROR)
        assert all(log.level.value <= LogLevel.ERROR.value for log in result)
    
    def test_filter_by_keyword(self, parser, sample_logs):
        """Anahtar kelime filtresi testi"""
        result = parser.filter_by_keyword(sample_logs, "error")
        
        assert len(result) == 2  # "error" içeren mesajlar
        assert all("error" in log.message.lower() for log in result)
    
    def test_filter_by_regex(self, parser, sample_logs):
        """Regex filtresi testi"""
        result = parser.filter_by_regex(sample_logs, r"Database.*failed")
        
        assert len(result) == 1
        assert result[0].message == "Database connection failed"
    
    def test_filter_by_service(self, parser, sample_logs):
        """Servis filtresi testi"""
        result = parser.filter_by_service(sample_logs, "db")
        
        assert len(result) == 1
        assert result[0].service == "db"
    
    def test_get_error_count(self, parser, sample_logs):
        """Error sayısı testi"""
        count = parser.get_error_count(sample_logs)
        
        assert count == 2
    
    def test_get_warning_count(self, parser, sample_logs):
        """Warning sayısı testi"""
        count = parser.get_warning_count(sample_logs)
        
        assert count == 1
    
    def test_get_statistics(self, parser, sample_logs):
        """İstatistik testi"""
        stats = parser.get_statistics(sample_logs)
        
        assert stats["total"] == 5
        assert "ERROR" in stats["by_level"]
        assert stats["by_level"]["ERROR"] == 2
        assert stats["error_count"] == 2
        assert stats["warning_count"] == 1
    
    def test_group_by_level(self, parser, sample_logs):
        """Seviyeye göre gruplama testi"""
        grouped = parser.group_by_level(sample_logs)
        
        assert "ERROR" in grouped
        assert "WARNING" in grouped
        assert len(grouped["ERROR"]) == 2
    
    def test_group_by_service(self, parser, sample_logs):
        """Servise göre gruplama testi"""
        grouped = parser.group_by_service(sample_logs)
        
        assert "db" in grouped
        assert "monitor" in grouped
        assert len(grouped["db"]) == 1
    
    def test_to_json(self, parser, sample_logs):
        """JSON dönüşümü testi"""
        result = parser.to_json(sample_logs)
        
        assert isinstance(result, list)
        assert len(result) == 5
        assert all(isinstance(item, dict) for item in result)
    
    def test_empty_logs_statistics(self, parser):
        """Boş log listesi istatistik testi"""
        stats = parser.get_statistics([])
        
        assert stats["total"] == 0
        assert stats["error_rate"] == 0


# Test çalıştırma
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
