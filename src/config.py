"""
Configuration Module
Uygulama yapılandırması.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Uygulama yapılandırma sınıfı"""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    
    # Monitoring settings
    refresh_interval: int = 30  # seconds
    
    # Alert thresholds
    error_threshold: int = 10
    warning_threshold: int = 20
    
    # Critical services
    critical_services: List[str] = field(default_factory=lambda: [
        # Linux
        "sshd", "nginx", "apache2", "mysql", "postgresql", "docker",
        # Windows
        "Spooler", "BITS", "wuauserv", "Dhcp", "Dnscache", "EventLog"
    ])
    
    # Log settings
    max_log_entries: int = 1000
    log_retention_days: int = 7


# Default configuration
config = Config()


def load_config_from_env():
    """Environment variable'lardan yapılandırma yükle"""
    global config
    
    config.host = os.environ.get("MONITOR_HOST", config.host)
    config.port = int(os.environ.get("MONITOR_PORT", config.port))
    config.debug = os.environ.get("MONITOR_DEBUG", "false").lower() == "true"
    
    config.error_threshold = int(os.environ.get("MONITOR_ERROR_THRESHOLD", config.error_threshold))
    config.warning_threshold = int(os.environ.get("MONITOR_WARNING_THRESHOLD", config.warning_threshold))


# Load on import
load_config_from_env()
