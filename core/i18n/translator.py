"""
Переводчик строк.
Функция t(key, lang) — возвращает строку из ru.json / en.json / he.json.
"""
import json
from pathlib import Path
from loguru import logger

_LOCALES_DIR = Path(__file__).parent

# Кэш загруженных переводов {lang: {key: value}}
_translations: dict = {}

SUPPORTED_LANGS = ['ru', 'he', 'en']
DEFAULT_LANG = 'ru'


def _load_lang(lang: str) -> dict:
    """Загружает переводы для языка."""
    if lang in _translations:
        return _translations[lang]

    file = _LOCALES_DIR / f"{lang}.json"
    if not file.exists():
        logger.warning(f"[i18n] Нет файла переводов: {file}")
        _translations[lang] = {}
        return {}

    try:
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
        _translations[lang] = data
        return data
    except Exception as e:
        logger.error(f"[i18n] Ошибка загрузки {file}: {e}")
        _translations[lang] = {}
        return {}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """
    Возвращает перевод строки.

    Пример:
        t("welcome", "ru") → "Привет!"
        t("welcome", "en") → "Hello!"
        t("booking_ask_name", "ru", name="Иван") → "Привет, Иван!"
    """
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG

    translations = _load_lang(lang)

    # Ищем ключ
    value = translations.get(key)

    # Fallback на русский
    if value is None and lang != DEFAULT_LANG:
        value = _load_lang(DEFAULT_LANG).get(key)

    # Если ключ не найден — возвращаем сам ключ
    if value is None:
        logger.warning(f"[i18n] Ключ не найден: '{key}' (lang={lang})")
        return key

    # Подставляем переменные
    if kwargs:
        try:
            value = value.format(**kwargs)
        except Exception as e:
            logger.error(f"[i18n] Ошибка форматирования '{key}': {e}")

    return value


def reload_translations() -> None:
    """Сбрасывает кэш переводов — для разработки."""
    global _translations
    _translations = {}
