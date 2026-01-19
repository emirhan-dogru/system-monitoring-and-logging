#!/usr/bin/env python3
"""
Monitoring & Logging Panel - Main Entry Point
Ana giriş noktası ve CLI arayüzü.
"""

import argparse
import sys
import os

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config


def self_check():
    """
    Self-check / Auto Test mekanizması.
    Tüm modüllerin doğru çalıştığını kontrol eder.
    """
    print("=" * 50)
    print("[*] Self-Check / Auto Test")
    print("=" * 50)
    
    checks = []
    
    # Core modülleri kontrol et
    try:
        from core.service_monitor import ServiceMonitor, ServiceStatus
        monitor = ServiceMonitor()
        summary = monitor.get_service_summary()
        checks.append(("Service Monitor", True, f"{summary['total']} servis bulundu"))
    except Exception as e:
        checks.append(("Service Monitor", False, str(e)))
    
    try:
        from core.log_collector import LogCollector
        collector = LogCollector()
        stats = collector.get_log_statistics()
        checks.append(("Log Collector", True, f"{stats['total']} log okundu"))
    except Exception as e:
        checks.append(("Log Collector", False, str(e)))
    
    try:
        from core.log_parser import LogParser
        parser = LogParser()
        checks.append(("Log Parser", True, "OK"))
    except Exception as e:
        checks.append(("Log Parser", False, str(e)))
    
    try:
        from core.alert_manager import AlertManager
        manager = AlertManager()
        summary = manager.get_alert_summary()
        checks.append(("Alert Manager", True, "OK"))
    except Exception as e:
        checks.append(("Alert Manager", False, str(e)))
    
    # Sonuçları yazdır
    print()
    all_passed = True
    for name, passed, message in checks:
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {name}: {message}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("[SUCCESS] Tum kontroller basarili!")
        return True
    else:
        print("[ERROR] Bazi kontroller basarisiz!")
        return False


def list_services():
    """Servisleri listele"""
    from core.service_monitor import ServiceMonitor
    
    monitor = ServiceMonitor()
    services = monitor.get_all_services()
    
    print(f"\n{'='*60}")
    print(f"Platform: {monitor.platform.upper()}")
    print(f"Toplam Servis: {len(services)}")
    print(f"{'='*60}\n")
    
    # Duruma göre grupla
    running = [s for s in services if s.status.value == 'running']
    stopped = [s for s in services if s.status.value == 'stopped']
    failed = [s for s in services if s.status.value == 'failed']
    
    print(f"[+] Calisan: {len(running)}")
    print(f"[-] Durmus: {len(stopped)}")
    print(f"[!] Hatali: {len(failed)}")
    
    print(f"\n{'-'*60}")
    print(f"{'Servis':<40} {'Durum':<15}")
    print(f"{'-'*60}")
    
    for s in services[:30]:  # İlk 30 servis
        status_icon = {
            'running': '[+]',
            'stopped': '[-]',
            'failed': '[!]'
        }.get(s.status.value, '[ ]')
        
        critical = "[CRITICAL]" if s.is_critical else ""
        print(f"{s.name:<40} {status_icon} {s.status.value:<10} {critical}")
    
    if len(services) > 30:
        print(f"\n... ve {len(services) - 30} servis daha")


def show_logs(level=None, limit=20):
    """Log göster"""
    from core.log_collector import LogCollector, LogLevel
    from core.log_parser import LogParser
    
    collector = LogCollector()
    parser = LogParser()
    
    log_level = None
    if level:
        level_map = {
            'error': LogLevel.ERROR,
            'warning': LogLevel.WARNING,
            'info': LogLevel.INFO
        }
        log_level = level_map.get(level.lower())
    
    logs = collector.get_logs(limit=limit, level=log_level)
    stats = parser.get_statistics(logs)
    
    print(f"\n{'='*70}")
    print(f"Log Istatistikleri")
    print(f"{'='*70}\n")
    
    print(f"Toplam: {stats['total']}")
    for level_name, count in stats.get('by_level', {}).items():
        print(f"  {level_name}: {count}")
    
    print(f"\n{'-'*70}")
    print(f"{'Zaman':<20} {'Seviye':<10} {'Servis':<15} {'Mesaj':<25}")
    print(f"{'-'*70}")
    
    for log in logs[:limit]:
        time_str = log.timestamp.strftime("%Y-%m-%d %H:%M")
        message = log.message[:35] + "..." if len(log.message) > 35 else log.message
        service = log.service[:12] if log.service else "-"
        print(f"{time_str:<20} {log.level.name:<10} {service:<15} {message}")


def watch_critical():
    """Kritik servisleri izle"""
    import time
    from core.service_monitor import ServiceMonitor
    from core.alert_manager import AlertManager
    
    monitor = ServiceMonitor()
    alert_manager = AlertManager()
    
    print("\n[*] Kritik servis izleme baslatildi...")
    print("Cikmak icin Ctrl+C basin\n")
    
    try:
        while True:
            critical_down = monitor.get_critical_down_services()
            
            if critical_down:
                print(f"\n[!] {len(critical_down)} kritik servis durmus!")
                for service in critical_down:
                    print(f"  [X] {service.name}")
            else:
                print("[OK] Tum kritik servisler calisiyor", end="\r")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nIzleme durduruldu.")


def run_server():
    """Web sunucusunu başlat"""
    from web.app import run_server as start_server
    
    print(f"\n{'='*50}")
    print("[*] Monitoring & Logging Panel")
    print(f"{'='*50}")
    print(f"Sunucu baslatiliyor: http://{config.host}:{config.port}")
    print("Durdurmak icin Ctrl+C basin")
    print(f"{'='*50}\n")
    
    start_server(host=config.host, port=config.port, debug=config.debug)


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="Monitoring & Logging Panel - Cross-platform sistem izleme aracı"
    )
    
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="Self-check / Auto Test çalıştır"
    )
    
    parser.add_argument(
        "--list-services",
        action="store_true",
        help="Servisleri listele"
    )
    
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Son logları göster"
    )
    
    parser.add_argument(
        "--level",
        choices=["error", "warning", "info"],
        help="Log seviyesi filtresi"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Gösterilecek maksimum log sayısı"
    )
    
    parser.add_argument(
        "--watch-critical",
        action="store_true",
        help="Kritik servisleri canlı izle"
    )
    
    parser.add_argument(
        "--host",
        default=config.host,
        help="Sunucu adresi"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=config.port,
        help="Sunucu portu"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug modunu etkinleştir"
    )
    
    args = parser.parse_args()
    
    # Update config
    config.host = args.host
    config.port = args.port
    config.debug = args.debug
    
    # Execute command
    if args.self_check:
        success = self_check()
        sys.exit(0 if success else 1)
    elif args.list_services:
        list_services()
    elif args.logs:
        show_logs(level=args.level, limit=args.limit)
    elif args.watch_critical:
        watch_critical()
    else:
        # Default: run web server
        run_server()


if __name__ == "__main__":
    main()
