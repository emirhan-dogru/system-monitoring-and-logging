"""
Linux Adapter Module
Linux sistemleri için systemd/journalctl adaptörü.
"""

import subprocess
import re
import sys
import os
from typing import List, Optional
from datetime import datetime

# Core modülleri import edebilmek için path ekle
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.service_monitor import ServiceInfo, ServiceStatus
from core.log_collector import LogEntry, LogLevel


class LinuxAdapter:
    """
    Linux sistemleri için servis ve log adaptörü.
    systemctl ve journalctl komutlarını kullanır.
    """

    # journalctl priority mapping
    PRIORITY_MAP = {
        0: LogLevel.EMERGENCY,
        1: LogLevel.ALERT,
        2: LogLevel.CRITICAL,
        3: LogLevel.ERROR,
        4: LogLevel.WARNING,
        5: LogLevel.NOTICE,
        6: LogLevel.INFO,
        7: LogLevel.DEBUG
    }

    def __init__(self):
        """LinuxAdapter başlatıcı."""
        pass

    def _run_command(self, cmd: List[str]) -> tuple:
        """
        Shell komutu çalıştır.
        
        Returns:
            (stdout, stderr, return_code) tuple
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 1
        except Exception as e:
            return "", str(e), 1

    def get_services(self) -> List[ServiceInfo]:
        """
        Tüm systemd servislerini listele.
        
        Returns:
            ServiceInfo listesi
        """
        services = []
        
        # Tüm servisleri listele
        stdout, stderr, code = self._run_command([
            'systemctl', 'list-units', '--type=service', '--all', '--no-pager', '--no-legend'
        ])
        
        if code != 0:
            return services
        
        for line in stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 4:
                name = parts[0].replace('.service', '')
                load_state = parts[1]
                active_state = parts[2]
                sub_state = parts[3]
                description = ' '.join(parts[4:]) if len(parts) > 4 else ""
                
                # Durumu belirle
                if active_state == 'active':
                    status = ServiceStatus.RUNNING
                elif active_state == 'failed':
                    status = ServiceStatus.FAILED
                else:
                    status = ServiceStatus.STOPPED
                
                services.append(ServiceInfo(
                    name=name,
                    display_name=description or name,
                    status=status,
                    description=description
                ))
        
        return services

    def get_service_status(self, service_name: str) -> Optional[ServiceInfo]:
        """
        Belirli bir servisin durumunu al.
        
        Args:
            service_name: Servis adı
            
        Returns:
            ServiceInfo veya None
        """
        stdout, stderr, code = self._run_command([
            'systemctl', 'is-active', service_name
        ])
        
        state = stdout.strip()
        
        if state == 'active':
            status = ServiceStatus.RUNNING
        elif state == 'failed':
            status = ServiceStatus.FAILED
        elif state == 'inactive':
            status = ServiceStatus.STOPPED
        else:
            status = ServiceStatus.UNKNOWN
        
        # PID almaya çalış
        pid = None
        stdout, stderr, code = self._run_command([
            'systemctl', 'show', service_name, '--property=MainPID'
        ])
        if code == 0 and 'MainPID=' in stdout:
            try:
                pid = int(stdout.split('=')[1].strip())
                if pid == 0:
                    pid = None
            except ValueError:
                pass
        
        return ServiceInfo(
            name=service_name,
            display_name=service_name,
            status=status,
            pid=pid
        )

    def get_logs(self,
                 limit: int = 100,
                 level: Optional[LogLevel] = None,
                 service: Optional[str] = None,
                 since: Optional[datetime] = None,
                 until: Optional[datetime] = None) -> List[LogEntry]:
        """
        journalctl ile log oku.
        
        Args:
            limit: Maksimum log sayısı
            level: Minimum log seviyesi
            service: Servis filtresi
            since: Başlangıç tarihi
            until: Bitiş tarihi
            
        Returns:
            LogEntry listesi
        """
        logs = []
        
        cmd = ['journalctl', '--no-pager', '-n', str(limit), '-o', 'short-iso']
        
        # Seviye filtresi
        if level:
            priority = level.value
            cmd.extend(['-p', str(priority)])
        
        # Servis filtresi
        if service:
            cmd.extend(['-u', service])
        
        # Tarih filtreleri
        if since:
            cmd.extend(['--since', since.strftime('%Y-%m-%d %H:%M:%S')])
        if until:
            cmd.extend(['--until', until.strftime('%Y-%m-%d %H:%M:%S')])
        
        stdout, stderr, code = self._run_command(cmd)
        
        if code != 0:
            return logs
        
        # Log satırlarını parse et
        for line in stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            entry = self._parse_log_line(line)
            if entry:
                logs.append(entry)
        
        return logs

    def _parse_log_line(self, line: str) -> Optional[LogEntry]:
        """
        Log satırını parse et.
        
        Format: 2024-01-15T10:30:45+0300 hostname service[pid]: message
        """
        try:
            # ISO timestamp pattern
            pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4})\s+(\S+)\s+(\S+?)(?:\[\d+\])?:\s*(.*)$'
            match = re.match(pattern, line)
            
            if match:
                timestamp_str, hostname, service, message = match.groups()
                
                # Timestamp parse
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('+0000', '+00:00'))
                except Exception:
                    timestamp = datetime.now()
                
                # Seviye tahmini (mesaj içeriğinden)
                level = self._guess_level(message)
                
                return LogEntry(
                    timestamp=timestamp,
                    level=level,
                    message=message,
                    source=hostname,
                    service=service
                )
        except Exception:
            pass
        
        return None

    def _guess_level(self, message: str) -> LogLevel:
        """Mesaj içeriğinden log seviyesi tahmin et"""
        message_lower = message.lower()
        
        if 'error' in message_lower or 'failed' in message_lower or 'failure' in message_lower:
            return LogLevel.ERROR
        elif 'warning' in message_lower or 'warn' in message_lower:
            return LogLevel.WARNING
        elif 'critical' in message_lower or 'crit' in message_lower:
            return LogLevel.CRITICAL
        elif 'debug' in message_lower:
            return LogLevel.DEBUG
        else:
            return LogLevel.INFO


# Test için
if __name__ == "__main__":
    adapter = LinuxAdapter()
    services = adapter.get_services()
    print(f"Found {len(services)} services")
    for s in services[:5]:
        print(f"  - {s.name}: {s.status.value}")
