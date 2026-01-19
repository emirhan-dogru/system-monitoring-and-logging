"""
Windows Adapter Module
Windows sistemleri için Services ve Event Log adaptörü.
"""

import subprocess
import re
import sys
import os
from typing import List, Optional
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import win32evtlog
    import win32evtlogutil
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

# Core modülleri import edebilmek için path ekle
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.service_monitor import ServiceInfo, ServiceStatus
from core.log_collector import LogEntry, LogLevel


class WindowsAdapter:
    """
    Windows sistemleri için servis ve log adaptörü.
    psutil ve Windows Event Log API kullanır.
    """

    # Windows Event Log level mapping
    LEVEL_MAP = {
        1: LogLevel.CRITICAL,   # EVENTLOG_ERROR_TYPE
        2: LogLevel.WARNING,    # EVENTLOG_WARNING_TYPE
        4: LogLevel.INFO,       # EVENTLOG_INFORMATION_TYPE
        8: LogLevel.INFO,       # EVENTLOG_AUDIT_SUCCESS
        16: LogLevel.WARNING    # EVENTLOG_AUDIT_FAILURE
    }

    def __init__(self):
        """WindowsAdapter başlatıcı."""
        if not PSUTIL_AVAILABLE:
            print("Warning: psutil not available. Service monitoring will be limited.")

    def get_services(self) -> List[ServiceInfo]:
        """
        Windows servislerini listele.
        
        Returns:
            ServiceInfo listesi
        """
        services = []
        
        if PSUTIL_AVAILABLE:
            try:
                for service in psutil.win_service_iter():
                    try:
                        info = service.as_dict()
                        
                        # Durumu belirle
                        status_str = info.get('status', 'unknown')
                        if status_str == 'running':
                            status = ServiceStatus.RUNNING
                        elif status_str == 'stopped':
                            status = ServiceStatus.STOPPED
                        elif status_str == 'paused':
                            status = ServiceStatus.STOPPED
                        else:
                            status = ServiceStatus.UNKNOWN
                        
                        services.append(ServiceInfo(
                            name=info.get('name', ''),
                            display_name=info.get('display_name', info.get('name', '')),
                            status=status,
                            description=info.get('description', ''),
                            pid=info.get('pid')
                        ))
                    except Exception:
                        continue
            except Exception as e:
                print(f"Error getting services: {e}")
        else:
            # PowerShell fallback
            services = self._get_services_powershell()
        
        return services

    def _get_services_powershell(self) -> List[ServiceInfo]:
        """PowerShell ile servis listesi al"""
        services = []
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 'Get-Service | Select-Object Name, DisplayName, Status | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                import json
                data = json.loads(result.stdout)
                
                if isinstance(data, dict):
                    data = [data]
                
                for item in data:
                    status_str = str(item.get('Status', 0))
                    
                    # Status enum: 1=Stopped, 4=Running
                    if status_str == '4' or 'Running' in status_str:
                        status = ServiceStatus.RUNNING
                    else:
                        status = ServiceStatus.STOPPED
                    
                    services.append(ServiceInfo(
                        name=item.get('Name', ''),
                        display_name=item.get('DisplayName', ''),
                        status=status
                    ))
        except Exception as e:
            print(f"PowerShell error: {e}")
        
        return services

    def get_service_status(self, service_name: str) -> Optional[ServiceInfo]:
        """
        Belirli bir servisin durumunu al.
        
        Args:
            service_name: Servis adı
            
        Returns:
            ServiceInfo veya None
        """
        if PSUTIL_AVAILABLE:
            try:
                service = psutil.win_service_get(service_name)
                info = service.as_dict()
                
                status_str = info.get('status', 'unknown')
                if status_str == 'running':
                    status = ServiceStatus.RUNNING
                elif status_str == 'stopped':
                    status = ServiceStatus.STOPPED
                else:
                    status = ServiceStatus.UNKNOWN
                
                return ServiceInfo(
                    name=info.get('name', service_name),
                    display_name=info.get('display_name', service_name),
                    status=status,
                    pid=info.get('pid')
                )
            except Exception:
                pass
        
        # PowerShell fallback
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 f'Get-Service -Name "{service_name}" | Select-Object Name, DisplayName, Status | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                import json
                data = json.loads(result.stdout)
                
                status_str = str(data.get('Status', 0))
                if status_str == '4' or 'Running' in status_str:
                    status = ServiceStatus.RUNNING
                else:
                    status = ServiceStatus.STOPPED
                
                return ServiceInfo(
                    name=data.get('Name', service_name),
                    display_name=data.get('DisplayName', service_name),
                    status=status
                )
        except Exception:
            pass
        
        return None

    def get_logs(self,
                 limit: int = 100,
                 level: Optional[LogLevel] = None,
                 service: Optional[str] = None,
                 since: Optional[datetime] = None,
                 until: Optional[datetime] = None) -> List[LogEntry]:
        """
        Windows Event Log oku.
        
        Args:
            limit: Maksimum log sayısı
            level: Minimum log seviyesi
            service: Kaynak filtresi
            since: Başlangıç tarihi
            until: Bitiş tarihi
            
        Returns:
            LogEntry listesi
        """
        logs = []
        
        if WIN32_AVAILABLE:
            logs = self._get_logs_win32(limit, level, service, since, until)
        else:
            logs = self._get_logs_powershell(limit, level, service, since, until)
        
        return logs

    def _get_logs_win32(self, limit, level, service, since, until) -> List[LogEntry]:
        """win32evtlog API ile log oku"""
        logs = []
        
        try:
            hand = win32evtlog.OpenEventLog(None, "System")
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            count = 0
            while count < limit:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                if not events:
                    break
                
                for event in events:
                    if count >= limit:
                        break
                    
                    # Tarih filtresi
                    timestamp = event.TimeGenerated
                    if since and timestamp < since:
                        continue
                    if until and timestamp > until:
                        continue
                    
                    # Seviye belirleme
                    event_type = event.EventType
                    log_level = self.LEVEL_MAP.get(event_type, LogLevel.INFO)
                    
                    # Seviye filtresi
                    if level and log_level.value > level.value:
                        continue
                    
                    # Servis/kaynak filtresi
                    source = event.SourceName
                    if service and source.lower() != service.lower():
                        continue
                    
                    message = ""
                    try:
                        message = win32evtlogutil.SafeFormatMessage(event, "System")
                    except Exception:
                        if event.StringInserts:
                            message = ", ".join([s for s in event.StringInserts if s])
                    
                    logs.append(LogEntry(
                        timestamp=timestamp,
                        level=log_level,
                        message=message[:500] if message else "No message",
                        source="System",
                        service=source
                    ))
                    count += 1
            
            win32evtlog.CloseEventLog(hand)
        except Exception as e:
            print(f"Win32 event log error: {e}")
        
        return logs

    def _get_logs_powershell(self, limit, level, service, since, until) -> List[LogEntry]:
        """PowerShell ile log oku"""
        logs = []
        
        try:
            # PowerShell komutu oluştur
            ps_cmd = f'Get-EventLog -LogName System -Newest {limit}'
            
            if service:
                ps_cmd += f' -Source "{service}"'
            
            if level:
                if level == LogLevel.ERROR:
                    ps_cmd += ' -EntryType Error'
                elif level == LogLevel.WARNING:
                    ps_cmd += ' -EntryType Warning,Error'
            
            ps_cmd += ' | Select-Object TimeGenerated, EntryType, Source, Message | ConvertTo-Json'
            
            result = subprocess.run(
                ['powershell', '-Command', ps_cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                import json
                data = json.loads(result.stdout)
                
                if isinstance(data, dict):
                    data = [data]
                
                for item in data:
                    # Timestamp parse
                    time_str = item.get('TimeGenerated', '')
                    try:
                        # PowerShell date format: /Date(timestamp)/
                        if '/Date(' in time_str:
                            ts = int(re.search(r'/Date\((\d+)\)/', time_str).group(1))
                            timestamp = datetime.fromtimestamp(ts / 1000)
                        else:
                            timestamp = datetime.now()
                    except Exception:
                        timestamp = datetime.now()
                    
                    # Level
                    entry_type = str(item.get('EntryType', 'Information'))
                    if 'Error' in entry_type:
                        log_level = LogLevel.ERROR
                    elif 'Warning' in entry_type:
                        log_level = LogLevel.WARNING
                    else:
                        log_level = LogLevel.INFO
                    
                    # Tarih filtresi
                    if since and timestamp < since:
                        continue
                    if until and timestamp > until:
                        continue
                    
                    message = str(item.get('Message', ''))[:500]
                    
                    logs.append(LogEntry(
                        timestamp=timestamp,
                        level=log_level,
                        message=message or "No message",
                        source="System",
                        service=item.get('Source', '')
                    ))
        except Exception as e:
            print(f"PowerShell event log error: {e}")
        
        return logs


# Test için
if __name__ == "__main__":
    adapter = WindowsAdapter()
    services = adapter.get_services()
    print(f"Found {len(services)} services")
    for s in services[:5]:
        print(f"  - {s.name}: {s.status.value}")
