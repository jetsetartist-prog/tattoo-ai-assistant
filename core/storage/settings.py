"""
Настройки приложения: валюта.
Валюта по умолчанию зависит от языка:
- ru → RUB
- he → ILS
- en → USD
"""
import os
import sqlite3
from typing import Optional
from loguru import logger

SQLITE_PATH = os.getenv("SQLITE_PATH", "data/leads.db")

CURRENCIES = {
    'RUB': {'symbol': '₽', 'name': 'Рубль', 'name_en': 'Ruble', 'name_he': 'רובל'},
    'ILS': {'symbol': '₪', 'name': 'Шекель', 'name_en': 'Shekel', 'name_he': 'שקל'},
    'USD': {'symbol': '$', 'name': 'Доллар', 'name_en': 'Dollar', 'name_he': 'דולר'},
    'EUR': {'symbol': '€', 'name': 'Евро', 'name_en': 'Euro', 'name_he': 'אירו'},
    'GBP': {'symbol': '£', 'name': 'Фунт', 'name_en': 'Pound', 'name_he': 'לירה'},
    'THB': {'symbol': '฿', 'name': 'Бат', 'name_en': 'Baht', 'name_he': 'באט'},
    'PHP': {'symbol': '₱', 'name': 'Песо', 'name_en': 'Peso', 'name_he': 'פסו'},
}

LANG_TO_CURRENCY = {
    'ru': 'RUB',
    'he': 'ILS',
    'en': 'USD',
}

DEFAULT_CURRENCY = 'RUB'


def get_setting(key: str, default: str = None) -> Optional[str]:
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(key: str, value: str):
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()
    logger.info(f"[Settings] {key} = {value}")


def get_currency_for_lang(lang: str) -> str:
    return LANG_TO_CURRENCY.get(lang, DEFAULT_CURRENCY)


def get_currency() -> str:
    return get_setting('currency', DEFAULT_CURRENCY)


def set_currency(code: str, manual: bool = True):
    if code not in CURRENCIES:
        return
    set_setting('currency', code)
    if manual:
        set_setting('currency_manual_set', 'true')


def is_currency_manual() -> bool:
    return get_setting('currency_manual_set', 'false') == 'true'


def sync_currency_with_lang(lang: str):
    """Автосинхронизация валюты с языком (если не менялась вручную)."""
    if is_currency_manual():
        return
    target = get_currency_for_lang(lang)
    current = get_currency()
    if current != target:
        set_setting('currency', target)
        logger.info(f"[Settings] Автосмена валюты: {current} → {target} (язык: {lang})")


def get_currency_symbol() -> str:
    return CURRENCIES.get(get_currency(), {}).get('symbol', '₽')


def get_all_currencies() -> dict:
    return CURRENCIES
