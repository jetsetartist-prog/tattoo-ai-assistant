"""
Часть 2: Шаблоны HTML для клиентов и услуг.
Создаёт:
- templates/clients.html
- templates/client_detail.html
- templates/services.html
- templates/service_edit.html
- templates/client_edit.html

Запуск: python install_crm_part2.py
"""
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"


# ============================================
# 1. clients.html — список клиентов
# ============================================

CLIENTS_HTML = """<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ t('clients_title', admin_lang) }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: #075e54; color: white; }
        .header-top { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px 10px 40px; }
        .header-top h1 { font-size: 20px; }
        .header-nav { display: flex; gap: 20px; padding: 0 40px 14px 40px; }
        .header-nav a { color: white; text-decoration: none; font-size: 14px; opacity: 0.8; }
        .header-nav a:hover { opacity: 1; }
        .header-nav a.active { opacity: 1; font-weight: 600; border-bottom: 2px solid #25d366; padding-bottom: 2px; }
        .lang-switch { display: flex; gap: 5px; }
        .lang-btn { padding: 3px 8px; background: rgba(255,255,255,0.15); color: white; text-decoration: none; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .lang-btn.active { background: #25d366; }

        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .card h2 { color: #075e54; font-size: 20px; }
        .search-box { display: flex; gap: 8px; }
        .search-box input {
            padding: 10px 16px; border: 2px solid #e0e0e0; border-radius: 8px;
            font-size: 14px; outline: none; width: 250px;
        }
        .search-box input:focus { border-color: #25d366; }
        .search-box button {
            padding: 10px 20px; background: #25d366; color: white; border: none;
            border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer;
        }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th { text-align: left; padding: 12px; background: #f9f9f9; color: #666; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        td { padding: 14px 12px; border-bottom: 1px solid #eee; }
        tr:hover { background: #fafafa; cursor: pointer; }
        .empty { text-align: center; padding: 60px 20px; color: #999; }
        .empty-icon { font-size: 48px; margin-bottom: 16px; }
        .btn-new {
            display: inline-block; padding: 10px 20px; background: #075e54; color: white;
            text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 600;
        }
        .btn-new:hover { background: #064a42; }
    </style>
</head>
<body>
    {% include '_nav.html' %}

    <div class="container">
        <div class="card">
            <div class="card-header">
                <h2>👥 {{ t('clients_title', admin_lang) }}</h2>
                <form class="search-box" method="GET" action="/admin/clients">
                    <input type="text" name="q" placeholder="{{ t('clients_search', admin_lang) }}" value="{{ search or '' }}">
                    <button type="submit">🔍</button>
                </form>
            </div>

            {% if clients %}
            <table>
                <thead>
                    <tr>
                        <th>{{ t('clients_th_name', admin_lang) }}</th>
                        <th>{{ t('clients_th_phone', admin_lang) }}</th>
                        <th>{{ t('clients_th_email', admin_lang) }}</th>
                        <th>{{ t('clients_th_created', admin_lang) }}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for c in clients %}
                    <tr onclick="window.location='/admin/clients/{{ c.id }}'">
                        <td><b>{{ c.name or '—' }}</b></td>
                        <td>{{ c.phone or '—' }}</td>
                        <td>{{ c.email or '—' }}</td>
                        <td>{{ c.created_at[:10] if c.created_at else '—' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="empty">
                <div class="empty-icon">👥</div>
                <p>{{ t('clients_empty', admin_lang) }}</p>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


# ============================================
# 2. client_detail.html — карточка клиента
# ============================================

CLIENT_DETAIL_HTML = """<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ client.name or 'Клиент' }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: #075e54; color: white; }
        .header-top { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px 10px 40px; }
        .header-top h1 { font-size: 20px; }
        .header-nav { display: flex; gap: 20px; padding: 0 40px 14px 40px; }
        .header-nav a { color: white; text-decoration: none; font-size: 14px; opacity: 0.8; }
        .header-nav a:hover { opacity: 1; }
        .header-nav a.active { opacity: 1; font-weight: 600; border-bottom: 2px solid #25d366; padding-bottom: 2px; }
        .lang-switch { display: flex; gap: 5px; }
        .lang-btn { padding: 3px 8px; background: rgba(255,255,255,0.15); color: white; text-decoration: none; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .lang-btn.active { background: #25d366; }

        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .card h2 { color: #075e54; font-size: 20px; margin-bottom: 20px; }
        .info-grid { display: grid; grid-template-columns: 180px 1fr; gap: 16px; font-size: 15px; }
        .info-grid .label { color: #666; font-weight: 500; }
        .info-grid .value { color: #333; }

        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 20px; }
        .stat { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .stat .label { font-size: 12px; color: #666; margin-bottom: 8px; }
        .stat .value { font-size: 26px; font-weight: 700; color: #075e54; }

        .notes-box { background: #f9f9f9; border-left: 4px solid #25d366; padding: 16px 20px; border-radius: 8px; color: #333; font-size: 15px; line-height: 1.6; white-space: pre-wrap; }

        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th { text-align: left; padding: 12px; background: #f9f9f9; color: #666; font-weight: 600; font-size: 12px; text-transform: uppercase; }
        td { padding: 14px 12px; border-bottom: 1px solid #eee; }
        tr:hover { background: #fafafa; cursor: pointer; }
        .status { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
        .status-pending { background: #fff3e0; color: #e65100; }
        .status-confirmed { background: #e8f5e9; color: #2e7d32; }
        .status-cancelled { background: #ffebee; color: #c62828; }

        .actions { display: flex; gap: 12px; margin-top: 20px; }
        .btn { padding: 12px 24px; border-radius: 8px; font-size: 15px; font-weight: 600; text-decoration: none; display: inline-block; border: none; cursor: pointer; }
        .btn-primary { background: #25d366; color: white; }
        .btn-primary:hover { background: #1ebe5d; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
    </style>
</head>
<body>
    {% include '_nav.html' %}

    <div class="container">
        <div class="card">
            <h2>👤 {{ client.name or 'Клиент' }}</h2>

            <div class="info-grid">
                <div class="label">{{ t('clients_th_name', admin_lang) }}:</div>
                <div class="value">{{ client.name or '—' }}</div>

                <div class="label">{{ t('clients_th_phone', admin_lang) }}:</div>
                <div class="value">{{ client.phone or '—' }}</div>

                <div class="label">{{ t('clients_th_email', admin_lang) }}:</div>
                <div class="value">{{ client.email or '—' }}</div>

                <div class="label">{{ t('clients_th_created', admin_lang) }}:</div>
                <div class="value">{{ client.created_at[:10] if client.created_at else '—' }}</div>
            </div>

            {% if client.notes %}
            <div style="margin-top: 24px;">
                <div class="label" style="color: #666; font-weight: 500; margin-bottom: 8px;">💬 {{ t('clients_notes', admin_lang) }}:</div>
                <div class="notes-box">{{ client.notes }}</div>
            </div>
            {% endif %}

            <div class="actions">
                <a href="/admin/clients" class="btn btn-secondary">← {{ t('clients_back', admin_lang) }}</a>
                <a href="/admin/clients/edit/{{ client.id }}" class="btn btn-primary">✎ {{ t('clients_edit', admin_lang) }}</a>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat">
                <div class="label">{{ t('client_stat_total', admin_lang) }}</div>
                <div class="value">{{ stats.total_bookings }}</div>
            </div>
            <div class="stat">
                <div class="label">{{ t('client_stat_confirmed', admin_lang) }}</div>
                <div class="value">{{ stats.confirmed_bookings }}</div>
            </div>
            <div class="stat">
                <div class="label">{{ t('client_stat_revenue', admin_lang) }}</div>
                <div class="value">{{ stats.total_revenue }} {{ currency_symbol }}</div>
            </div>
            <div class="stat">
                <div class="label">{{ t('client_stat_avg', admin_lang) }}</div>
                <div class="value">{{ stats.average_check }} {{ currency_symbol }}</div>
            </div>
        </div>

        <div class="card">
            <h2>📅 {{ t('client_bookings_history', admin_lang) }}</h2>

            {% if bookings %}
            <table>
                <thead>
                    <tr>
                        <th>{{ t('bookings_th_date', admin_lang) }}</th>
                        <th>{{ t('bookings_th_time', admin_lang) }}</th>
                        <th>{{ t('bookings_th_size', admin_lang) }}</th>
                        <th>{{ t('bookings_th_status', admin_lang) }}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for b in bookings %}
                    <tr onclick="window.location='/admin/bookings/{{ b.id }}'">
                        <td><b>{{ b.date }}</b></td>
                        <td>{{ b.time }}</td>
                        <td>{{ b.service_name or '—' }}</td>
                        <td>
                            {% if b.status == 'pending' %}
                            <span class="status status-pending">{{ t('bookings_status_pending', admin_lang) }}</span>
                            {% elif b.status == 'confirmed' %}
                            <span class="status status-confirmed">{{ t('bookings_status_confirmed', admin_lang) }}</span>
                            {% elif b.status == 'cancelled' %}
                            <span class="status status-cancelled">{{ t('bookings_status_cancelled', admin_lang) }}</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="empty">
                <div class="empty-icon">📭</div>
                <p>{{ t('client_bookings_empty', admin_lang) }}</p>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


# ============================================
# 3. services.html — список услуг
# ============================================

SERVICES_HTML = """<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ t('services_title', admin_lang) }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: #075e54; color: white; }
        .header-top { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px 10px 40px; }
        .header-top h1 { font-size: 20px; }
        .header-nav { display: flex; gap: 20px; padding: 0 40px 14px 40px; }
        .header-nav a { color: white; text-decoration: none; font-size: 14px; opacity: 0.8; }
        .header-nav a:hover { opacity: 1; }
        .header-nav a.active { opacity: 1; font-weight: 600; border-bottom: 2px solid #25d366; padding-bottom: 2px; }
        .lang-switch { display: flex; gap: 5px; }
        .lang-btn { padding: 3px 8px; background: rgba(255,255,255,0.15); color: white; text-decoration: none; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .lang-btn.active { background: #25d366; }

        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .card h2 { color: #075e54; font-size: 20px; }
        .btn-new { display: inline-block; padding: 12px 24px; background: #25d366; color: white; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 600; }
        .btn-new:hover { background: #1ebe5d; }

        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th { text-align: left; padding: 12px; background: #f9f9f9; color: #666; font-weight: 600; font-size: 12px; text-transform: uppercase; }
        td { padding: 14px 12px; border-bottom: 1px solid #eee; }
        .actions-cell { display: flex; gap: 6px; }
        .btn-sm { padding: 6px 12px; border-radius: 6px; font-size: 12px; text-decoration: none; font-weight: 600; }
        .btn-edit { background: #f0f0f0; color: #333; }
        .btn-edit:hover { background: #e0e0e0; }
        .btn-delete { background: #ffebee; color: #c62828; }
        .btn-delete:hover { background: #ffcdd2; }
    </style>
</head>
<body>
    {% include '_nav.html' %}

    <div class="container">
        <div class="card">
            <div class="card-header">
                <h2>💰 {{ t('services_title', admin_lang) }}</h2>
                <a href="/admin/services/new" class="btn-new">➕ {{ t('services_new', admin_lang) }}</a>
            </div>

            {% if services %}
            <table>
                <thead>
                    <tr>
                        <th>{{ t('services_th_name', admin_lang) }}</th>
                        <th>{{ t('services_th_duration', admin_lang) }}</th>
                        <th>{{ t('services_th_price', admin_lang) }}</th>
                        <th>{{ t('services_th_buffer', admin_lang) }}</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {% for s in services %}
                    <tr>
                        <td><b>{{ s.name }}</b></td>
                        <td>{{ s.duration_minutes // 60 }}{{ t('booking_hours_short', admin_lang) }} {{ s.duration_minutes % 60 }}мин</td>
                        <td>{{ s.price_from }} {{ currency_symbol }}</td>
                        <td>{{ s.buffer_minutes or 30 }} мин</td>
                        <td>
                            <div class="actions-cell">
                                <a href="/admin/services/edit/{{ s.id }}" class="btn-sm btn-edit">✎</a>
                                <a href="/admin/services/delete/{{ s.id }}"
                                   class="btn-sm btn-delete"
                                   onclick="return confirm('{{ t('services_delete_confirm', admin_lang) }}')">🗑</a>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="empty">
                <div class="empty-icon">💰</div>
                <p>{{ t('services_empty', admin_lang) }}</p>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


# ============================================
# 4. service_edit.html — создание/редактирование услуги
# ============================================

SERVICE_EDIT_HTML = """<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ t('service_edit_title', admin_lang) }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: #075e54; color: white; }
        .header-top { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px 10px 40px; }
        .header-top h1 { font-size: 20px; }
        .header-nav { display: flex; gap: 20px; padding: 0 40px 14px 40px; }
        .header-nav a { color: white; text-decoration: none; font-size: 14px; opacity: 0.8; }
        .header-nav a:hover { opacity: 1; }
        .header-nav a.active { opacity: 1; font-weight: 600; border-bottom: 2px solid #25d366; padding-bottom: 2px; }
        .lang-switch { display: flex; gap: 5px; }
        .lang-btn { padding: 3px 8px; background: rgba(255,255,255,0.15); color: white; text-decoration: none; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .lang-btn.active { background: #25d366; }

        .container { max-width: 600px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .card h2 { color: #075e54; font-size: 20px; margin-bottom: 24px; }
        label { display: block; color: #333; font-size: 13px; margin-bottom: 6px; font-weight: 500; }
        .required { color: #c00; }
        input[type="text"], input[type="number"] {
            width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 8px;
            font-size: 15px; outline: none; margin-bottom: 8px;
        }
        input:focus { border-color: #25d366; }
        .hint { display: block; font-size: 12px; color: #999; margin-bottom: 16px; }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .field { margin-bottom: 16px; }
        .actions { display: flex; gap: 12px; margin-top: 24px; }
        .btn { padding: 14px 28px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-primary { background: #25d366; color: white; }
        .btn-primary:hover { background: #1ebe5d; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
        .alert-error { background: #ffe5e5; color: #c00; padding: 14px 18px; border-radius: 8px; font-size: 14px; margin-bottom: 20px; border-left: 4px solid #c00; }
    </style>
</head>
<body>
    {% include '_nav.html' %}

    <div class="container">
        <div class="card">
            <h2>{{ t('service_edit_title', admin_lang) }}</h2>

            {% if error %}
            <div class="alert-error">{{ error }}</div>
            {% endif %}

            <form method="POST">
                <div class="field">
                    <label>{{ t('services_th_name', admin_lang) }} <span class="required">*</span></label>
                    <input type="text" name="name" value="{{ service.name if service else '' }}" required autofocus>
                </div>

                <div class="row">
                    <div class="field">
                        <label>{{ t('service_hours', admin_lang) }}</label>
                        <input type="number" name="hours" min="0" max="24" value="{{ (service.duration_minutes // 60) if service else 1 }}">
                    </div>
                    <div class="field">
                        <label>{{ t('service_minutes', admin_lang) }}</label>
                        <input type="number" name="minutes" min="0" max="59" step="5" value="{{ (service.duration_minutes % 60) if service else 0 }}">
                    </div>
                </div>
                <span class="hint">{{ t('service_duration_hint', admin_lang) }}</span>

                <div class="field">
                    <label>{{ t('services_th_price', admin_lang) }} ({{ currency_symbol }})</label>
                    <input type="number" name="price_from" min="0" value="{{ service.price_from if service else 0 }}">
                </div>

                <div class="field">
                    <label>{{ t('services_th_buffer', admin_lang) }} ({{ t('service_minutes', admin_lang) }})</label>
                    <input type="number" name="buffer_minutes" min="0" max="120" step="5" value="{{ service.buffer_minutes if service else 30 }}">
                    <span class="hint">{{ t('service_buffer_hint', admin_lang) }}</span>
                </div>

                <div class="actions">
                    <button type="submit" class="btn btn-primary">💾 {{ t('service_save', admin_lang) }}</button>
                    <a href="/admin/services" class="btn btn-secondary">← {{ t('service_cancel', admin_lang) }}</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""


# ============================================
# 5. client_edit.html — редактирование клиента
# ============================================

CLIENT_EDIT_HTML = """<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ t('client_edit_title', admin_lang) }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: #075e54; color: white; }
        .header-top { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px 10px 40px; }
        .header-top h1 { font-size: 20px; }
        .header-nav { display: flex; gap: 20px; padding: 0 40px 14px 40px; }
        .header-nav a { color: white; text-decoration: none; font-size: 14px; opacity: 0.8; }
        .header-nav a.active { opacity: 1; font-weight: 600; border-bottom: 2px solid #25d366; padding-bottom: 2px; }
        .lang-switch { display: flex; gap: 5px; }
        .lang-btn { padding: 3px 8px; background: rgba(255,255,255,0.15); color: white; text-decoration: none; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .lang-btn.active { background: #25d366; }

        .container { max-width: 600px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .card h2 { color: #075e54; font-size: 20px; margin-bottom: 24px; }
        label { display: block; color: #333; font-size: 13px; margin-bottom: 6px; font-weight: 500; }
        input[type="text"], input[type="tel"], input[type="email"], textarea {
            width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 8px;
            font-size: 15px; outline: none; margin-bottom: 16px; font-family: inherit;
        }
        input:focus, textarea:focus { border-color: #25d366; }
        textarea { resize: vertical; min-height: 80px; }
        .actions { display: flex; gap: 12px; margin-top: 8px; }
        .btn { padding: 14px 28px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-primary { background: #25d366; color: white; }
        .btn-primary:hover { background: #1ebe5d; }
        .btn-secondary { background: #f0f0f0; color: #333; }
    </style>
</head>
<body>
    {% include '_nav.html' %}

    <div class="container">
        <div class="card">
            <h2>✎ {{ t('client_edit_title', admin_lang) }}</h2>

            <form method="POST">
                <label>{{ t('clients_th_name', admin_lang) }}</label>
                <input type="text" name="name" value="{{ client.name or '' }}">

                <label>{{ t('clients_th_phone', admin_lang) }}</label>
                <input type="tel" name="phone" value="{{ client.phone or '' }}">

                <label>{{ t('clients_th_email', admin_lang) }}</label>
                <input type="email" name="email" value="{{ client.email or '' }}">

                <label>{{ t('clients_notes', admin_lang) }}</label>
                <textarea name="notes" placeholder="{{ t('client_notes_ph', admin_lang) }}">{{ client.notes or '' }}</textarea>

                <div class="actions">
                    <button type="submit" class="btn btn-primary">💾 {{ t('client_save', admin_lang) }}</button>
                    <a href="/admin/clients/{{ client.id }}" class="btn btn-secondary">← {{ t('client_cancel', admin_lang) }}</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_part2_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    print(f"📦 Бэкап: {backup_dir.name}")
    print()


def create_file(name: str, content: str):
    path = TEMPLATES / name
    path.write_text(content, encoding='utf-8')
    print(f"  ✅ templates/{name}")


def main():
    print("=" * 60)
    print("🚀 Часть 2: Шаблоны HTML (клиенты + услуги)")
    print("=" * 60)
    print()

    backup()

    print("📄 Создание шаблонов:")
    create_file("clients.html", CLIENTS_HTML)
    create_file("client_detail.html", CLIENT_DETAIL_HTML)
    create_file("services.html", SERVICES_HTML)
    create_file("service_edit.html", SERVICE_EDIT_HTML)
    create_file("client_edit.html", CLIENT_EDIT_HTML)
    print()

    print("=" * 60)
    print("✅ ЧАСТЬ 2 ГОТОВА")
    print("=" * 60)
    print()
    print("Дальше — Часть 3: маршруты в web_demo.py + переводы + меню")
    print()


if __name__ == '__main__':
    main()