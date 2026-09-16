"""
Форма записи. Пошаговый сбор данных:
имя → телефон → размер → дата → время → бронирование.
Хранит состояние в памяти.
"""
from datetime import datetime
from loguru import logger
from core.messaging.base import IncomingMessage, MessageAdapter, Button
from core.storage.leads import save_lead
from core.storage.schedule import (
    get_default_master,
    get_all_services,
    get_free_dates,
    get_free_slots,
    book_slot,
)

# Состояния пользователей: {user_key: {"step": ..., "data": {...}}}
_booking_states: dict = {}


def is_in_booking(user_key: str) -> bool:
    return user_key in _booking_states


def start_booking(user_key: str) -> None:
    _booking_states[user_key] = {"step": "name", "data": {}}


def cancel_booking_state(user_key: str) -> None:
    """Отменяет заполнение формы."""
    _booking_states.pop(user_key, None)


async def handle_booking_input(
    msg: IncomingMessage,
    adapter: MessageAdapter,
    admin_chat_id: str = None,
) -> None:
    """Обработка одного шага формы."""
    user_key = f"{msg.platform}:{msg.user_id}"
    state = _booking_states[user_key]
    step = state["step"]
    text = msg.text.strip()

    # ----- ШАГ 1: ИМЯ -----
    if step == "name":
        state["data"]["name"] = text
        state["step"] = "phone"
        await adapter.send_message(
            msg.chat_id,
            f"📱 Приятно познакомиться, {text}!\n\nНапиши свой номер телефона:",
        )
        return

    # ----- ШАГ 2: ТЕЛЕФОН -----
    if step == "phone":
        state["data"]["phone"] = text
        state["step"] = "size"

        services = get_all_services()
        if not services:
            await adapter.send_message(
                msg.chat_id,
                "⚠️ Услуги не настроены. Обратитесь к администратору.",
            )
            cancel_booking_state(user_key)
            return

        # Показываем услуги кнопками
        buttons = []
        for s in services:
            hours = s["duration_minutes"] // 60
            buttons.append(Button(
                f"{s['name']} — {hours}ч",
                color="secondary",
            ))

        await adapter.send_message(
            msg.chat_id,
            "📏 Какой размер татуировки тебя интересует?",
            buttons=buttons,
        )
        return

    # ----- ШАГ 3: РАЗМЕР (выбор из услуг) -----
    if step == "size":
        services = get_all_services()
        # Ищем услугу по названию (частичное совпадение)
        chosen = None
        for s in services:
            if s["name"].lower() in text.lower() or text.lower() in s["name"].lower():
                chosen = s
                break

        if not chosen:
            # Попробуем найти по ключевым словам
            text_lower = text.lower()
            if "мал" in text_lower:
                chosen = next((s for s in services if "мал" in s["name"].lower()), None)
            elif "сред" in text_lower:
                chosen = next((s for s in services if "сред" in s["name"].lower()), None)
            elif "боль" in text_lower:
                chosen = next((s for s in services if "боль" in s["name"].lower()), None)

        if not chosen:
            buttons = []
            for s in services:
                hours = s["duration_minutes"] // 60
                buttons.append(Button(f"{s['name']} — {hours}ч", color="secondary"))
            await adapter.send_message(
                msg.chat_id,
                "🤔 Не понял размер. Выбери, пожалуйста, из вариантов:",
                buttons=buttons,
            )
            return

        state["data"]["service_id"] = chosen["id"]
        state["data"]["service_name"] = chosen["name"]
        state["data"]["duration"] = chosen["duration_minutes"]
        state["step"] = "date"

        # Получаем свободные даты
        master = get_default_master()
        if not master:
            await adapter.send_message(msg.chat_id, "⚠️ Мастер не найден.")
            cancel_booking_state(user_key)
            return

        free_dates = get_free_dates(
            master["id"],
            service_duration=chosen["duration_minutes"],
            days_ahead=14,
        )

        if not free_dates:
            await adapter.send_message(
                msg.chat_id,
                "😔 К сожалению, свободных дат нет. Попробуйте позже.",
            )
            cancel_booking_state(user_key)
            return

        # Показываем до 6 дат кнопками
        buttons = []
        for d in free_dates[:6]:
            buttons.append(Button(d["human"], color="secondary"))

        await adapter.send_message(
            msg.chat_id,
            f"📅 {chosen['name']} — {chosen['duration_minutes'] // 60}ч.\n\n"
            f"Выбери удобную дату:",
            buttons=buttons,
        )
        return

    # ----- ШАГ 4: ДАТА (выбор из кнопок) -----
    if step == "date":
        master = get_default_master()
        duration = state["data"]["duration"]

        free_dates = get_free_dates(
            master["id"],
            service_duration=duration,
            days_ahead=14,
        )

        # Ищем выбранную дату
        chosen_date = None
        for d in free_dates:
            if d["human"] == text or d["date"] == text:
                chosen_date = d
                break

        if not chosen_date:
            # Попробуем найти по частичному совпадению
            for d in free_dates:
                if d["human"].startswith(text) or text in d["human"]:
                    chosen_date = d
                    break

        if not chosen_date:
            buttons = []
            for d in free_dates[:6]:
                buttons.append(Button(d["human"], color="secondary"))
            await adapter.send_message(
                msg.chat_id,
                "🤔 Не понял дату. Выбери из вариантов:",
                buttons=buttons,
            )
            return

        state["data"]["date"] = chosen_date["date"]
        state["data"]["date_human"] = chosen_date["human"]
        state["step"] = "time"

        # Получаем свободные слоты на эту дату
        free_slots = get_free_slots(master["id"], chosen_date["date"], duration)

        if not free_slots:
            state["step"] = "date"
            await adapter.send_message(
                msg.chat_id,
                "😔 На эту дату слотов нет. Выбери другую:",
                buttons=[Button(d["human"], color="secondary") for d in free_dates[:6]],
            )
            return

        # Показываем слоты (до 12 кнопок — по 3 в ряд)
        buttons = []
        for slot in free_slots[:12]:
            buttons.append(Button(slot, color="secondary"))

        await adapter.send_message(
            msg.chat_id,
            f"🕐 {chosen_date['human']}\n\nВыбери удобное время:",
            buttons=buttons,
        )
        return

    # ----- ШАГ 5: ВРЕМЯ + БРОНИРОВАНИЕ -----
    if step == "time":
        master = get_default_master()
        duration = state["data"]["duration"]
        chosen_date = state["data"]["date"]

        free_slots = get_free_slots(master["id"], chosen_date, duration)

        # Ищем выбранное время
        chosen_time = None
        for slot in free_slots:
            if slot == text or slot in text:
                chosen_time = slot
                break

        if not chosen_time:
            buttons = [Button(slot, color="secondary") for slot in free_slots[:12]]
            await adapter.send_message(
                msg.chat_id,
                "🤔 Не понял время. Выбери из вариантов:",
                buttons=buttons,
            )
            return

        # СОХРАНЯЕМ ЛИД
        data = state["data"]
        lead_id = save_lead(
            platform=msg.platform,
            user_id=msg.user_id,
            name=data["name"],
            phone=data["phone"],
            style="",  # стиль спросит AI или мастер
            size=data["service_name"],
            date_preference=f"{data['date_human']} {chosen_time}",
        )

        # БРОНИРУЕМ СЛОТ
        booking_id = book_slot(
            master_id=master["id"],
            date_str=chosen_date,
            time_str=chosen_time,
            duration=duration,
            lead_id=lead_id,
            service_id=data["service_id"],
        )

        if not booking_id:
            await adapter.send_message(
                msg.chat_id,
                "⚠️ Не удалось забронировать. Попробуйте выбрать другое время.",
            )
            state["step"] = "time"
            return

        # Уведомляем админа
        if admin_chat_id:
            admin_msg = (
                f"🔔 Новая запись!\n\n"
                f"Платформа: {msg.platform}\n"
                f"Имя: {data['name']}\n"
                f"Телефон: {data['phone']}\n"
                f"Размер: {data['service_name']} ({duration // 60}ч)\n"
                f"Дата: {data['date_human']}\n"
                f"Время: {chosen_time}"
            )
            try:
                await adapter.send_message(admin_chat_id, admin_msg)
            except Exception as e:
                logger.error(f"[Booking] Не удалось уведомить админа: {e}")

        # Завершаем
        cancel_booking_state(user_key)

        await adapter.send_message(
            msg.chat_id,
            f"✅ {data['name']}, ты записан!\n\n"
            f"📅 {data['date_human']}\n"
            f"🕐 {chosen_time}\n"
            f"⏱ {data['service_name']} ({duration // 60}ч)\n\n"
            f"Мы свяжемся с тобой для подтверждения.",
            buttons=[
                Button("Прайс", color="secondary"),
                Button("Портфолио", color="secondary"),
            ],
        )
        return