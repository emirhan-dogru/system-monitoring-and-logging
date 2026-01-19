"""
Log Parser Module
Log ayrıştırma ve filtreleme modülü.
"""

import re
from typing import List, Dict, Optional, Pattern
from .log_collector import LogEntry, LogLevel


class LogParser:
    """
    Log ayrıştırma ve filtreleme sınıfı.
    Regex ile arama, filtreleme ve analiz özellikleri sunar.
    """

    def __init__(self):
        """LogParser başlatıcı."""
        pass

    def filter_by_level(self, logs: List[LogEntry], min_level: LogLevel) -> List[LogEntry]:
        """
        Log seviyesine göre filtrele.
        
        Args:
            logs: Filtrelenecek loglar
            min_level: Minimum log seviyesi (dahil)
            
        Returns:
            Filtrelenmiş log listesi
        """
        return [log for log in logs if log.level.value <= min_level.value]

    def filter_by_regex(self, logs: List[LogEntry], pattern: str) -> List[LogEntry]:
        """
        Regex pattern ile filtrele.
        
        Args:
            logs: Filtrelenecek loglar
            pattern: Regex pattern
            
        Returns:
            Eşleşen log listesi
        """
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            return [log for log in logs if compiled.search(log.message)]
        except re.error:
            return []

    def filter_by_keyword(self, logs: List[LogEntry], keyword: str) -> List[LogEntry]:
        """
        Anahtar kelime ile filtrele.
        
        Args:
            logs: Filtrelenecek loglar
            keyword: Aranacak kelime
            
        Returns:
            Eşleşen log listesi
        """
        keyword_lower = keyword.lower()
        return [log for log in logs if keyword_lower in log.message.lower()]

    def filter_by_service(self, logs: List[LogEntry], service_name: str) -> List[LogEntry]:
        """
        Servis adına göre filtrele.
        
        Args:
            logs: Filtrelenecek loglar
            service_name: Servis adı
            
        Returns:
            Filtrelenmiş log listesi
        """
        return [log for log in logs if log.service.lower() == service_name.lower()]

    def get_error_count(self, logs: List[LogEntry]) -> int:
        """ERROR seviyesindeki log sayısı"""
        return len([log for log in logs if log.level == LogLevel.ERROR])

    def get_warning_count(self, logs: List[LogEntry]) -> int:
        """WARNING seviyesindeki log sayısı"""
        return len([log for log in logs if log.level == LogLevel.WARNING])

    def get_critical_count(self, logs: List[LogEntry]) -> int:
        """CRITICAL ve üstü log sayısı"""
        return len([log for log in logs if log.level.value <= LogLevel.CRITICAL.value])

    def group_by_level(self, logs: List[LogEntry]) -> Dict[str, List[LogEntry]]:
        """
        Logları seviyeye göre grupla.
        
        Returns:
            Seviye -> LogEntry listesi sözlüğü
        """
        grouped = {}
        for log in logs:
            level_name = log.level.name
            if level_name not in grouped:
                grouped[level_name] = []
            grouped[level_name].append(log)
        return grouped

    def group_by_service(self, logs: List[LogEntry]) -> Dict[str, List[LogEntry]]:
        """
        Logları servise göre grupla.
        
        Returns:
            Servis -> LogEntry listesi sözlüğü
        """
        grouped = {}
        for log in logs:
            service = log.service or "unknown"
            if service not in grouped:
                grouped[service] = []
            grouped[service].append(log)
        return grouped

    def get_statistics(self, logs: List[LogEntry]) -> Dict:
        """
        Detaylı log istatistikleri hesapla.
        
        Returns:
            İstatistik sözlüğü
        """
        if not logs:
            return {
                "total": 0,
                "by_level": {},
                "by_service": {},
                "error_rate": 0,
                "warning_rate": 0
            }

        total = len(logs)
        by_level = {}
        by_service = {}

        for log in logs:
            # Level sayımı
            level_name = log.level.name
            by_level[level_name] = by_level.get(level_name, 0) + 1

            # Servis sayımı
            service = log.service or "unknown"
            by_service[service] = by_service.get(service, 0) + 1

        error_count = by_level.get("ERROR", 0)
        warning_count = by_level.get("WARNING", 0)

        return {
            "total": total,
            "by_level": by_level,
            "by_service": by_service,
            "error_count": error_count,
            "warning_count": warning_count,
            "error_rate": round(error_count / total * 100, 2),
            "warning_rate": round(warning_count / total * 100, 2)
        }

    def find_patterns(self, logs: List[LogEntry], patterns: Dict[str, str]) -> Dict[str, List[LogEntry]]:
        """
        Birden fazla pattern ile eşleştirme yap.
        
        Args:
            logs: Aranacak loglar
            patterns: İsim -> regex pattern sözlüğü
            
        Returns:
            Pattern ismi -> eşleşen loglar sözlüğü
        """
        results = {}
        for name, pattern in patterns.items():
            results[name] = self.filter_by_regex(logs, pattern)
        return results

    def to_json(self, logs: List[LogEntry]) -> List[Dict]:
        """Logları JSON formatına dönüştür"""
        return [log.to_dict() for log in logs]


# Test için
if __name__ == "__main__":
    parser = LogParser()
    print("LogParser initialized successfully")
