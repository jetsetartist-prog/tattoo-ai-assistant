"""Fix: переводы off_slot_* в JSON."""
import json
from pathlib import Path

BASE = Path(__file__).parent
I18N = BASE / "core" / "i18n"

NEW = {
    "ru": {
        "off_slot_title": "Нерабочее время",
        "off_slot_question": "Это нерабочее время. Открыть слот для записи клиента?",
        "off_slot_yes": "Открыть и записать",
        "off_slot_no": "Отмена",
        "calendar_day_off": "Нерабочее время",
        "calendar_cant_move_off": "Нельзя переместить в нерабочее время",
        "calendar_drag_hint": "Перетащите запись в другой слот",
        "calendar_moved": "Запись перемещена",
        "calendar_slot_busy": "Слот занят",
    },
    "en": {
        "off_slot_title": "Non-working hours",
        "off_slot_question": "This is a non-working time slot. Open it for booking?",
        "off_slot_yes": "Open and book",
        "off_slot_no": "Cancel",
        "calendar_day_off": "Day off",
        "calendar_cant_move_off": "Cannot move to non-working hours",
        "calendar_drag_hint": "Drag a booking to change its time",
        "calendar_moved": "Booking moved",
        "calendar_slot_busy": "Slot is busy",
    },
    "he": {
        "off_slot_title": "שעות לא עובדות",
        "off_slot_question": "זו שעה לא עובדת. לפתוח להזמנה?",
        "off_slot_yes": "פתח והזמן",
        "off_slot_no": "ביטול",
        "calendar_day_off": "יום חופש",
        "calendar_cant_move_off": "לא ניתן להעביר",
        "calendar_drag_hint": "גרור הזמנה לשינוי זמן",
        "calendar_moved": "ההזמנה הועברה",
        "calendar_slot_busy": "המשבצת תפוסה",
    },
}


def main():
    print("🔧 Переводы off_slot_*")
    for lang, data in NEW.items():
        path = I18N / f"{lang}.json"
        if not path.exists():
            print(f"  ⚠️  Нет {lang}.json")
            continue
        with open(path, encoding='utf-8') as f:
            existing = json.load(f)
        before = len(existing)
        existing.update(data)
        after = len(existing)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {lang}.json: {before} → {after}")


if __name__ == '__main__':
    main()