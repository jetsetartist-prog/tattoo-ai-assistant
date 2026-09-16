"""
Ядро: обработка входящих сообщений.
Понимает опечатки, транслит и определяет язык (ru/he/en).
"""
import os
import difflib
from loguru import logger
from core.messaging.base import IncomingMessage, MessageAdapter, Button
from core.handlers.booking import start_booking, handle_booking_input, is_in_booking
from core.ai.provider import get_ai_response
from core.i18n.detector import detect_language
from core.i18n.translator import t

ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "").strip() or None

# Карта раскладки: английские клавиши → русские
LAYOUT_MAP = str.maketrans(
    "qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?~",
    "йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё",
)


def translit_to_ru(text: str) -> str:
    """Превращает 'ghbdat' в 'привет'."""
    return text.translate(LAYOUT_MAP)


def normalize_text(text: str) -> str:
    """Нормализует текст."""
    text = text.strip().lower()
    text = text.strip("?!.,;:()[]{}\"'")
    return text


def fuzzy_match(text: str, variants: list, threshold: float = 0.75) -> bool:
    """Проверяет похожесть на команды (опечатки + транслит)."""
    text = normalize_text(text)
    if not text:
        return False

    candidates = {text, translit_to_ru(text)}

    for candidate in candidates:
        for v in variants:
            if v in candidate:
                return True
        for word in candidate.split():
            matches = difflib.get_close_matches(word, variants, n=1, cutoff=threshold)
            if matches:
                return True
    return False


# Словари команд (на трёх языках)
GREETINGS = [
    "привет", "приветствую", "здравствуй", "хай", "прив",
    "hello", "hi", "hey",
    "שלום", "היי",
]
PRICE_WORDS = [
    "прайс", "цена", "цены", "стоимость", "сколько", "стоит",
    "price", "prices", "cost", "how much",
    "מחיר", "מחירים", "כמה",
]
PORTFOLIO_WORDS = [
    "портфолио", "работы", "примеры", "галерея",
    "portfolio", "works", "gallery",
    "תיק עבודות", "עבודות", "גלריה",
]
CONTACTS_WORDS = [
    "контакты", "контакт", "телефон", "адрес", "связаться",
    "contacts", "contact", "phone", "address",
    "יצירת קשר", "טלפון", "כתובת",
]
BOOKING_WORDS = [
    "записаться", "запись", "записаца", "записатся", "хочу записаться",
    "book", "booking", "appointment",
    "לקבוע תור", "תור", "להזמין",
]
MENU_WORDS = [
    "меню", "старт", "начать",
    "menu", "start",
    "תפריט", "התחל",
]


async def handle_incoming(msg: IncomingMessage, adapter: MessageAdapter) -> None:
    """Точка входа ядра."""
    user_key = f"{msg.platform}:{msg.user_id}"
    text = msg.text.strip()
    text_lower = normalize_text(text)

    # Определяем язык
    lang = detect_language(text)

    logger.info(f"[{msg.platform}] user={msg.user_id} lang={lang}: {text[:50]}")

    # 1. Форма записи
    if is_in_booking(user_key):
        await handle_booking_input(
            msg,
            adapter,
            admin_chat_id=ADMIN_USER_ID if ADMIN_USER_ID else None,
            lang=lang,
        )
        return

    # 2. Приветствие / меню
    if fuzzy_match(text_lower, GREETINGS) or fuzzy_match(text_lower, MENU_WORDS):
        await adapter.send_message(
            msg.chat_id,
            t("welcome", lang),
            buttons=[
                Button(t("menu_booking", lang), color="primary"),
                Button(t("menu_price", lang), color="secondary"),
                Button(t("menu_portfolio", lang), color="secondary"),
                Button(t("menu_contacts", lang), color="secondary"),
            ],
        )
        return

    # 3. Прайс
    if fuzzy_match(text_lower, PRICE_WORDS):
        await adapter.send_message(
            msg.chat_id,
            t("price", lang),
        )
        return

    # 4. Портфолио
    if fuzzy_match(text_lower, PORTFOLIO_WORDS):
        await adapter.send_message(
            msg.chat_id,
            t("portfolio", lang),
        )
        return

    # 5. Контакты
    if fuzzy_match(text_lower, CONTACTS_WORDS):
        await adapter.send_message(
            msg.chat_id,
            t("contacts", lang),
        )
        return

    # 6. Записаться
    if fuzzy_match(text_lower, BOOKING_WORDS):
        start_booking(user_key)
        await adapter.send_message(
            msg.chat_id,
            t("booking_start", lang),
        )
        return

    # 7. AI
        # 7. AI — только для ru/en (GigaChat не знает иврит)
    if lang in ('ru', 'en'):
        try:
            ai_response = get_ai_response(text, user_key, lang=lang)
            if ai_response:
                await adapter.send_message(msg.chat_id, ai_response)
                return
        except Exception as e:
            logger.error(f"[AI] Ошибка: {e}")
    else:
        logger.info(f"[AI] Пропущен для языка '{lang}' (используем заготовки)")

    # 8. Fallback — заготовка
    await adapter.send_message(
        msg.chat_id,
        t("not_understood", lang),
    )

    # 8. Fallback
    await adapter.send_message(
        msg.chat_id,
        t("not_understood", lang),
    )