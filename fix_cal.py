"""Fix: заменяет calendar.html на версию с нерабочими часами."""
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
CALENDAR = BASE / "templates" / "calendar.html"

HTML = '''<!DOCTYPE html>
<html lang="{{ admin_lang }}" {% if admin_lang == 'he' %}dir="rtl"{% endif %}>
<head>
    <meta charset="UTF-8">
    <title>{{ t('calendar_title', admin_lang) }}</title>
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
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .nav-week { display: flex; justify-content: space-between; align-items: center; background: white; padding: 16px 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .nav-week h2 { color: #075e54; font-size: 18px; }
        .nav-week .links a { display: inline-block; padding: 8px 16px; background: #f0f0f0; color: #333; text-decoration: none; border-radius: 8px; font-size: 14px; margin-left: 8px; }
        .nav-week .links a.today { background: #25d366; color: white; }
        .nav-week .links a.new-booking { background: #075e54; color: white; }
        .calendar { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .cal-header { display: grid; grid-template-columns: 80px repeat(7, 1fr); background: #f9f9f9; border-bottom: 2px solid #eee; }
        .cal-header > div { padding: 14px 8px; text-align: center; font-size: 13px; font-weight: 600; color: #666; border-right: 1px solid #eee; }
        .cal-header > div:last-child { border-right: none; }
        .cal-header .today { background: #e8f5e9; color: #075e54; }
        .cal-header .day-off { background: #fce4ec; color: #c62828; }
        .cal-body { display: grid; grid-template-columns: 80px repeat(7, 1fr); }
        .time-slot { padding: 8px; font-size: 11px; color: #999; text-align: right; border-right: 1px solid #eee; border-bottom: 1px solid #f5f5f5; height: 60px; }
        .day-slot { border-right: 1px solid #eee; border-bottom: 1px solid #f5f5f5; height: 60px; position: relative; padding: 2px; cursor: pointer; transition: background 0.15s; }
        .day-slot:hover { background: #f0f8f5; }
        .day-slot:last-child { border-right: none; }
        .day-slot.drag-over { background: #c8e6c9; border: 2px dashed #25d366; }
        .day-slot.off { background: repeating-linear-gradient(45deg, #fce4ec, #fce4ec 6px, #fff0f3 6px, #fff0f3 12px); cursor: not-allowed; }
        .day-slot.off:hover { background: repeating-linear-gradient(45deg, #f8bbd0, #f8bbd0 6px, #fce4ec 6px, #fce4ec 12px); }
        .booking { background: linear-gradient(135deg, #25d366 0%, #1ebe5d 100%); color: white; padding: 4px 6px; border-radius: 6px; font-size: 11px; line-height: 1.3; cursor: grab; overflow: hidden; height: 100%; display: flex; flex-direction: column; justify-content: center; position: relative; user-select: none; }
        .booking:active { cursor: grabbing; }
        .booking.dragging { opacity: 0.4; }
        .booking.pending { background: linear-gradient(135deg, #ffb74d 0%, #ff9800 100%); }
        .booking.cancelled { background: #ccc; text-decoration: line-through; opacity: 0.6; }
        .booking .b-name { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .booking .b-time { font-size: 10px; opacity: 0.9; }
        .booking .b-icons { font-size: 10px; position: absolute; top: 3px; right: 4px; }
        .legend { display: flex; gap: 20px; margin-top: 16px; font-size: 13px; color: #666; flex-wrap: wrap; }
        .legend-item { display: flex; align-items: center; gap: 6px; }
        .legend-color { width: 16px; height: 16px; border-radius: 4px; }
        .legend-color.off { background: repeating-linear-gradient(45deg, #fce4ec, #fce4ec 4px, #fff0f3 4px, #fff0f3 8px); border: 1px solid #f8bbd0; }
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999; align-items: center; justify-content: center; }
        .modal-content { background: white; border-radius: 12px; padding: 30px; max-width: 400px; margin: 20px; }
        .modal-content h3 { color: #075e54; margin-bottom: 16px; }
        .modal-content p { color: #666; margin-bottom: 24px; font-size: 14px; }
        .modal-actions { display: flex; gap: 12px; }
        .modal-btn { flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
        .modal-btn-primary { background: #25d366; color: white; }
        .modal-btn-secondary { background: #f0f0f0; color: #333; }
    </style>
</head>
<body>
    {% include '_nav.html' %}
    <div class="container">
        <div class="nav-week">
            <h2>{{ week_label }}</h2>
            <div class="links">
                <a href="/admin/calendar?week_offset={{ week_offset - 1 }}">← {{ t('calendar_prev', admin_lang) }}</a>
                <a href="/admin/calendar?week_offset=0" class="today">{{ t('calendar_today', admin_lang) }}</a>
                <a href="/admin/calendar?week_offset={{ week_offset + 1 }}">{{ t('calendar_next', admin_lang) }} →</a>
                <a href="/admin/bookings/new" class="new-booking">➕ {{ t('new_booking_btn', admin_lang) }}</a>
            </div>
        </div>
        <div class="calendar">
            <div class="cal-header">
                <div></div>
                {% for day in days %}
                <div class="{% if day.is_today %}today{% elif day.is_off_day %}day-off{% endif %}">
                    {{ day.name }}<br><small>{{ day.day_num }}</small>
                </div>
                {% endfor %}
            </div>
            <div class="cal-body">
                {% for hour in hours %}
                <div class="time-slot">{{ hour }}:00</div>
                    {% for day in days %}
                    {% set slot_bookings = day.bookings_by_hour.get(hour, []) %}
                    {% set is_off_slot = day.is_off_day or (hour not in day.working_hours) %}
                    {% if slot_bookings %}
                    <div class="day-slot" data-date="{{ day.date }}" data-time="{{ '%02d' % hour }}:00">
                        {% for b in slot_bookings %}
                        <div class="booking {% if b.status == 'pending' %}pending{% elif b.status == 'cancelled' %}cancelled{% endif %}"
                             draggable="true" data-booking-id="{{ b.id }}"
                             onclick="event.stopPropagation(); window.location='/admin/bookings/{{ b.id }}'">
                            <div class="b-name">{{ b.name }}</div>
                            <div class="b-time">{{ b.time }} · {{ b.duration // 60 }}ч</div>
                            {% if b.has_notes or b.has_image %}<div class="b-icons">{% if b.has_notes %}💬{% endif %}{% if b.has_image %}📎{% endif %}</div>{% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    {% elif is_off_slot %}
                    <div class="day-slot off" title="{{ t('calendar_day_off', admin_lang) }}" onclick="openOffSlot('{{ day.date }}', '{{ '%02d' % hour }}:00')"></div>
                    {% else %}
                    <div class="day-slot" data-date="{{ day.date }}" data-time="{{ '%02d' % hour }}:00" onclick="window.location='/admin/bookings/new?date={{ day.date }}&time={{ '%02d' % hour }}:00'"></div>
                    {% endif %}
                    {% endfor %}
                {% endfor %}
            </div>
        </div>
        <div class="legend">
            <div class="legend-item"><div class="legend-color" style="background: #25d366;"></div><span>{{ t('calendar_legend_confirmed', admin_lang) }}</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #ff9800;"></div><span>{{ t('calendar_legend_pending', admin_lang) }}</span></div>
            <div class="legend-item"><div class="legend-color off"></div><span>{{ t('calendar_day_off', admin_lang) }}</span></div>
        </div>
    </div>
    <div class="modal-overlay" id="off_slot_modal">
        <div class="modal-content">
            <h3>⚠️ {{ t('off_slot_title', admin_lang) }}</h3>
            <p>{{ t('off_slot_question', admin_lang) }}</p>
            <div class="modal-actions">
                <button onclick="confirmOpenSlot()" class="modal-btn modal-btn-primary">{{ t('off_slot_yes', admin_lang) }}</button>
                <button onclick="closeOffSlotModal()" class="modal-btn modal-btn-secondary">{{ t('off_slot_no', admin_lang) }}</button>
            </div>
        </div>
    </div>
    <script>
        let draggedBooking = null;
        document.querySelectorAll('.booking[draggable="true"]').forEach(el => {
            el.addEventListener('dragstart', function(e) {
                draggedBooking = { id: this.dataset.bookingId, element: this };
                this.classList.add('dragging');
            });
            el.addEventListener('dragend', function(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('.day-slot').forEach(s => s.classList.remove('drag-over'));
            });
        });
        let pendingSlot = null;
        function openOffSlot(date, time) {
            pendingSlot = { date: date, time: time };
            document.getElementById('off_slot_modal').style.display = 'flex';
        }
        function closeOffSlotModal() {
            pendingSlot = null;
            document.getElementById('off_slot_modal').style.display = 'none';
        }
        function confirmOpenSlot() {
            if (!pendingSlot) return;
            fetch('/admin/api/slots/open', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(pendingSlot)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const slot = pendingSlot;
                    closeOffSlotModal();
                    window.location.href = '/admin/bookings/new?date=' + slot.date + '&time=' + slot.time;
                } else {
                    alert('Ошибка: ' + (data.error || 'не удалось'));
                }
            })
            .catch(() => alert('Ошибка соединения'));
            pendingSlot = null;
        }
    </script>
</body>
</html>
'''


def main():
    print("🔧 Замена calendar.html")
    if CALENDAR.exists():
        backup = BASE / f"backup_cal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup.mkdir(exist_ok=True)
        shutil.copy(CALENDAR, backup / "calendar.html")
        print(f"📦 Бэкап: {backup.name}")

    CALENDAR.write_text(HTML, encoding='utf-8')
    print("✅ calendar.html заменён")
    print()
    print("Проверьте:")
    print('  python -c "c = open(\'templates/calendar.html\', encoding=\'utf-8\').read(); print(\'is_off_day:\', \'is_off_day\' in c); print(\'day-slot off:\', \'day-slot off\' in c)"')


if __name__ == '__main__':
    main()