"""
Обновляет JSON-файлы переводов: добавляет ключи для кабинета.
Существующие ключи сохраняются.
Запуск: python update_i18n_json.py
"""
import json
from pathlib import Path

BASE = Path(__file__).parent
I18N_DIR = BASE / "core" / "i18n"

# Новые ключи для каждого языка
NEW_RU = {
    "admin_title": "Кабинет мастера",
    "admin_nav_home": "Главная",
    "admin_nav_schedule": "Расписание",
    "admin_nav_bookings": "Записи",
    "admin_nav_calendar": "Календарь",
    "admin_nav_settings": "Настройки",
    "admin_nav_logout": "Выйти",
    "admin_welcome_title": "Добро пожаловать!",
    "admin_welcome_text": "Вы вошли как {email}",
    "admin_card_bookings_title": "📋 Записи клиентов",
    "admin_card_bookings_text": "Список всех записей, подтверждение и отмена.",
    "admin_card_bookings_btn": "Открыть записи →",
    "admin_card_schedule_title": "📅 Расписание",
    "admin_card_schedule_text": "Настройте свои рабочие часы по дням недели, добавьте выходные.",
    "admin_card_schedule_btn": "Настроить расписание →",
    "admin_card_settings_title": "🔐 Настройки",
    "admin_card_settings_text": "Смена пароля, данные аккаунта.",
    "admin_card_settings_btn": "Открыть настройки →",
    "admin_card_dev_title": "🚧 В разработке",
    "admin_card_dev_text": "Скоро добавим:",
    "admin_card_dev_stat": "📊 Статистика и выручка",
    "admin_card_dev_cal": "🗓 Календарь с записями",
    "admin_card_dev_wa": "💬 Интеграция с WhatsApp и Instagram",

    "schedule_title": "📅 Рабочие часы",
    "schedule_subtitle": "Укажите, в какие дни вы работаете и во сколько начинаете и заканчиваете.",
    "schedule_saved": "✅ Расписание сохранено",
    "schedule_working": "Работаю",
    "schedule_save": "💾 Сохранить",
    "schedule_back": "← Назад",
    "schedule_day_0": "Понедельник",
    "schedule_day_1": "Вторник",
    "schedule_day_2": "Среда",
    "schedule_day_3": "Четверг",
    "schedule_day_4": "Пятница",
    "schedule_day_5": "Суббота",
    "schedule_day_6": "Воскресенье",

    "bookings_title": "📋 Записи клиентов",
    "bookings_total": "Всего: {count}",
    "bookings_filter_all": "Все",
    "bookings_filter_upcoming": "Предстоящие",
    "bookings_filter_pending": "Ожидают",
    "bookings_filter_past": "Прошедшие",
    "bookings_th_date": "Дата",
    "bookings_th_time": "Время",
    "bookings_th_client": "Клиент",
    "bookings_th_phone": "Телефон",
    "bookings_th_size": "Размер",
    "bookings_th_status": "Статус",
    "bookings_th_actions": "Действия",
    "bookings_status_pending": "Ожидает",
    "bookings_status_confirmed": "Подтверждено",
    "bookings_status_cancelled": "Отменено",
    "bookings_btn_confirm": "✓ Подтвердить",
    "bookings_btn_cancel": "✕ Отменить",
    "bookings_empty": "📭 Записей пока нет",

    "calendar_title": "📅 Календарь",
    "calendar_prev": "← Прошлая",
    "calendar_today": "Текущая",
    "calendar_next": "Следующая →",
    "calendar_legend_confirmed": "Подтверждено",
    "calendar_legend_pending": "Ожидает",
    "calendar_legend_cancelled": "Отменено",

    "settings_title": "🔐 Смена пароля",
    "settings_subtitle": "Вы вошли как {email}",
    "settings_old_password": "Старый пароль",
    "settings_new_password": "Новый пароль (минимум 8 символов)",
    "settings_new_password2": "Повторите новый пароль",
    "settings_save": "💾 Сохранить",
    "settings_back": "← Назад",
    "settings_success": "✅ Пароль успешно изменён",
    "settings_error_old": "Старый пароль введён неверно",
    "settings_error_length": "Новый пароль должен быть не короче 8 символов",
    "settings_error_match": "Пароли не совпадают",
}

NEW_EN = {
    "admin_title": "Master's Cabinet",
    "admin_nav_home": "Home",
    "admin_nav_schedule": "Schedule",
    "admin_nav_bookings": "Bookings",
    "admin_nav_calendar": "Calendar",
    "admin_nav_settings": "Settings",
    "admin_nav_logout": "Logout",
    "admin_welcome_title": "Welcome!",
    "admin_welcome_text": "You are logged in as {email}",
    "admin_card_bookings_title": "📋 Client Bookings",
    "admin_card_bookings_text": "All bookings, confirm and cancel.",
    "admin_card_bookings_btn": "Open bookings →",
    "admin_card_schedule_title": "📅 Schedule",
    "admin_card_schedule_text": "Set your working hours by days of the week, add days off.",
    "admin_card_schedule_btn": "Set schedule →",
    "admin_card_settings_title": "🔐 Settings",
    "admin_card_settings_text": "Change password, account info.",
    "admin_card_settings_btn": "Open settings →",
    "admin_card_dev_title": "🚧 In development",
    "admin_card_dev_text": "Coming soon:",
    "admin_card_dev_stat": "📊 Statistics and revenue",
    "admin_card_dev_cal": "🗓 Calendar with bookings",
    "admin_card_dev_wa": "💬 WhatsApp and Instagram integration",

    "schedule_title": "📅 Working hours",
    "schedule_subtitle": "Specify which days you work and your start/end times.",
    "schedule_saved": "✅ Schedule saved",
    "schedule_working": "Working",
    "schedule_save": "💾 Save",
    "schedule_back": "← Back",
    "schedule_day_0": "Monday",
    "schedule_day_1": "Tuesday",
    "schedule_day_2": "Wednesday",
    "schedule_day_3": "Thursday",
    "schedule_day_4": "Friday",
    "schedule_day_5": "Saturday",
    "schedule_day_6": "Sunday",

    "bookings_title": "📋 Client Bookings",
    "bookings_total": "Total: {count}",
    "bookings_filter_all": "All",
    "bookings_filter_upcoming": "Upcoming",
    "bookings_filter_pending": "Pending",
    "bookings_filter_past": "Past",
    "bookings_th_date": "Date",
    "bookings_th_time": "Time",
    "bookings_th_client": "Client",
    "bookings_th_phone": "Phone",
    "bookings_th_size": "Size",
    "bookings_th_status": "Status",
    "bookings_th_actions": "Actions",
    "bookings_status_pending": "Pending",
    "bookings_status_confirmed": "Confirmed",
    "bookings_status_cancelled": "Cancelled",
    "bookings_btn_confirm": "✓ Confirm",
    "bookings_btn_cancel": "✕ Cancel",
    "bookings_empty": "📭 No bookings yet",

    "calendar_title": "📅 Calendar",
    "calendar_prev": "← Previous",
    "calendar_today": "Current",
    "calendar_next": "Next →",
    "calendar_legend_confirmed": "Confirmed",
    "calendar_legend_pending": "Pending",
    "calendar_legend_cancelled": "Cancelled",

    "settings_title": "🔐 Change password",
    "settings_subtitle": "You are logged in as {email}",
    "settings_old_password": "Old password",
    "settings_new_password": "New password (min 8 chars)",
    "settings_new_password2": "Repeat new password",
    "settings_save": "💾 Save",
    "settings_back": "← Back",
    "settings_success": "✅ Password changed successfully",
    "settings_error_old": "Old password is incorrect",
    "settings_error_length": "New password must be at least 8 characters",
    "settings_error_match": "Passwords don't match",
}

NEW_HE = {
    "admin_title": "הקבינט של המאסטר",
    "admin_nav_home": "בית",
    "admin_nav_schedule": "לוח זמנים",
    "admin_nav_bookings": "הזמנות",
    "admin_nav_calendar": "לוח שנה",
    "admin_nav_settings": "הגדרות",
    "admin_nav_logout": "יציאה",
    "admin_welcome_title": "ברוך הבא!",
    "admin_welcome_text": "אתה מחובר בתור {email}",
    "admin_card_bookings_title": "📋 הזמנות לקוחות",
    "admin_card_bookings_text": "כל ההזמנות, אישור וביטול.",
    "admin_card_bookings_btn": "פתח הזמנות →",
    "admin_card_schedule_title": "📅 לוח זמנים",
    "admin_card_schedule_text": "הגדר את שעות העבודה שלך לפי ימי השבוע.",
    "admin_card_schedule_btn": "הגדר לוח זמנים →",
    "admin_card_settings_title": "🔐 הגדרות",
    "admin_card_settings_text": "שינוי סיסמה, פרטי חשבון.",
    "admin_card_settings_btn": "פתח הגדרות →",
    "admin_card_dev_title": "🚧 בפיתוח",
    "admin_card_dev_text": "בקרוב:",
    "admin_card_dev_stat": "📊 סטטיסטיקה והכנסות",
    "admin_card_dev_cal": "🗓 לוח שנה עם הזמנות",
    "admin_card_dev_wa": "💬 אינטגרציה עם WhatsApp ו-Instagram",

    "schedule_title": "📅 שעות עבודה",
    "schedule_subtitle": "ציין באילו ימים אתה עובד ושעות התחלה/סיום.",
    "schedule_saved": "✅ לוח הזמנים נשמר",
    "schedule_working": "עובד",
    "schedule_save": "💾 שמור",
    "schedule_back": "← חזור",
    "schedule_day_0": "שני",
    "schedule_day_1": "שלישי",
    "schedule_day_2": "רביעי",
    "schedule_day_3": "חמישי",
    "schedule_day_4": "שישי",
    "schedule_day_5": "שבת",
    "schedule_day_6": "ראשון",

    "bookings_title": "📋 הזמנות לקוחות",
    "bookings_total": "סה\"כ: {count}",
    "bookings_filter_all": "הכל",
    "bookings_filter_upcoming": "עתידיות",
    "bookings_filter_pending": "ממתינות",
    "bookings_filter_past": "עברו",
    "bookings_th_date": "תאריך",
    "bookings_th_time": "שעה",
    "bookings_th_client": "לקוח",
    "bookings_th_phone": "טלפון",
    "bookings_th_size": "גודל",
    "bookings_th_status": "סטטוס",
    "bookings_th_actions": "פעולות",
    "bookings_status_pending": "ממתין",
    "bookings_status_confirmed": "מאושר",
    "bookings_status_cancelled": "מבוטל",
    "bookings_btn_confirm": "✓ אשר",
    "bookings_btn_cancel": "✕ בטל",
    "bookings_empty": "📭 אין הזמנות עדיין",

    "calendar_title": "📅 לוח שנה",
    "calendar_prev": "← הקודם",
    "calendar_today": "נוכחי",
    "calendar_next": "הבא →",
    "calendar_legend_confirmed": "מאושר",
    "calendar_legend_pending": "ממתין",
    "calendar_legend_cancelled": "מבוטל",

    "settings_title": "🔐 שינוי סיסמה",
    "settings_subtitle": "אתה מחובר בתור {email}",
    "settings_old_password": "סיסמה ישנה",
    "settings_new_password": "סיסמה חדשה (לפחות 8 תווים)",
    "settings_new_password2": "חזור על הסיסמה החדשה",
    "settings_save": "💾 שמור",
    "settings_back": "← חזור",
    "settings_success": "✅ הסיסמה שונתה בהצלחה",
    "settings_error_old": "הסיסמה הישנה שגויה",
    "settings_error_length": "הסיסמה החדשה חייבת להיות לפחות 8 תווים",
    "settings_error_match": "הסיסמאות לא תואמות",
}


def update_json(lang: str, new_keys: dict):
    """Добавляет новые ключи в JSON, не удаляя существующие."""
    path = I18N_DIR / f"{lang}.json"

    if path.exists():
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    before = len(data)
    data.update(new_keys)  # Обновляем/добавляем
    after = len(data)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ {lang}.json: {before} → {after} ключей")


def main():
    print("=" * 60)
    print("🚀 Обновление JSON-файлов переводов")
    print("=" * 60)
    print()

    update_json('ru', NEW_RU)
    update_json('en', NEW_EN)
    update_json('he', NEW_HE)

    print()
    print("=" * 60)
    print("✅ Готово!")
    print("=" * 60)
    print()
    print("Проверьте:")
    print('  python -c "from core.i18n.translator import reload_translations, t; reload_translations(); print(t(\'admin_nav_home\', \'ru\'))"')
    print()


if __name__ == '__main__':
    main()