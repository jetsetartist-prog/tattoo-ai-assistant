"""
ЭТАП 1b: Автоподсказка клиентов (без предупреждений о дубликатах).

Что делает:
1. web_demo.py: маршрут /admin/api/clients/search — автоподсказка
2. new_booking.html: автоподсказка при вводе имени
3. Переводы

Запуск: python install_stage1b_client_autocomplete.py
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"
I18N = BASE / "core" / "i18n"
WEB_DEMO = BASE / "web_demo.py"


# ============================================
# 1. МАРШРУТ ПОИСКА
# ============================================

ROUTE_SEARCH = '''

# ============================================
# API: ПОИСК КЛИЕНТОВ
# ============================================

@app.route('/admin/api/clients/search')
def admin_api_clients_search():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return jsonify([])

    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])

    from core.storage.clients import get_all_clients
    clients = get_all_clients(search=query)

    result = []
    for c in clients[:10]:
        result.append({
            'id': c['id'],
            'name': c['name'] or '',
            'phone': c['phone'] or '',
        })

    return jsonify(result)
'''


# ============================================
# 2. NEW_BOOKING_HTML
# ============================================

NEW_BOOKING_HTML = """<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ t('new_booking_title', admin_lang) }}</title>
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

        .container { max-width: 700px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .card h2 { color: #075e54; font-size: 20px; margin-bottom: 8px; }
        .subtitle { color: #666; font-size: 14px; margin-bottom: 24px; }
        label { display: block; color: #333; font-size: 13px; margin-bottom: 6px; font-weight: 500; }
        .required { color: #c00; }
        input[type="text"], input[type="tel"], input[type="date"], input[type="time"], input[type="number"], select, textarea {
            width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 8px;
            font-size: 15px; outline: none; margin-bottom: 8px; font-family: inherit;
        }
        input:focus, select:focus, textarea:focus { border-color: #25d366; }
        textarea { resize: vertical; min-height: 80px; }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .field { margin-bottom: 16px; position: relative; }
        .field input, .field select, .field textarea { margin-bottom: 0; }
        .actions { margin-top: 24px; display: flex; gap: 12px; }
        .btn { padding: 14px 28px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-primary { background: #25d366; color: white; }
        .btn-primary:hover { background: #1ebe5d; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
        .alert-error { background: #ffe5e5; color: #c00; padding: 14px 18px; border-radius: 8px; font-size: 14px; margin-bottom: 20px; border-left: 4px solid #c00; }
        .hint { display: block; font-size: 12px; color: #999; margin-top: 6px; margin-bottom: 16px; }
        .file-input-wrap {
            border: 2px dashed #ccc;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            margin-bottom: 16px;
        }
        .file-input-wrap:hover { border-color: #25d366; }
        .file-input-wrap input[type="file"] { display: none; }
        .file-preview { margin-top: 12px; display: none; }
        .file-preview img { max-width: 200px; max-height: 200px; border-radius: 8px; border: 2px solid #e0e0e0; }

        .autocomplete-list {
            position: absolute;
            top: 100%; left: 0; right: 0;
            background: white;
            border: 2px solid #25d366;
            border-top: none;
            border-radius: 0 0 8px 8px;
            max-height: 250px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .autocomplete-list.show { display: block; }
        .autocomplete-item {
            padding: 12px 16px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
        }
        .autocomplete-item:hover { background: #f0f8f5; }
        .autocomplete-item:last-child { border-bottom: none; }
        .autocomplete-item .ac-name { font-weight: 600; color: #075e54; }
        .autocomplete-item .ac-phone { color: #666; font-size: 13px; }
        .autocomplete-item .ac-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
            background: #e8f5e9;
            color: #2e7d32;
            margin-left: 8px;
        }

        .selected-client {
            background: #e8f5e9;
            border: 2px solid #25d366;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 16px;
            font-size: 14px;
            display: none;
        }
        .selected-client.show { display: block; }
        .selected-client .sc-title { font-weight: 600; color: #2e7d32; margin-bottom: 4px; }
        .selected-client .sc-info { color: #666; }
        .selected-client .sc-clear { float: right; color: #c00; cursor: pointer; font-size: 18px; line-height: 1; }
    </style>
</head>
<body>
    {% include '_nav.html' %}

    <div class="container">
        <div class="card">
            <h2>{{ t('new_booking_title', admin_lang) }}</h2>
            <p class="subtitle">{{ t('new_booking_subtitle', admin_lang) }}</p>

            {% if error %}
            <div class="alert-error">{{ error }}</div>
            {% endif %}

            <form method="POST" action="/admin/bookings/new" enctype="multipart/form-data">
                <div class="selected-client" id="selected_client">
                    <span class="sc-clear" onclick="clearSelectedClient()">✕</span>
                    <div class="sc-title">✓ {{ t('client_selected', admin_lang) }}</div>
                    <div class="sc-info" id="selected_client_info"></div>
                </div>

                <input type="hidden" name="client_id" id="client_id" value="">

                <div class="field">
                    <label>{{ t('new_booking_name', admin_lang) }} <span class="required">*</span></label>
                    <input type="text" name="name" id="name_input" value="{{ prefill_name or '' }}" required autofocus autocomplete="off">
                    <div class="autocomplete-list" id="autocomplete_list"></div>
                </div>

                <div class="field">
                    <label>{{ t('new_booking_phone', admin_lang) }} <span class="required">*</span></label>
                    <input type="tel" name="phone" id="phone_input" value="{{ prefill_phone or '' }}" required>
                </div>

                <div class="field">
                    <label>{{ t('new_booking_service', admin_lang) }} <span class="required">*</span></label>
                    <select name="service_id" required>
                        <option value="">{{ t('new_booking_select_service', admin_lang) }}</option>
                        {% for s in services %}
                        <option value="{{ s.id }}" {% if prefill_service_id == s.id %}selected{% endif %}>
                            {{ s.name }} — {{ s.duration_minutes // 60 }}ч — от {{ s.price_from }} {{ currency_symbol }}
                        </option>
                        {% endfor %}
                    </select>
                </div>

                <div class="row">
                    <div class="field">
                        <label>{{ t('new_booking_date', admin_lang) }} <span class="required">*</span></label>
                        <input type="date" name="date" value="{{ prefill_date or '' }}" required min="{{ today }}">
                    </div>
                    <div class="field">
                        <label>{{ t('new_booking_time', admin_lang) }} <span class="required">*</span></label>
                        <input type="time" name="time" value="{{ prefill_time or '' }}" required step="1800">
                        <span class="hint">{{ t('new_booking_time_hint', admin_lang) }}</span>
                    </div>
                </div>

                <div class="field">
                    <label>{{ t('new_booking_notes', admin_lang) }}</label>
                    <textarea name="notes" placeholder="{{ t('new_booking_notes_ph', admin_lang) }}">{{ prefill_notes or '' }}</textarea>
                </div>

                <div class="field">
                    <label>{{ t('new_booking_image', admin_lang) }}</label>
                    <label class="file-input-wrap" for="file_input">
                        <div class="file-input-label" id="file_label">📎 {{ t('new_booking_image_hint', admin_lang) }}</div>
                        <input type="file" id="file_input" name="reference_image" accept="image/*" onchange="previewFile(this)">
                    </label>
                    <div class="file-preview" id="file_preview">
                        <img id="preview_img" src="" alt="Preview">
                    </div>
                </div>

                <div class="row">
                    <div class="field">
                        <label>{{ t('new_booking_price', admin_lang) }} ({{ currency_symbol }})</label>
                        <input type="number" name="price" min="0" value="{{ prefill_price or 0 }}">
                    </div>
                    <div class="field">
                        <label>{{ t('new_booking_deposit', admin_lang) }} ({{ currency_symbol }})</label>
                        <input type="number" name="deposit" min="0" value="{{ prefill_deposit or 0 }}">
                    </div>
                </div>

                <div class="actions">
                    <button type="submit" class="btn btn-primary">{{ t('new_booking_save', admin_lang) }}</button>
                    <a href="/admin/calendar" class="btn btn-secondary">{{ t('new_booking_cancel', admin_lang) }}</a>
                </div>
            </form>
        </div>
    </div>

    <script>
        function previewFile(input) {
            const preview = document.getElementById('file_preview');
            const img = document.getElementById('preview_img');
            const label = document.getElementById('file_label');
            if (input.files && input.files[0]) {
                const file = input.files[0];
                label.textContent = '📎 ' + file.name;
                const reader = new FileReader();
                reader.onload = function(e) { img.src = e.target.result; preview.style.display = 'block'; };
                reader.readAsDataURL(file);
            } else {
                label.textContent = '📎 {{ t("new_booking_image_hint", admin_lang) }}';
                preview.style.display = 'none';
            }
        }

        const nameInput = document.getElementById('name_input');
        const phoneInput = document.getElementById('phone_input');
        const clientIdInput = document.getElementById('client_id');
        const acList = document.getElementById('autocomplete_list');
        const selectedClient = document.getElementById('selected_client');
        const selectedClientInfo = document.getElementById('selected_client_info');

        let searchTimeout = null;

        nameInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            if (query.length < 2) { acList.classList.remove('show'); return; }

            searchTimeout = setTimeout(() => {
                fetch('/admin/api/clients/search?q=' + encodeURIComponent(query))
                    .then(r => r.json())
                    .then(clients => {
                        if (clients.length === 0) { acList.classList.remove('show'); return; }
                        acList.innerHTML = '';
                        clients.forEach(c => {
                            const item = document.createElement('div');
                            item.className = 'autocomplete-item';
                            item.innerHTML = `<div class="ac-name">${c.name}<span class="ac-badge">{{ t('client_existing', admin_lang) }}</span></div><div class="ac-phone">${c.phone}</div>`;
                            item.onclick = () => selectClient(c);
                            acList.appendChild(item);
                        });
                        acList.classList.add('show');
                    })
                    .catch(() => acList.classList.remove('show'));
            }, 300);
        });

        function selectClient(client) {
            nameInput.value = client.name;
            phoneInput.value = client.phone;
            clientIdInput.value = client.id;
            selectedClientInfo.textContent = client.name + ' · ' + client.phone;
            selectedClient.classList.add('show');
            acList.classList.remove('show');
        }

        function clearSelectedClient() {
            clientIdInput.value = '';
            selectedClient.classList.remove('show');
        }

        document.addEventListener('click', function(e) {
            if (!nameInput.contains(e.target) && !acList.contains(e.target)) {
                acList.classList.remove('show');
            }
        });
    </script>
</body>
</html>
"""


# ============================================
# 3. ПЕРЕВОДЫ
# ============================================

I18N_RU = {
    "client_selected": "Выбран клиент",
    "client_existing": "из базы",
}

I18N_EN = {
    "client_selected": "Client selected",
    "client_existing": "from base",
}

I18N_HE = {
    "client_selected": "לקוח נבחר",
    "client_existing": "מהמאגר",
}


# ============================================
# ФУНКЦИИ
# ============================================

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f"backup_stage1b_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    if TEMPLATES.exists():
        shutil.copytree(TEMPLATES, backup_dir / "templates", dirs_exist_ok=True)
    if WEB_DEMO.exists():
        shutil.copy(WEB_DEMO, backup_dir / "web_demo.py")
    print(f"📦 Бэкап: {backup_dir.name}")
    print()


def update_template():
    path = TEMPLATES / "new_booking.html"
    path.write_text(NEW_BOOKING_HTML, encoding='utf-8')
    print("  ✅ new_booking.html обновлён")


def update_web_demo():
    if not WEB_DEMO.exists():
        return
    content = WEB_DEMO.read_text(encoding='utf-8')
    if '/admin/api/clients/search' not in content:
        marker = "if __name__ == '__main__':"
        if marker in content:
            content = content.replace(marker, ROUTE_SEARCH + "\n\n" + marker, 1)
            print("  ✅ web_demo.py: маршрут поиска")
    else:
        print("  ⏭️  web_demo.py: маршрут уже есть")
    WEB_DEMO.write_text(content, encoding='utf-8')


def update_i18n():
    for lang, data in [('ru', I18N_RU), ('en', I18N_EN), ('he', I18N_HE)]:
        path = I18N / f"{lang}.json"
        if not path.exists():
            continue
        with open(path, encoding='utf-8') as f:
            existing = json.load(f)
        before = len(existing)
        existing.update(data)
        after = len(existing)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {lang}.json: {before} → {after}")


def main():
    print("=" * 60)
    print("🚀 ЭТАП 1b: Автоподсказка клиентов")
    print("=" * 60)
    print()

    backup()
    update_template()
    update_web_demo()
    update_i18n()

    print()
    print("=" * 60)
    print("✅ ЭТАП 1b ГОТОВ")
    print("=" * 60)
    print()
    print("Что делает:")
    print("  - При вводе имени → подсказка клиентов из базы")
    print("  - Выбор клиента → подставляется телефон")
    print("  - Без предупреждений о дубликатах")
    print()


if __name__ == '__main__':
    main()