"""
Локальный веб-эмулятор мессенджера + кабинет мастера.
Запуск: python web_demo.py
Открыть: http://localhost:5000
Кабинет: http://localhost:5000/admin
Расписание: http://localhost:5000/admin/schedule
Записи: http://localhost:5000/admin/bookings
Календарь: http://localhost:5000/admin/calendar
Настройки: http://localhost:5000/admin/settings
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
    get_master, get_bookings, cancel_booking, confirm_booking,
)
from core.i18n.translator import t

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
    if 't' not in kwargs:
        kwargs['t'] = t

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

    hours = list(range(10, 21))

    days = []
    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    for i in range(7):
        day_date = monday + timedelta(days=i)
        date_str = day_date.isoformat()

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
            })

        days.append({
            'name': weekdays_ru[i],
            'day_num': day_date.strftime('%d.%m'),
            'date': date_str,
            'is_today': day_date == today,
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


@app.after_request
def save_lang_cookie(response):
    lang = request.args.get('lang', '').strip().lower()
    if lang in ('ru', 'en', 'he'):
        response.set_cookie('admin_lang', lang, max_age=365 * 24 * 3600)
    return response


if __name__ == '__main__':
    app.run(debug=True, port=5000)