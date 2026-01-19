/**
 * Monitoring & Logging Panel - Dashboard JavaScript
 * Frontend interactivity and API communication
 */

// ===== Global State =====
let currentTab = 'dashboard';
let servicesData = [];
let logsData = [];
let alertsData = [];

// ===== Charts =====
let serviceChart = null;
let logChart = null;

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Tab navigation
    setupNavigation();

    // Initial data load
    refreshData();

    // Auto refresh every 30 seconds
    setInterval(refreshData, 30000);

    console.log('Dashboard initialized');
}

// ===== Navigation =====
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tab = item.dataset.tab;
            switchTab(tab);
        });
    });
}

function switchTab(tab) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.tab === tab);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tab}-tab`);
    });

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'services': 'Servisler',
        'logs': 'Loglar',
        'alerts': 'Uyarılar'
    };
    document.getElementById('page-title').textContent = titles[tab] || tab;

    currentTab = tab;

    // Load tab-specific data
    if (tab === 'services') loadServices();
    else if (tab === 'logs') loadLogs();
    else if (tab === 'alerts') loadAlerts();
}

// ===== Data Loading =====
async function refreshData() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();

        // Update platform info
        document.getElementById('platform-name').textContent =
            data.platform === 'windows' ? 'Windows' : 'Linux';

        // Update stats
        document.getElementById('stat-running').textContent = data.services.running || 0;
        document.getElementById('stat-stopped').textContent = data.services.stopped || 0;
        document.getElementById('stat-errors').textContent = data.logs.error_count || 0;
        document.getElementById('stat-alerts').textContent = data.alerts.active || 0;

        // Update alert badge
        const alertBadge = document.getElementById('alert-badge');
        alertBadge.textContent = data.alerts.active || 0;
        alertBadge.style.display = data.alerts.active > 0 ? 'flex' : 'none';

        // Update charts
        updateServiceChart(data.services);
        updateLogChart(data.logs);

        // Update last update time
        document.getElementById('last-update-time').textContent = new Date().toLocaleTimeString('tr-TR');

        // Load alerts for recent section
        loadRecentAlerts();

    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}

// ===== Services =====
async function loadServices() {
    const container = document.getElementById('services-list');
    container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Yükleniyor...</p></div>';

    try {
        const filter = document.getElementById('service-filter').value;
        const url = filter ? `/api/services?status=${filter}` : '/api/services';

        const response = await fetch(url);
        const data = await response.json();

        servicesData = data.services;
        renderServices(servicesData);

    } catch (error) {
        console.error('Error loading services:', error);
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Servisler yüklenemedi</p></div>';
    }
}

function renderServices(services) {
    const container = document.getElementById('services-list');

    if (services.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-server"></i><p>Servis bulunamadı</p></div>';
        return;
    }

    container.innerHTML = services.map(service => `
        <div class="service-card">
            <div class="service-status ${service.status}"></div>
            <div class="service-info">
                <div class="service-name">${escapeHtml(service.name)}</div>
                <div class="service-display-name">${escapeHtml(service.display_name)}</div>
            </div>
            ${service.is_critical ? '<span class="service-badge critical">Kritik</span>' : ''}
        </div>
    `).join('');
}

function filterServices() {
    loadServices();
}

function searchServices() {
    const search = document.getElementById('service-search').value.toLowerCase();
    const filtered = servicesData.filter(s =>
        s.name.toLowerCase().includes(search) ||
        s.display_name.toLowerCase().includes(search)
    );
    renderServices(filtered);
}

// ===== Logs =====
async function loadLogs() {
    const container = document.getElementById('logs-list');
    container.innerHTML = '<tr><td colspan="4" class="loading"><i class="fas fa-spinner fa-spin"></i> Yükleniyor...</td></tr>';

    try {
        const level = document.getElementById('log-level-filter').value;
        const limit = document.getElementById('log-limit').value;

        let url = `/api/logs?limit=${limit}`;
        if (level) url += `&level=${level}`;

        const response = await fetch(url);
        const data = await response.json();

        logsData = data.logs;
        renderLogs(logsData);

    } catch (error) {
        console.error('Error loading logs:', error);
        container.innerHTML = '<tr><td colspan="4" class="loading">Loglar yüklenemedi</td></tr>';
    }
}

function renderLogs(logs) {
    const container = document.getElementById('logs-list');

    if (logs.length === 0) {
        container.innerHTML = '<tr><td colspan="4" class="loading">Log bulunamadı</td></tr>';
        return;
    }

    container.innerHTML = logs.map(log => `
        <tr>
            <td class="log-timestamp">${formatTimestamp(log.timestamp)}</td>
            <td><span class="log-level ${log.level.toLowerCase()}">${log.level}</span></td>
            <td class="log-service">${escapeHtml(log.service || '-')}</td>
            <td class="log-message" title="${escapeHtml(log.message)}">${escapeHtml(log.message)}</td>
        </tr>
    `).join('');
}

function filterLogs() {
    loadLogs();
}

function searchLogs() {
    const search = document.getElementById('log-search').value.toLowerCase();
    const filtered = logsData.filter(log =>
        log.message.toLowerCase().includes(search) ||
        (log.service && log.service.toLowerCase().includes(search))
    );
    renderLogs(filtered);
}

// ===== Alerts =====
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();

        alertsData = data.alerts;

        // Update counts
        document.getElementById('critical-count').textContent =
            `${data.summary.critical || 0} Kritik`;
        document.getElementById('high-count').textContent =
            `${data.summary.high || 0} Yüksek`;

        renderAlerts(alertsData);

    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

async function loadRecentAlerts() {
    try {
        const response = await fetch('/api/alerts?active=true');
        const data = await response.json();

        const container = document.getElementById('recent-alerts');

        if (data.alerts.length === 0) {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-check-circle"></i><p>Aktif uyarı yok</p></div>';
            return;
        }

        container.innerHTML = data.alerts.slice(0, 5).map(alert => `
            <div class="alert-item ${alert.severity}">
                <div class="alert-item-header">
                    <span class="alert-title">${escapeHtml(alert.title)}</span>
                    <span class="alert-time">${formatTimestamp(alert.timestamp)}</span>
                </div>
                <div class="alert-message">${escapeHtml(alert.message)}</div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading recent alerts:', error);
    }
}

function renderAlerts(alerts) {
    const container = document.getElementById('alerts-list');

    if (alerts.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-check-circle"></i><p>Aktif uyarı yok</p></div>';
        return;
    }

    container.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.severity}">
            <div class="alert-item-header">
                <span class="alert-title">${escapeHtml(alert.title)}</span>
                <span class="alert-time">${formatTimestamp(alert.timestamp)}</span>
            </div>
            <div class="alert-message">${escapeHtml(alert.message)}</div>
            <div class="alert-actions">
                ${!alert.acknowledged ? `<button class="alert-btn acknowledge" onclick="acknowledgeAlert('${alert.id}')">Onayla</button>` : ''}
                ${!alert.resolved ? `<button class="alert-btn resolve" onclick="resolveAlert('${alert.id}')">Çözüldü</button>` : ''}
            </div>
        </div>
    `).join('');
}

async function acknowledgeAlert(alertId) {
    try {
        await fetch(`/api/alerts/${alertId}/acknowledge`, { method: 'POST' });
        loadAlerts();
    } catch (error) {
        console.error('Error acknowledging alert:', error);
    }
}

async function resolveAlert(alertId) {
    try {
        await fetch(`/api/alerts/${alertId}/resolve`, { method: 'POST' });
        loadAlerts();
        refreshData();
    } catch (error) {
        console.error('Error resolving alert:', error);
    }
}

// ===== Charts =====
function updateServiceChart(data) {
    const ctx = document.getElementById('service-chart');
    if (!ctx) return;

    if (serviceChart) {
        serviceChart.destroy();
    }

    serviceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Çalışan', 'Durmuş', 'Hatalı'],
            datasets: [{
                data: [data.running || 0, data.stopped || 0, data.failed || 0],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a0a0b0',
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            cutout: '65%'
        }
    });
}

function updateLogChart(data) {
    const ctx = document.getElementById('log-chart');
    if (!ctx) return;

    if (logChart) {
        logChart.destroy();
    }

    const byLevel = data.by_level || {};

    logChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(byLevel),
            datasets: [{
                label: 'Log Sayısı',
                data: Object.values(byLevel),
                backgroundColor: Object.keys(byLevel).map(level => {
                    const colors = {
                        'ERROR': '#ef4444',
                        'WARNING': '#f59e0b',
                        'INFO': '#3b82f6',
                        'DEBUG': '#6c6c7c',
                        'CRITICAL': '#dc2626'
                    };
                    return colors[level] || '#6c5ce7';
                }),
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#a0a0b0'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    },
                    ticks: {
                        color: '#a0a0b0'
                    }
                }
            }
        }
    });
}

// ===== Utilities =====
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTimestamp(isoString) {
    if (!isoString) return '-';
    try {
        const date = new Date(isoString);
        return date.toLocaleString('tr-TR', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return isoString;
    }
}
