"""
Локальный веб-эмулятор мессенджера + кабинет мастера.
Запуск: python web_demo.py
Открыть: http://localhost:5000
Кабинет: http://localhost:5000/admin
"""
import asyncio
import os
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import (
    Flask, render_template_string, request, jsonify,
    redirect, make_response,
)
from loguru import logger
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

from core.handlers.message_handler import handle_incoming
from core.messaging.base import IncomingMessage, MessageAdapter
from core.storage.leads import init_db
from core.auth.mailer import init_mail, send_master_password
from core.auth.storage import (
    generate_password,
    create_session, get_session, destroy_session,
)
from core.storage.schedule import (
    get_default_master, get_all_work_hours, set_work_hours,
    get_master_by_email, set_master_password, has_password,
    get_master, get_bookings, cancel_booking, confirm_booking, update_booking_price, delete_booking,
    create_manual_booking, get_booking, update_booking,
    get_free_slots_admin, get_all_services, get_service,
)
from core.storage.stats import (
    get_period_stats, get_upcoming_count, get_recent_bookings,
)
from core.i18n.translator import t
from core.storage.clients import (
    get_or_create_client, get_client, get_all_clients,
    get_client_stats, get_client_bookings, update_client,
)
from core.storage.services import (
    get_all_services as get_services_list, get_service as get_service_by_id,
    create_service, update_service, delete_service,
)
from core.storage.settings import (
    get_currency, set_currency, get_currency_symbol,
    get_currency_for_lang, sync_currency_with_lang, is_currency_manual,
    get_all_currencies,
)

# Инициализация БД
init_db()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me-in-env")
init_mail(app)

# Хранилище ответов для каждого сеанса
sessions = {}


class WebAdapter(MessageAdapter):
    """Адаптер-заглушка: вместо отправки в мессенджер — кладет ответ в сессию."""
    def __init__(self, session_id):
        self.session_id = session_id

    @property
    def platform_name(self):
        return "web"

    async def send_message(self, chat_id, text, buttons=None):
        if self.session_id not in sessions:
            sessions[self.session_id] = []
        btn_list = []
        if buttons:
            btn_list = [{"label": b.label, "color": b.color} for b in buttons]
        sessions[self.session_id].append({"text": text, "buttons": btn_list})

    async def start(self, handler):
        pass


HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AI-ассистент тату-салона</title>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #e5ddd5;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .phone {
        width: 420px;
        height: 90vh;
        max-height: 800px;
        background: #ece5dd;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .header {
        background: #075e54;
        color: white;
        padding: 15px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #25d366;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .header-info h3 { font-size: 16px; font-weight: 500; }
    .header-info p { font-size: 12px; opacity: 0.8; }

    #chat {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .msg {
        max-width: 75%;
        padding: 8px 12px;
        border-radius: 12px;
        font-size: 14px;
        line-height: 1.4;
        word-wrap: break-word;
        position: relative;
        animation: fadeIn 0.2s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .msg.user {
        align-self: flex-end;
        background: #dcf8c6;
        border-bottom-right-radius: 3px;
    }
    .msg.bot {
        align-self: flex-start;
        background: white;
        border-bottom-left-radius: 3px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .msg .buttons {
        margin-top: 8px;
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
    }
    .msg .buttons button {
        background: #075e54;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 15px;
        font-size: 12px;
        cursor: pointer;
        transition: background 0.2s;
    }
    .msg .buttons button:hover { background: #064a42; }

    .input-area {
        background: #f0f0f0;
        padding: 10px 15px;
        display: flex;
        gap: 8px;
        align-items: center;
    }
    .input-area input {
        flex: 1;
        padding: 10px 15px;
        border: none;
        border-radius: 20px;
        font-size: 14px;
        outline: none;
    }
    .input-area button {
        background: #25d366;
        color: white;
        border: none;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
    }
    .input-area button:hover { background: #1ebe5d; }

    .typing {
        align-self: flex-start;
        background: white;
        padding: 12px 16px;
        border-radius: 12px;
        display: flex;
        gap: 4px;
    }
    .typing span {
        width: 7px;
        height: 7px;
        background: #999;
        border-radius: 50%;
        animation: blink 1.4s infinite;
    }
    .typing span:nth-child(2) { animation-delay: 0.2s; }
    .typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink {
        0%, 60%, 100% { opacity: 0.3; }
        30% { opacity: 1; }
    }
</style>
</head>
<body>
<div class="phone">
    <div class="header">
        <div class="avatar">💉</div>
        <div class="header-info">
            <h3>Tattoo AI Assistant</h3>
            <p>онлайн</p>
        </div>
    </div>
    <div id="chat"></div>
    <form class="input-area" onsubmit="event.preventDefault(); send();">
        <input id="msg" type="text" placeholder="Напишите сообщение..." autocomplete="off">
        <button type="submit">➤</button>
    </form>
</div>

<script>
const chat = document.getElementById('chat');

function scrollDown() { chat.scrollTop = chat.scrollHeight; }

function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'msg user';
    div.textContent = text;
    chat.appendChild(div);
    scrollDown();
}

function addBotMessage(text, buttons) {
    const div = document.createElement('div');
    div.className = 'msg bot';
    div.textContent = text;
    if (buttons && buttons.length > 0) {
        const btnBox = document.createElement('div');
        btnBox.className = 'buttons';
        for (const b of buttons) {
            const btn = document.createElement('button');
            btn.textContent = b.label;
            btn.onclick = () => sendText(b.label);
            btnBox.appendChild(btn);
        }
        div.appendChild(btnBox);
    }
    chat.appendChild(div);
    scrollDown();
}

function showTyping() {
    const div = document.createElement('div');
    div.className = 'typing';
    div.id = 'typing';
    div.innerHTML = '<span></span><span></span><span></span>';
    chat.appendChild(div);
    scrollDown();
}

function hideTyping() {
    const t = document.getElementById('typing');
    if (t) t.remove();
}

async function sendText(text) {
    if (!text) return;
    addUserMessage(text);
    showTyping();
    try {
        const resp = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: text, session: 'demo'})
        });
        const data = await resp.json();
        hideTyping();
        for (const m of data.messages) {
            addBotMessage(m.text, m.buttons);
        }
    } catch (e) {
        hideTyping();
        addBotMessage('⚠️ Ошибка соединения', []);
    }
}

function send() {
    const input = document.getElementById('msg');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    sendText(text);
}

window.onload = () => {
    addBotMessage(
        '👋 Привет! Я AI-ассистент тату-салона.\\nВыбери действие:',
        [
            {label: 'Записаться', color: 'primary'},
            {label: 'Прайс', color: 'secondary'},
            {label: 'Портфолио', color: 'secondary'},
            {label: 'Контакты', color: 'secondary'}
        ]
    );
};
</script>
</body>
</html>
"""


# ============================================
# ЧАТ
# ============================================

@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    text = data.get('text', '')
    session_id = data.get('session', 'demo')

    sessions[session_id] = []

    msg = IncomingMessage(
        platform="web",
        user_id="demo_user",
        chat_id="demo_chat",
        text=text,
    )
    adapter = WebAdapter(session_id)

    asyncio.run(handle_incoming(msg, adapter))

    return jsonify({"messages": sessions.get(session_id, [])})


# ============================================
# ШАБЛОНЫ
# ============================================

def get_admin_lang() -> str:
    """Возвращает язык кабинета из query-параметра или cookie."""
    lang_from_query = request.args.get('lang', '').strip().lower()
    if lang_from_query in ('ru', 'en', 'he'):
        return lang_from_query

    lang_from_cookie = request.cookies.get('admin_lang', '').strip().lower()
    if lang_from_cookie in ('ru', 'en', 'he'):
        return lang_from_cookie

    return 'ru'


def _render_template_file(filename: str, **kwargs):
    if 'admin_lang' not in kwargs:
        kwargs['admin_lang'] = get_admin_lang()

    # Синхронизация валюты с языком
    try:
        sync_currency_with_lang(kwargs['admin_lang'])
    except Exception:
        pass

    if 't' not in kwargs:
        kwargs['t'] = t

    # Добавляем валюту во все шаблоны
    if 'currency' not in kwargs:
        try:
            kwargs['currency'] = get_currency()
            kwargs['currency_symbol'] = get_currency_symbol()
        except Exception:
            kwargs['currency'] = 'RUB'
            kwargs['currency_symbol'] = '₽'

    path = os.path.join(os.path.dirname(__file__), 'templates', filename)
    with open(path, encoding='utf-8') as f:
        return render_template_string(f.read(), **kwargs)



# ============================================
# АВТОРИЗАЦИЯ
# ============================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return _render_template_file('login.html', error=None, info=None)

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not email or not password:
        return _render_template_file(
            'login.html',
            error='Введите email и пароль',
            info=None,
        ), 400

    master = get_master_by_email(email)
    if not master:
        return _render_template_file(
            'login.html',
            error='Мастер с таким email не найден',
            info=None,
        ), 400

    if not master.get('password_hash'):
        return _render_template_file(
            'login.html',
            error='Пароль ещё не установлен. Нажмите «Забыли пароль?»',
            info=None,
        ), 400

    if not check_password_hash(master['password_hash'], password):
        return _render_template_file(
            'login.html',
            error='Неверный пароль',
            info=None,
        ), 400

    token = create_session(email)
    resp = make_response(redirect('/admin'))
    resp.set_cookie('admin_session', token, httponly=True, max_age=7 * 24 * 3600)
    return resp


@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def admin_forgot_password():
    if request.method == 'GET':
        return _render_template_file('forgot_password.html', error=None, info=None)

    email = request.form.get('email', '').strip().lower()
    master = get_master_by_email(email)

    if not master:
        return _render_template_file(
            'forgot_password.html',
            error='Мастер с таким email не найден',
            info=None,
        ), 400

    new_password = generate_password()
    password_hash = generate_password_hash(new_password)
    set_master_password(master['id'], password_hash)

    ok = send_master_password(email, new_password)
    if not ok:
        return _render_template_file(
            'forgot_password.html',
            error='Не удалось отправить письмо. Попробуйте позже.',
            info=None,
        ), 500

    return _render_template_file(
        'forgot_password.html',
        error=None,
        info=f'Новый пароль отправлен на {email}. Проверьте почту.',
    )


@app.route('/admin/logout')
def admin_logout():
    token = request.cookies.get('admin_session')
    if token:
        destroy_session(token)
    resp = make_response(redirect('/admin/login'))
    resp.delete_cookie('admin_session')
    return resp


@app.route('/admin')
def admin_dashboard():
    token = request.cookies.get('admin_session')
    email = get_session(token) if token else None

    if not email:
        return redirect('/admin/login')

    return _render_template_file('admin.html', email=email, active='home')


# ============================================
# РАСПИСАНИЕ
# ============================================

@app.route('/admin/schedule', methods=['GET', 'POST'])
def admin_schedule():
    token = request.cookies.get('admin_session')
    email = get_session(token) if token else None

    if not email:
        return redirect('/admin/login')

    master = get_default_master()
    if not master:
        return "Мастер не найден", 500

    saved = False

    if request.method == 'POST':
        for weekday in range(7):
            is_working = f'working_{weekday}' in request.form
            start = request.form.get(f'start_{weekday}', '10:00')
            end = request.form.get(f'end_{weekday}', '20:00')
            set_work_hours(master['id'], weekday, start, end, is_working)
        saved = True

    hours = get_all_work_hours(master['id'])
    hours_by_weekday = {h['weekday']: h for h in hours}

    weekdays_ru = [
        "Понедельник", "Вторник", "Среда",
        "Четверг", "Пятница", "Суббота", "Воскресенье"
    ]

    days = []
    for wd in range(7):
        h = hours_by_weekday.get(wd, {
            'weekday': wd,
            'start_time': '10:00',
            'end_time': '20:00',
            'is_working': 0,
        })
        days.append({
            'weekday': wd,
            'name': weekdays_ru[wd],
            'start_time': h['start_time'],
            'end_time': h['end_time'],
            'is_working': bool(h['is_working']),
        })

    return _render_template_file('schedule.html', days=days, saved=saved, active='schedule')


# ============================================
# СПИСОК ЗАПИСЕЙ
# ============================================

@app.route('/admin/bookings')
def admin_bookings():
    token = request.cookies.get('admin_session')
    email = get_session(token) if token else None

    if not email:
        return redirect('/admin/login')

    master = get_default_master()
    if not master:
        return "Мастер не найден", 500

    filter_type = request.args.get('filter', 'all')

    all_bookings = get_bookings(master['id'])

    today = datetime.now().date().isoformat()

    if filter_type == 'upcoming':
        bookings = [b for b in all_bookings if b['date'] >= today and b['status'] != 'cancelled']
    elif filter_type == 'pending':
        bookings = [b for b in all_bookings if b['status'] == 'pending']
    elif filter_type == 'past':
        bookings = [b for b in all_bookings if b['date'] < today]
    else:
        bookings = all_bookings

    conn = sqlite3.connect(os.getenv("SQLITE_PATH", "data/leads.db"))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    enriched = []
    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    for b in bookings:
        cur.execute("SELECT * FROM leads WHERE id = ?", (b['lead_id'],))
        lead = cur.fetchone()

        cur.execute("SELECT * FROM services WHERE id = ?", (b['service_id'],))
        service = cur.fetchone()

        try:
            dt = datetime.strptime(b['date'], "%Y-%m-%d").date()
            date_human = f"{dt.strftime('%d.%m.%Y')} ({weekdays_ru[dt.weekday()]})"
        except Exception:
            date_human = b['date']

        enriched.append({
            'id': b['id'],
            'date': b['date'],
            'date_human': date_human,
            'time': b['time'],
            'duration': b['duration'],
            'status': b['status'],
            'name': lead['name'] if lead else '—',
            'phone': lead['phone'] if lead else '—',
            'service_name': service['name'] if service else '—',
        })

    conn.close()

    return _render_template_file(
        'bookings.html',
        bookings=enriched,
        filter_type=filter_type,
        active='bookings',
    )


@app.route('/admin/bookings/confirm/<int:booking_id>')
def admin_booking_confirm(booking_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    confirm_booking(booking_id)
    return redirect('/admin/bookings')


@app.route('/admin/bookings/cancel/<int:booking_id>')
def admin_booking_cancel(booking_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    cancel_booking(booking_id)
    return redirect('/admin/bookings')


# ============================================
# КАЛЕНДАРЬ
# ============================================

@app.route('/admin/calendar')
def admin_calendar():
    token = request.cookies.get('admin_session')
    email = get_session(token) if token else None

    if not email:
        return redirect('/admin/login')

    master = get_default_master()
    if not master:
        return "Мастер не найден", 500

    week_offset = int(request.args.get('week_offset', 0))

    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    sunday = monday + timedelta(days=6)

    all_bookings = get_bookings(master['id'])

    conn = sqlite3.connect(os.getenv("SQLITE_PATH", "data/leads.db"))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    from core.storage.schedule import get_all_work_hours, is_day_off, _time_to_minutes
    work_hours_list = get_all_work_hours(master['id'])
    work_hours_by_weekday = {wh['weekday']: wh for wh in work_hours_list}

    all_hours = set()
    for wh in work_hours_list:
        if wh.get('is_working'):
            start_h = _time_to_minutes(wh['start_time']) // 60
            end_h = _time_to_minutes(wh['end_time']) // 60
            for h in range(start_h, end_h):
                all_hours.add(h)

    if all_hours:
        hours = list(range(min(all_hours), max(all_hours) + 1))
    else:
        hours = list(range(10, 21))

    days = []
    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    for i in range(7):
        day_date = monday + timedelta(days=i)
        date_str = day_date.isoformat()
        weekday = day_date.weekday()

        wh = work_hours_by_weekday.get(weekday, {})
        is_working_day = bool(wh.get('is_working'))

        work_start_h = None
        work_end_h = None
        if is_working_day:
            work_start_h = _time_to_minutes(wh['start_time']) // 60
            work_end_h = _time_to_minutes(wh['end_time']) // 60

        is_off_day = (not is_working_day) or is_day_off(master['id'], date_str)

        working_hours = set()
        if not is_off_day:
            for h in range(work_start_h, work_end_h):
                working_hours.add(h)

        bookings_by_hour = {}

        for b in all_bookings:
            if b['date'] != date_str:
                continue
            if b['status'] == 'cancelled':
                continue

            try:
                hour = int(b['time'].split(':')[0])
            except Exception:
                continue

            cur.execute("SELECT * FROM leads WHERE id = ?", (b['lead_id'],))
            lead = cur.fetchone()

            if hour not in bookings_by_hour:
                bookings_by_hour[hour] = []

            bookings_by_hour[hour].append({
                'id': b['id'],
                'time': b['time'],
                'duration': b['duration'],
                'status': b['status'],
                'name': lead['name'] if lead else '—',
                'has_notes': bool(b.get('notes')),
                'has_image': bool(b.get('reference_image')),
            })

        days.append({
            'name': weekdays_ru[i],
            'day_num': day_date.strftime('%d.%m'),
            'date': date_str,
            'is_today': day_date == today,
            'is_off_day': is_off_day,
            'working_hours': working_hours,
            'bookings_by_hour': bookings_by_hour,
        })

    conn.close()

    week_label = f"{monday.strftime('%d.%m.%Y')} — {sunday.strftime('%d.%m.%Y')}"

    return _render_template_file(
        'calendar.html',
        days=days,
        hours=hours,
        week_label=week_label,
        week_offset=week_offset,
        active='calendar',
    )


# ============================================
# СТАТИСТИКА
# ============================================

@app.route('/admin/stats')
def admin_stats():
    token = request.cookies.get('admin_session')
    email = get_session(token) if token else None

    if not email:
        return redirect('/admin/login')

    master = get_default_master()
    if not master:
        return "Мастер не найден", 500

    period = request.args.get('period', 'month')
    if period not in ('today', 'week', 'month', 'all'):
        period = 'month'

    stats = get_period_stats(master['id'], period)
    recent = get_recent_bookings(master['id'], limit=5)

    return _render_template_file(
        'stats.html',
        stats=stats,
        recent=recent,
        period=period,
        active='stats',
    )


# ============================================
# НАСТРОЙКИ / СМЕНА ПАРОЛЯ
# ============================================

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    token = request.cookies.get('admin_session')
    email = get_session(token) if token else None

    if not email:
        return redirect('/admin/login')

    master = get_master_by_email(email)
    if not master:
        return "Мастер не найден", 500

    error = None
    info = None

    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        new_password2 = request.form.get('new_password2', '')

        if not check_password_hash(master['password_hash'] or '', old_password):
            error = 'Старый пароль введён неверно'
        elif len(new_password) < 8:
            error = 'Новый пароль должен быть не короче 8 символов'
        elif new_password != new_password2:
            error = 'Пароли не совпадают'
        else:
            password_hash = generate_password_hash(new_password)
            set_master_password(master['id'], password_hash)
            info = '✅ Пароль успешно изменён'

    return _render_template_file(
        'settings.html',
        email=email,
        error=error,
        info=info,
        active='settings',
    )


# ============================================
# СОХРАНЕНИЕ ЯЗЫКА
# ============================================

@app.after_request
def save_lang_cookie(response):
    lang = request.args.get('lang', '').strip().lower()
    if lang in ('ru', 'en', 'he'):
        response.set_cookie('admin_lang', lang, max_age=365 * 24 * 3600)
    return response




# ============================================
# НОВАЯ ЗАПИСЬ (вручную)
# ============================================

import uuid
from werkzeug.utils import secure_filename
from flask import send_from_directory

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin/uploads/<filename>')
def admin_upload(filename):
    """Отдаёт загруженный файл."""
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/admin/bookings/new', methods=['GET', 'POST'])
def admin_new_booking():
    token = request.cookies.get('admin_session')
    email = get_session(token) if token else None

    if not email:
        return redirect('/admin/login')

    master = get_default_master()
    if not master:
        return "Мастер не найден", 500

    services = get_all_services()

    # Prefill из query
    prefill_date = request.args.get('date', '')
    prefill_time = request.args.get('time', '')

    if request.method == 'GET':
        return _render_template_file(
            'new_booking.html',
            services=services,
            error=None,
            prefill_date=prefill_date,
            prefill_time=prefill_time,
            prefill_name='',
            prefill_phone='',
            prefill_service_id=None,
            prefill_notes='',
            today=datetime.now().date().isoformat(),
            active='calendar',
        )

    # POST
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    service_id = request.form.get('service_id', '').strip()
    date_str = request.form.get('date', '').strip()
    time_str = request.form.get('time', '').strip()
    notes = request.form.get('notes', '').strip()
    price = int(request.form.get('price', 0) or 0)
    deposit = int(request.form.get('deposit', 0) or 0)

    error = None

    if not name or not phone or not service_id or not date_str or not time_str:
        error = 'Заполните обязательные поля'

    service = get_service(int(service_id)) if service_id else None
    if not service:
        error = 'Услуга не найдена'

    if not error:
        duration = service['duration_minutes']

        # Проверяем, что слот свободен
        free = get_free_slots_admin(master['id'], date_str, duration)
        if time_str not in free:
            error = 'Этот слот занят. Выберите другое время.'

    if error:
        return _render_template_file(
            'new_booking.html',
            services=services,
            error=error,
            prefill_date=date_str,
            prefill_time=time_str,
            prefill_name=name,
            prefill_phone=phone,
            prefill_service_id=int(service_id) if service_id else None,
            prefill_notes=notes,
            today=datetime.now().date().isoformat(),
            active='calendar',
        ), 400

    # Загрузка файла
    reference_image = ''
    if 'reference_image' in request.files:
        file = request.files['reference_image']
        if file and file.filename and allowed_file(file.filename):
            # Проверяем размер
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)

            if size <= MAX_FILE_SIZE:
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"booking_{uuid.uuid4().hex[:12]}.{ext}"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                reference_image = filename

    # Получаем или создаём клиента
    from core.storage.clients import get_or_create_client
    client_id = get_or_create_client(name, phone)

    # Создаём запись
    booking_id = create_manual_booking(
        master_id=master['id'],
        date_str=date_str,
        time_str=time_str,
        duration=service['duration_minutes'],
        name=name,
        phone=phone,
        service_id=service['id'],
        notes=notes,
        reference_image=reference_image,
        client_id=client_id,
        price=price,
        deposit=deposit,
        source='manual',
    )

    if not booking_id:
        return _render_template_file(
            'new_booking.html',
            services=services,
            error='Не удалось создать запись',
            prefill_date=date_str,
            prefill_time=time_str,
            prefill_name=name,
            prefill_phone=phone,
            prefill_service_id=int(service_id) if service_id else None,
            prefill_notes=notes,
            today=datetime.now().date().isoformat(),
            active='calendar',
        ), 500

    return redirect('/admin/bookings')




# ============================================
# ДЕТАЛИ ЗАПИСИ
# ============================================

@app.route('/admin/bookings/<int:booking_id>')
def admin_booking_detail(booking_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    booking = get_booking(booking_id)
    if not booking:
        return "Запись не найдена", 404

    # Обогащаем датой human
    try:
        dt = datetime.strptime(booking['date'], "%Y-%m-%d").date()
        weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        booking['date_human'] = f"{dt.strftime('%d.%m.%Y')} ({weekdays_ru[dt.weekday()]})"
    except Exception:
        booking['date_human'] = booking['date']

    return _render_template_file(
        'booking_detail.html',
        booking=booking,
        active='bookings',
    )




@app.route('/admin/bookings/delete/<int:booking_id>')
def admin_booking_delete(booking_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    delete_booking(booking_id)
    return redirect('/admin/bookings')




# ============================================
# КЛИЕНТЫ
# ============================================

@app.route('/admin/clients')
def admin_clients():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    search = request.args.get('q', '').strip()
    clients = get_all_clients(search=search)

    return _render_template_file(
        'clients.html',
        clients=clients,
        search=search,
        active='clients',
    )


@app.route('/admin/clients/<int:client_id>')
def admin_client_detail(client_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    client = get_client(client_id)
    if not client:
        return "Клиент не найден", 404

    stats = get_client_stats(client_id)
    bookings = get_client_bookings(client_id)

    return _render_template_file(
        'client_detail.html',
        client=client,
        stats=stats,
        bookings=bookings,
        active='clients',
    )


@app.route('/admin/clients/edit/<int:client_id>', methods=['GET', 'POST'])
def admin_client_edit(client_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    client = get_client(client_id)
    if not client:
        return "Клиент не найден", 404

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        notes = request.form.get('notes', '').strip()

        update_client(
            client_id,
            name=name if name else None,
            phone=phone if phone else None,
            email=email if email else None,
            notes=notes if notes else None,
        )
        return redirect(f'/admin/clients/{client_id}')

    return _render_template_file(
        'client_edit.html',
        client=client,
        active='clients',
    )


# ============================================
# УСЛУГИ
# ============================================

@app.route('/admin/services')
def admin_services():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    services = get_all_services()

    return _render_template_file(
        'services.html',
        services=services,
        active='services',
    )


@app.route('/admin/services/new', methods=['GET', 'POST'])
def admin_service_new():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    error = None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        hours = int(request.form.get('hours', 0) or 0)
        minutes = int(request.form.get('minutes', 0) or 0)
        price_from = int(request.form.get('price_from', 0) or 0)
        buffer_minutes = int(request.form.get('buffer_minutes', 30) or 30)

        duration_minutes = hours * 60 + minutes

        if not name:
            error = 'Введите название услуги'
        elif duration_minutes <= 0:
            error = 'Длительность должна быть больше 0'
        else:
            create_service(name, duration_minutes, price_from, buffer_minutes)
            return redirect('/admin/services')

    return _render_template_file(
        'service_edit.html',
        service=None,
        error=error,
        active='services',
    )


@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
def admin_service_edit(service_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    service = get_service(service_id)
    if not service:
        return "Услуга не найдена", 404

    error = None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        hours = int(request.form.get('hours', 0) or 0)
        minutes = int(request.form.get('minutes', 0) or 0)
        price_from = int(request.form.get('price_from', 0) or 0)
        buffer_minutes = int(request.form.get('buffer_minutes', 30) or 30)

        duration_minutes = hours * 60 + minutes

        if not name:
            error = 'Введите название услуги'
        elif duration_minutes <= 0:
            error = 'Длительность должна быть больше 0'
        else:
            update_service(
                service_id,
                name=name,
                duration_minutes=duration_minutes,
                price_from=price_from,
                buffer_minutes=buffer_minutes,
            )
            return redirect('/admin/services')

    return _render_template_file(
        'service_edit.html',
        service=service,
        error=error,
        active='services',
    )


@app.route('/admin/services/delete/<int:service_id>')
def admin_service_delete(service_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    delete_service(service_id)
    return redirect('/admin/services')




@app.route('/admin/bookings/edit/<int:booking_id>', methods=['POST'])
def admin_booking_edit_price(booking_id):
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return redirect('/admin/login')

    price = int(request.form.get('price', 0) or 0)
    deposit = int(request.form.get('deposit', 0) or 0)

    update_booking_price(booking_id, price=price, deposit=deposit)
    return redirect(f'/admin/bookings/{booking_id}')




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


# ============================================
# API: ОТКРЫТИЕ НЕРАБОЧЕГО СЛОТА
# ============================================

@app.route('/admin/api/slots/open', methods=['POST'])
def admin_api_open_slot():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return jsonify({'success': False, 'error': 'Not authorized'}), 401

    data = request.json
    date_str = data.get('date')
    time_str = data.get('time')

    if not date_str or not time_str:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    master = get_default_master()
    if not master:
        return jsonify({'success': False, 'error': 'Master not found'}), 500

    from core.storage.schedule import add_custom_slot
    add_custom_slot(master['id'], date_str, time_str)

    return jsonify({'success': True})


# ============================================
# API: ПЕРЕМЕЩЕНИЕ ЗАПИСИ (drag & drop)
# ============================================

@app.route('/admin/api/bookings/move', methods=['POST'])
def admin_api_booking_move():
    token = request.cookies.get('admin_session')
    if not get_session(token):
        return jsonify({'success': False, 'error': 'Not authorized'}), 401

    data = request.json
    booking_id = data.get('booking_id')
    new_date = data.get('date')
    new_time = data.get('time')

    if not booking_id or not new_date or not new_time:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    booking = get_booking(booking_id)
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'}), 404

    master = get_default_master()
    duration = booking['duration']

    from core.storage.schedule import get_free_slots_admin
    free = get_free_slots_admin(master['id'], new_date, duration)

    if not (new_date == booking['date'] and new_time == booking['time']):
        if new_time not in free:
            return jsonify({'success': False, 'error': 'Slot is busy'}), 400

    import sqlite3 as _sqlite3
    conn = _sqlite3.connect(os.getenv("SQLITE_PATH", "data/leads.db"))
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET date = ?, time = ? WHERE id = ?",
                (new_date, new_time, booking_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)