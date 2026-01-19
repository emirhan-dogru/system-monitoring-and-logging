"""
Flask Web Application
Monitoring & Logging Dashboard web uygulaması.
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import os
import sys

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.service_monitor import ServiceMonitor
from core.log_collector import LogCollector, LogLevel
from core.log_parser import LogParser
from core.alert_manager import AlertManager, AlertType, AlertSeverity

# Flask uygulaması
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.config['SECRET_KEY'] = 'monitoring-logging-secret-key'

# SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Core modüller
service_monitor = ServiceMonitor()
log_collector = LogCollector()
log_parser = LogParser()
alert_manager = AlertManager()


# ===== HTML Routes =====

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


# ===== API Routes =====

@app.route('/api/status')
def api_status():
    """Sistem durumu"""
    return jsonify({
        'status': 'ok',
        'platform': service_monitor.platform,
        'version': '1.0.0'
    })


@app.route('/api/services')
def api_services():
    """Servis listesi"""
    filter_status = request.args.get('status', None)
    
    services = service_monitor.get_all_services()
    
    # Duruma göre filtrele
    if filter_status == 'running':
        services = [s for s in services if s.status.value == 'running']
    elif filter_status == 'stopped':
        services = [s for s in services if s.status.value == 'stopped']
    elif filter_status == 'failed':
        services = [s for s in services if s.status.value == 'failed']
    elif filter_status == 'critical':
        services = [s for s in services if s.is_critical]
    
    return jsonify({
        'services': [s.to_dict() for s in services],
        'count': len(services)
    })


@app.route('/api/services/summary')
def api_services_summary():
    """Servis özeti"""
    return jsonify(service_monitor.get_service_summary())


@app.route('/api/services/<service_name>')
def api_service_detail(service_name):
    """Servis detayı"""
    service = service_monitor.get_service_status(service_name)
    if service:
        return jsonify(service.to_dict())
    return jsonify({'error': 'Service not found'}), 404


@app.route('/api/logs')
def api_logs():
    """Log listesi"""
    limit = request.args.get('limit', 100, type=int)
    level = request.args.get('level', None)
    service = request.args.get('service', None)
    search = request.args.get('search', None)
    
    # Seviye filtresi
    log_level = None
    if level:
        level_map = {
            'error': LogLevel.ERROR,
            'warning': LogLevel.WARNING,
            'info': LogLevel.INFO,
            'debug': LogLevel.DEBUG
        }
        log_level = level_map.get(level.lower())
    
    logs = log_collector.get_logs(limit=limit, level=log_level, service=service)
    
    # Arama filtresi
    if search:
        logs = log_parser.filter_by_keyword(logs, search)
    
    return jsonify({
        'logs': log_parser.to_json(logs),
        'count': len(logs),
        'statistics': log_parser.get_statistics(logs)
    })


@app.route('/api/logs/statistics')
def api_logs_statistics():
    """Log istatistikleri"""
    logs = log_collector.get_logs(limit=100)
    return jsonify(log_parser.get_statistics(logs))


@app.route('/api/alerts')
def api_alerts():
    """Uyarı listesi"""
    active_only = request.args.get('active', 'true').lower() == 'true'
    
    if active_only:
        alerts = alert_manager.get_active_alerts()
    else:
        alerts = alert_manager.alerts
    
    return jsonify({
        'alerts': [a.to_dict() for a in alerts],
        'count': len(alerts),
        'summary': alert_manager.get_alert_summary()
    })


@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
def api_acknowledge_alert(alert_id):
    """Uyarıyı onayla"""
    if alert_manager.acknowledge_alert(alert_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Alert not found'}), 404


@app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
def api_resolve_alert(alert_id):
    """Uyarıyı çöz"""
    if alert_manager.resolve_alert(alert_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Alert not found'}), 404


@app.route('/api/dashboard')
def api_dashboard():
    """Dashboard özeti"""
    # Servis özeti
    service_summary = service_monitor.get_service_summary()
    
    # Log istatistikleri
    logs = log_collector.get_logs(limit=100)
    log_stats = log_parser.get_statistics(logs)
    
    # Uyarı özeti
    alert_summary = alert_manager.get_alert_summary()
    
    # Kritik servis kontrolü
    critical_down = service_monitor.get_critical_down_services()
    for service in critical_down:
        alert_manager.check_service_status(
            service.name, 
            is_running=False, 
            is_critical=True
        )
    
    # Hata oranı kontrolü
    alert_manager.check_error_rate(
        log_stats.get('error_count', 0),
        log_stats.get('total', 1)
    )
    
    return jsonify({
        'services': service_summary,
        'logs': log_stats,
        'alerts': alert_summary,
        'platform': service_monitor.platform
    })


# ===== WebSocket Events =====

@socketio.on('connect')
def handle_connect():
    """WebSocket bağlantısı"""
    emit('connected', {'status': 'ok'})


@socketio.on('request_update')
def handle_request_update():
    """Güncel veri talebi"""
    emit('dashboard_update', {
        'services': service_monitor.get_service_summary(),
        'alerts': alert_manager.get_alert_summary()
    })


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Sunucuyu başlat"""
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_server(debug=True)
